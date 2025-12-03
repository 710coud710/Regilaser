"""
PLC Worker - Giao tiếp PLC qua serial (COM port)
"""
import time
import serial
from serial import SerialException

from PySide6.QtCore import QObject, Signal, Slot
from utils.Logging import getLogger


log = getLogger()


class PLCWorker(QObject):
    """Serial worker cho PLC"""
    logMessage = Signal(str, str)  # (message, level) = (message, INFO/WARNING/ERROR)
    data_received = Signal(str)
    error_occurred = Signal(str)
    connectionStatusChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.port_name = "COM3"
        self.baudrate = 9600
        self.timeout = 1.0

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    @Slot(str, int)
    @Slot(str)
    @Slot()
    def connect(self, port_name=None, baudrate=None):
        try:
            if port_name:
                self.port_name = port_name
            if baudrate:
                self.baudrate = baudrate

            log.info(f"[PLC] Connecting {self.port_name} baudrate: {self.baudrate}")

            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

            self.serial_port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            self.is_connected = True
            log.info("[PLC] Connected")
            self.connectionStatusChanged.emit(True)
            return True
        except SerialException as exc:
            log.error(f"[PLC] Serial error: {exc}")
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            self.error_occurred.emit(str(exc))
            return False

    @Slot()
    def disconnect(self):
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = None
            self.is_connected = False
            log.info("[PLC] Disconnected")
            self.connectionStatusChanged.emit(False)
            return True
        except SerialException as exc:
            log.error(f"[PLC] Disconnect error: {exc}")
            self.error_occurred.emit(str(exc))
            return False

    # ------------------------------------------------------------------
    # Command helpers
    # ------------------------------------------------------------------
    def _ensure_connection(self) -> bool:
        if not self.is_connected or not self.serial_port:
            error_msg = "Not connected to PLC"
            log.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        return True

    @Slot(str)
    def sendData_PLC(self, data):
        try:
            if not self._ensure_connection():
                return False
            payload = data if data.endswith("\r\n") else f"{data}\r\n"
            log.info(f"[PLC] Sent: {payload.strip()}")
            bytes_written = self.serial_port.write(payload.encode('ascii'))
            self.serial_port.flush()
            log.info(f"[PLC] Data sent successfully: {bytes_written} bytes")
            return True
        except Exception as exc:
            log.error(f"[PLC] Send command error: {exc}")
            self.error_occurred.emit(str(exc))
            return False
        
    def readData_PLC(self, timeout_ms=10000):
        try:
            if not self.is_connected or not self.serial_port:
                error_msg = "Not connected to PLC"
                log.error(error_msg)
                self.error_occurred.emit(error_msg)
                return None

            start_time = time.time()
            timeout_sec = timeout_ms / 1000.0
            data_bytes = b''
            no_data_count = 0
            max_no_data_count = 10 
            
            log.info("Waiting for data...")
            
            while time.time() - start_time < timeout_sec:
                if self.serial_port.in_waiting > 0:
                    # Có dữ liệu, đọc tất cả
                    chunk = self.serial_port.read(self.serial_port.in_waiting)
                    data_bytes += chunk
                    no_data_count = 0  # Reset counter
                    log.debug(f"Received {len(chunk)} bytes, total: {len(data_bytes)}")
                else:
                    # Không có dữ liệu
                    no_data_count += 1
                    if len(data_bytes) > 0 and no_data_count >= max_no_data_count:
                        # Đã có dữ liệu và không còn dữ liệu mới trong 100ms → dừng
                        log.info(f"No more data after {max_no_data_count * 10}ms, stopping read")
                        break
                    time.sleep(0.01)  # Chờ 10ms
            
            # Kiểm tra dữ liệu
            if not data_bytes:
                error_msg = "Timeout: No data received"
                log.error(f"{error_msg}")
                self.error_occurred.emit(error_msg)
                return None
            
            # Chuyển bytes sang text string (ASCII decoding)
            data_str = data_bytes.decode('ascii', errors='ignore')
            log.info(f"[PLC] Data received: {data_str}")
            self.data_received.emit(data_str)
            return data_str
                
        except UnicodeDecodeError as e:
            error_msg = f"ASCII decoding error: {str(e)} - Data contains non-ASCII bytes"
            log.error(f"[PLC] {error_msg}")
            self.error_occurred.emit(error_msg)
            return None
            
        except serial.SerialException as e:
            error_msg = f"Serial port error: {str(e)}"
            log.error(f"[PLC] {error_msg}")
            self.error_occurred.emit(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Read data error: {str(e)}"
            log.error(f"[PLC] {error_msg}")
            log.debug("Exception details:", exc_info=True)
            self.error_occurred.emit(error_msg)
            return None

    # ------------------------------------------------------------------
    # Connection health check (dùng cho auto-reconnect)
    # ------------------------------------------------------------------
    def checkConnectionAlive(self) -> bool:
        """Kiểm tra kết nối serial còn mở không."""
        return bool(self.serial_port and self.serial_port.is_open)

