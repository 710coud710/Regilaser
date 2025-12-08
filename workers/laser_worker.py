"""
Laser Worker - Quản lý kết nối laser controller (TCP hoặc RS232)
"""
import socket
import time
from typing import Optional

import serial
from serial import SerialException

from utils.Logging import getLogger
from utils.schema import LaserConnectMode


log = getLogger()


class LaserWorker:
    """Worker phụ trách giao tiếp laser controller (TCP socket hoặc COM)."""

    def __init__(
        self,
        mode: LaserConnectMode,
        ip: str,
        port: int,
        timeout_ms: int = 3000,
        com_port: Optional[str] = None,
        baudrate: Optional[int] = 9600,
    ):
        self.mode = mode if isinstance(mode, LaserConnectMode) else LaserConnectMode(mode)
        self.ip = ip
        self.port = port
        self.timeout_ms = timeout_ms
        self.com_port = com_port
        self.baudrate = baudrate or 9600

        self._socket: Optional[socket.socket] = None
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def connect(
        self,
        ip: Optional[str] = None,
        port: Optional[int] = None,
        com_port: Optional[str] = None,
        baudrate: Optional[int] = None,
    ):
        """Kết nối tới laser controller"""
        self.disconnect()

        if self.mode == LaserConnectMode.TCP:
            target_ip = ip or self.ip
            target_port = port or self.port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout_ms / 1000)
            sock.connect((target_ip, target_port))
            sock.setblocking(False)

            self._socket = sock
            self.ip = target_ip
            self.port = target_port
            self.is_connected = True
            log.info("Laser TCP socket connected (non-blocking)")
        else:
            target_port = com_port or self.com_port
            target_baud = baudrate or self.baudrate
            if not target_port:
                raise RuntimeError("Laser COM port is not configured")

            try:
                ser = serial.Serial(
                    port=target_port,
                    baudrate=target_baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=self.timeout_ms / 1000,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False,
                )
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                self.serial_port = ser
                self.com_port = target_port
                self.baudrate = target_baud
                self.is_connected = True
                log.info(f"Laser connected: {target_port} baudrate: {target_baud}bps")
            except SerialException as exc:
                self.serial_port = None
                self.is_connected = False
                raise RuntimeError(f"Cannot open laser COM port {target_port}: {exc}") from exc

        return True

    def disconnect(self):
        """Ngắt kết nối laser"""
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

        if self.serial_port:
            try:
                self.serial_port.close()
            except SerialException:
                pass
            self.serial_port = None

        self.is_connected = False

    # ------------------------------------------------------------------
    # Command helpers
    # ------------------------------------------------------------------
    def send_ga(self, script: str, timeout_ms: Optional[int] = None):
        """Gửi lệnh GA,<script>"""
        try:
            self._ensure_connection()
            return self.sendRawCommand(f"GA,{script}", expect_keyword="GA,0", timeout_ms=timeout_ms)
        except Exception as exc:
            log.error(f"Error: {exc}")
            raise

    def send_c2(self, script: str, content: str, timeout_ms: Optional[int] = None):
        """Gửi lệnh C2,<script>,<block>,<content>"""
        try:
            self._ensure_connection()
            command = f"C2,{script},{content}"
            return self.sendRawCommand(command, expect_keyword="C2,0", timeout_ms=timeout_ms)
        except Exception as exc:
            log.error(f"Error: {exc}")
            raise

    def send_nt(self, timeout_ms: Optional[int] = None):
        """Gửi lệnh NT"""
        try:        
            self._ensure_connection()
            return self.sendRawCommand("NT", expect_keyword="NT,0", timeout_ms=timeout_ms)
        except Exception as exc:
            log.error(f"Error: {exc}")
            raise


    def sendRawCommand(
        self,
        command: str,
        expect_keyword: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ):
        """Gửi lệnh ASCII bất kỳ tới laser"""
        self._ensure_connection()
        payload = command if command.endswith("\r\n") else f"{command}\r\n"
        timeout_ms = timeout_ms or self.timeout_ms

        log.info(f"Sending command to laser: {payload.strip()}")
        if self.mode == LaserConnectMode.TCP:
            response = self._send_tcp_command(payload, timeout_ms)
        else:
            response = self._send_serial_command(payload, timeout_ms)

        if response:
            log.info(f"Laser response: {response}")
        else:
            log.warning("Laser returned empty response")
        if expect_keyword and response and expect_keyword not in response:
            raise RuntimeError(
                f"Unexpected response for '{command.strip()}': '{response}' "
                f"(expect '{expect_keyword}')"
            )
        return response

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _ensure_connection(self):
        if not self.is_connected:
            raise RuntimeError("Laser controller is not connected")

    def _send_tcp_command(self, payload: str, timeout_ms: int) -> str:
        if not self._socket:
            raise RuntimeError("TCP socket is not available")
        data = payload.encode("ascii")
        total_sent = 0
        deadline = time.time() + (self.timeout_ms / 1000)

        while total_sent < len(data):
            try:
                sent = self._socket.send(data[total_sent:]) 
                if sent == 0:
                    raise RuntimeError("Socket connection broken while sending data")
                total_sent += sent
            except BlockingIOError:
                if time.time() > deadline:
                    self.is_connected = False
                    raise TimeoutError("Timeout while sending data to laser")
                time.sleep(0.01)
            except OSError as exc:
                self.is_connected = False
                raise RuntimeError(f"Socket error while sending: {exc}") from exc

        return self._read_response_tcp(timeout_ms)

    def _send_serial_command(self, payload: str, timeout_ms: int) -> str:
        if not self.serial_port or not self.serial_port.is_open:
            self.is_connected = False
            raise RuntimeError("Serial port is not available")
    
        try:
            self.serial_port.write(payload.encode("ascii"))
            self.serial_port.flush()
        except SerialException as exc:
            self.is_connected = False
            raise RuntimeError(f"Serial write error: {exc}") from exc

        return self._read_response_serial(timeout_ms)

    def _read_response_tcp(self, timeout_ms: int) -> str:
        deadline = time.time() + (timeout_ms / 1000)
        chunks = []
        while time.time() < deadline:
            try:
                data = self._socket.recv(1024)  # type: ignore[arg-type]
                if data:
                    chunks.append(data)
                    if data.endswith(b"\n"):
                        break
                else:
                    break
            except BlockingIOError:
                time.sleep(0.01)
            except OSError as exc:
                self.is_connected = False
                raise RuntimeError(f"Socket error while receiving: {exc}") from exc

        if not chunks:
            return ""

        return b"".join(chunks).decode("ascii", errors="ignore").strip()

    def _read_response_serial(self, timeout_ms: int) -> str:
        deadline = time.time() + (timeout_ms / 1000)
        buffer = bytearray()

        while time.time() < deadline:
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        buffer.extend(data)
                        break
                        # Nếu nhận dữ liệu kết thúc bằng new line (\r\n)
                        # if buffer.endswith(b"\n") or buffer.endswith(b"\r\n"):
                        #     break
                else:
                    time.sleep(0.01)
            except SerialException as exc:
                self.is_connected = False
                raise RuntimeError(f"Serial read error: {exc}") from exc

        if not buffer:
            return ""

        return buffer.decode("ascii", errors="ignore").strip()

    def checkConnectionAlive(self) -> bool:
        """Kiểm tra nhanh trạng thái kết nối"""
        if self.mode == LaserConnectMode.TCP:
            if not self._socket:
                return False
            try:
                self._socket.getpeername()
                return True
            except OSError:
                return False
        return bool(self.serial_port and self.serial_port.is_open)

