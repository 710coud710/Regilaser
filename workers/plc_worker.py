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
    def _ensure_connection(self):
        if not self.is_connected or not self.serial_port:
            raise RuntimeError("PLC is not connected")

    @Slot(str)
    def send_command(self, command):
        """Gửi command ASCII (auto append CRLF)"""
        try:
            self._ensure_connection()
            payload = command if command.endswith("\r\n") else f"{command}\r\n"
            self.serial_port.write(payload.encode("ascii"))
            self.serial_port.flush()
            log.info(f"[PLC] Sent command: {command}")
            return True
        except Exception as exc:
            log.error(f"[PLC] Send command error: {exc}")
            self.error_occurred.emit(str(exc))
            return False

    @Slot(str, int)
    def wait_for_signal(self, expected_signal, timeout_ms=3000):
        """
        Chờ chuỗi phản hồi chứa expected_signal
        """
        try:
            self._ensure_connection()
            end_time = time.time() + (timeout_ms / 1000)
            buffer = ""

            while time.time() < end_time:
                line = self.serial_port.readline().decode("ascii", errors="ignore").strip()
                if line:
                    log.info(f"[PLC] Received: {line}")
                    buffer += line
                    self.data_received.emit(line)
                    if expected_signal in line:
                        return line
            self.error_occurred.emit(f"Timeout waiting for PLC signal: {expected_signal}")
            return ""
        except Exception as exc:
            log.error(f"[PLC] Wait signal error: {exc}")
            self.error_occurred.emit(str(exc))
            return ""

