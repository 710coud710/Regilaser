"""
SFIS Worker - Xử lý giao tiếp COM port với SFIS (Shop Floor Information System)
"""
import serial
import time
from PySide6.QtCore import QObject, Signal, QThread


class SFISWorker(QObject):
    """Worker xử lý giao tiếp serial với SFIS"""
    
    # Signals
    data_received = Signal(str)  # Dữ liệu nhận được từ SFIS
    error_occurred = Signal(str)  # Lỗi xảy ra
    connection_status_changed = Signal(bool)  # Trạng thái kết nối
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.port_name = "COM2"
        self.baudrate = 9600
        self.timeout = 5.0
        
    def connect(self, port_name=None, baudrate=None):
        """Kết nối đến SFIS qua COM port"""
        try:
            if port_name:
                self.port_name = port_name
            if baudrate:
                self.baudrate = baudrate
                
            # Đóng kết nối cũ nếu có
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            # Mở kết nối mới
            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            self.is_connected = True
            self.connection_status_changed.emit(True)
            return True
            
        except Exception as e:
            self.is_connected = False
            self.connection_status_changed.emit(False)
            self.error_occurred.emit(f"Lỗi kết nối SFIS: {str(e)}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối SFIS"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.is_connected = False
            self.connection_status_changed.emit(False)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Lỗi ngắt kết nối: {str(e)}")
            return False
    
    def send_data(self, data):
        """
        Gửi dữ liệu đến SFIS
        
        Args:
            data (str): Dữ liệu cần gửi
            
        Returns:
            bool: True nếu gửi thành công
        """
        try:
            if not self.is_connected or not self.serial_port:
                self.error_occurred.emit("Chưa kết nối SFIS")
                return False
            
            # Chuyển string sang bytes và gửi
            data_bytes = data.encode('ascii')
            self.serial_port.write(data_bytes)
            self.serial_port.flush()
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Lỗi gửi dữ liệu: {str(e)}")
            return False
    
    def read_data(self, expected_length=None, timeout_ms=5000):
        """
        Đọc dữ liệu từ SFIS
        
        Args:
            expected_length (int): Độ dài dữ liệu mong đợi (None = đọc tất cả)
            timeout_ms (int): Thời gian timeout (ms)
            
        Returns:
            str: Dữ liệu nhận được, hoặc None nếu lỗi
        """
        try:
            if not self.is_connected or not self.serial_port:
                self.error_occurred.emit("Chưa kết nối SFIS")
                return None
            
            # Đợi dữ liệu
            start_time = time.time()
            timeout_sec = timeout_ms / 1000.0
            
            if expected_length:
                # Đọc số byte cố định
                data_bytes = b''
                while len(data_bytes) < expected_length:
                    if time.time() - start_time > timeout_sec:
                        self.error_occurred.emit("Timeout đọc dữ liệu SFIS")
                        return None
                    
                    if self.serial_port.in_waiting > 0:
                        remaining = expected_length - len(data_bytes)
                        chunk = self.serial_port.read(remaining)
                        data_bytes += chunk
                    else:
                        time.sleep(0.01)  # Chờ 10ms
            else:
                # Đọc tất cả dữ liệu có sẵn
                while time.time() - start_time < timeout_sec:
                    if self.serial_port.in_waiting > 0:
                        data_bytes = self.serial_port.read(self.serial_port.in_waiting)
                        break
                    time.sleep(0.01)
                else:
                    self.error_occurred.emit("Timeout đọc dữ liệu SFIS")
                    return None
            
            # Chuyển bytes sang string
            data_str = data_bytes.decode('ascii', errors='ignore').strip()
            
            if data_str:
                self.data_received.emit(data_str)
                return data_str
            else:
                return None
                
        except Exception as e:
            self.error_occurred.emit(f"Lỗi đọc dữ liệu: {str(e)}")
            return None
    
    def send_and_wait(self, data, expected_length=None, timeout_ms=5000):
        """
        Gửi dữ liệu và chờ phản hồi
        
        Args:
            data (str): Dữ liệu gửi đi
            expected_length (int): Độ dài phản hồi mong đợi
            timeout_ms (int): Thời gian timeout (ms)
            
        Returns:
            str: Dữ liệu nhận được, hoặc None nếu lỗi
        """
        if self.send_data(data):
            return self.read_data(expected_length, timeout_ms)
        return None
    
    def clear_buffer(self):
        """Xóa buffer đọc/ghi"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                return True
        except Exception as e:
            self.error_occurred.emit(f"Lỗi xóa buffer: {str(e)}")
            return False
    
    def is_port_available(self, port_name):
        """Kiểm tra COM port có khả dụng không"""
        try:
            test_port = serial.Serial(port_name)
            test_port.close()
            return True
        except:
            return False
    
    @staticmethod
    def list_available_ports():
        """Liệt kê các COM port khả dụng"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

