import serial
import time
from PySide6.QtCore import QObject, Signal, QThread, Slot
from utils.Logging import getLogger

log = getLogger()


class SFISWorker(QObject):
    # Signals
    data_received = Signal(str)  # Dữ liệu nhận được từ SFIS (text ASCII)
    error_occurred = Signal(str)  # Lỗi xảy ra
    connectionStatusChanged = Signal(bool)  # Trạng thái kết nối
    signal_sent = Signal(bool, str)  # (success, message) - Tín hiệu đã gửi
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        
        # Cấu hình COM port mặc định
        self.port_name = "COM2"
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 5.0
        
        log.info("SFISWorker initialized")
    
    @Slot(str, int)
    @Slot(str)
    @Slot()
    def connect(self, port_name=None, baudrate=None):
        """Kết nối đến SFIS qua COM port"""
        try:
            if port_name:
                self.port_name = port_name
            if baudrate:
                self.baudrate = baudrate
            
            log.info(f"Connecting to {self.port_name}...")
            log.info(f"Config: baudrate={self.baudrate}, bytesize=8, parity=N, stopbits=1")
            
            # Close existing connection if any
            if self.serial_port and self.serial_port.is_open:
                log.info("Closing existing connection...")
                self.serial_port.close()
            
            # Mở kết nối mới với PySerial
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                xonxoff=False,  # No software flow control
                rtscts=False,   # No hardware (RTS/CTS) flow control
                dsrdtr=False    # No hardware (DSR/DTR) flow control
            )
            
            # Xóa buffer cũ
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.is_connected = True
            log.info(f"Connected successfully to {self.port_name}")
            self.connectionStatusChanged.emit(True)
            return True
            
        except serial.SerialException as e:
            self.is_connected = False
            error_msg = f"Serial port error: {str(e)}"
            log.error(f"{error_msg}")
            self.connectionStatusChanged.emit(False)
            self.error_occurred.emit(error_msg)
            return False
            
        except Exception as e:
            self.is_connected = False
            error_msg = f"Connection error: {str(e)}"
            log.error(f"{error_msg}")
            log.debug("Exception details:", exc_info=True)
            self.connectionStatusChanged.emit(False)
            self.error_occurred.emit(error_msg)
            return False
    
    @Slot()
    def disconnect(self):
        """
        Ngắt kết nối SFIS
        
        Returns:
            bool: True nếu ngắt kết nối thành công
        """
        try:
            log.info(f"Disconnecting from {self.port_name}...")
            
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                log.info(f"✓ Disconnected from {self.port_name}")
            
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            return True
            
        except Exception as e:
            error_msg = f"Disconnect error: {str(e)}"
            log.error(f"✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False
    
    def send_data(self, data):
        """Gửi dữ liệu text ASCII đến SFIS qua COM port"""
        try:
            # Check connection
            if not self.is_connected or not self.serial_port:
                error_msg = "Not connected to SFIS"
                log.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False
            
            # Log chi tiết trước khi gửi
            log.info("=" * 70)
            log.info("Sending data to SFIS...")
            log.info(f"Port: {self.port_name}")
            log.info(f"Data length: {len(data)} bytes")
            log.info(f"Data (text): {data}")
            log.info(f"Data (HEX): {data.encode('ascii').hex()}")
            
            # Chuyển text string sang bytes (ASCII encoding)
            data_bytes = data.encode('ascii')
            
            # Gửi qua COM port
            bytes_written = self.serial_port.write(data_bytes)
            self.serial_port.flush()  # Đảm bảo dữ liệu được gửi ngay
            
            log.info(f"✓ Data sent successfully")
            log.info(f"  Bytes written: {bytes_written}/{len(data_bytes)}")
            log.info("=" * 70)
            
            return True
            
        except UnicodeEncodeError as e:
            error_msg = f"ASCII encoding error: {str(e)} - Data contains non-ASCII characters"
            log.error(f"✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False
            
        except serial.SerialException as e:
            error_msg = f"Serial port error: {str(e)}"
            log.error(f"✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Send data error: {str(e)}"
            log.error(f"✗ {error_msg}")
            log.debug("Exception details:", exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
    
    @Slot(str)
    def send_start_signal(self, start_message):
        """Gửi tín hiệu START text đến SFIS (fire and forget - không chờ phản hồi)
        Slot method để được gọi từ QMetaObject.invokeMethod trong thread"""
        log.info("=" * 70)
        log.info("send_start_signal() called")
        log.info(f"Message: {start_message}")
        log.info(f"Length: {len(start_message)} bytes")
        log.info("=" * 70)
        
        try:
            # Gửi dữ liệu text qua COM port
            success = self.send_data(start_message)
            
            if success:
                log.info("✓ START signal sent successfully")
                self.signal_sent.emit(True, "START signal sent successfully")
            else:
                log.error("✗ Failed to send START signal")
                self.signal_sent.emit(False, "Failed to send START signal")
                
        except Exception as e:
            error_msg = f"Exception in send_start_signal: {str(e)}"
            log.error(f"✗ {error_msg}")
            log.debug("Exception details:", exc_info=True)
            self.signal_sent.emit(False, error_msg)
    
    def read_data(self, expected_length=None, timeout_ms=5000):
        """Đọc dữ liệu text ASCII từ SFIS qua COM port """
        try:
            # Check connection
            if not self.is_connected or not self.serial_port:
                error_msg = "Not connected to SFIS"
                log.error(error_msg)
                self.error_occurred.emit(error_msg)
                return None

            log.info("Reading data from SFIS via COM port...")
            log.info(f"Port: {self.port_name}")
            log.info(f"Expected length: {expected_length if expected_length else 'all available'} bytes")
            log.info(f"Timeout: {timeout_ms}ms")
            
            # Đợi dữ liệu
            start_time = time.time()
            timeout_sec = timeout_ms / 1000.0
            data_bytes = b''
            
            if expected_length:
                # Đọc số byte cố định
                log.info(f"Waiting for {expected_length} bytes...")
                
                while len(data_bytes) < expected_length:
                    # Kiểm tra timeout
                    if time.time() - start_time > timeout_sec:
                        error_msg = f"Timeout: Received {len(data_bytes)}/{expected_length} bytes"
                        log.error(f"{error_msg}")
                        self.error_occurred.emit(error_msg)
                        return None
                    
                    # Đọc dữ liệu nếu có
                    if self.serial_port.in_waiting > 0:
                        remaining = expected_length - len(data_bytes)
                        chunk = self.serial_port.read(remaining)
                        data_bytes += chunk
                        log.debug(f"Received {len(chunk)} bytes, total: {len(data_bytes)}/{expected_length}")
                    else:
                        time.sleep(0.01)  # Chờ 10ms trước khi check lại
            else:
                # Đọc tất cả dữ liệu có sẵn
                log.info("Waiting for data...")
                
                while time.time() - start_time < timeout_sec:
                    if self.serial_port.in_waiting > 0:
                        data_bytes = self.serial_port.read(self.serial_port.in_waiting)
                        log.debug(f"Received {len(data_bytes)} bytes")
                        break
                    time.sleep(0.01)
                else:
                    error_msg = "Timeout: No data received"
                    log.error(f"{error_msg}")
                    self.error_occurred.emit(error_msg)
                    return None
            
            # Check data
            if not data_bytes:
                log.warning("No data received")
                return None
            
            # Chuyển bytes sang text string (ASCII decoding)
            data_str = data_bytes.decode('ascii', errors='ignore').strip()
            # log.info(f"  Bytes received: {len(data_bytes)}")
            log.info(f"  Data received from SFIS: {data_str}")            
            # Emit signal
            self.data_received.emit(data_str)
            return data_str
                
        except UnicodeDecodeError as e:
            error_msg = f"ASCII decoding error: {str(e)} - Data contains non-ASCII bytes"
            log.error(f"✗ {error_msg}")
            log.error(f"  Raw bytes (HEX): {data_bytes.hex()}")
            self.error_occurred.emit(error_msg)
            return None
            
        except serial.SerialException as e:
            error_msg = f"Serial port error: {str(e)}"
            log.error(f"✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Read data error: {str(e)}"
            log.error(f"✗ {error_msg}")
            log.debug("Exception details:", exc_info=True)
            self.error_occurred.emit(error_msg)
            return None
    
    def send_and_wait(self, data, expected_length=None, timeout_ms=5000):
        """Gửi dữ liệu text và chờ phản hồi text từ SFIS"""
        log.info("Send and wait for response...")
        
        if self.send_data(data):
            return self.read_data(expected_length, timeout_ms)
        else:
            log.error("Failed to send data, skipping read")
            return None
    
    def clear_buffer(self):
        """Xóa buffer đọc/ghi của COM port"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                log.info("Buffer cleared")
                return True
            else:
                log.warning("Cannot clear buffer: Port not open")
                return False
        except Exception as e:
            error_msg = f"Clear buffer error: {str(e)}"
            log.error(f"✗ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False
    
    def is_port_available(self, port_name):
        """Kiểm tra COM port có khả dụng """
        try:
            test_port = serial.Serial(port_name)
            test_port.close()
            log.info(f"Port {port_name} is available")
            return True
        except:
            log.warning(f"Port {port_name} is not available")
            return False
    
    @staticmethod
    def list_available_ports():
        """Liệt kê các COM port khả dụng trên hệ thống"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        log.info(f"Available ports: {port_list}")
        return port_list
    
    def get_port_info(self):
        """Lấy thông tin cấu hình COM port hiện tại"""
        return {
            'port_name': self.port_name,
            'baudrate': self.baudrate,
            'bytesize': self.bytesize,
            'parity': self.parity,
            'stopbits': self.stopbits,
            'timeout': self.timeout,
            'is_connected': self.is_connected
        }

