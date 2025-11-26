"""
Laser Worker - Quản lý kết nối TCP tới bộ điều khiển laser
"""
import socket
import time
from typing import Optional

from utils.Logging import getLogger


log = getLogger()


class LaserWorker:
    """Worker phụ trách giao tiếp laser controller qua TCP socket."""

    def __init__(self, ip: str, port: int, timeout_ms: int = 3000):
        self.ip = ip
        self.port = port
        self.timeout_ms = timeout_ms

        self._socket: Optional[socket.socket] = None
        self.is_connected = False

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def connect(self, ip: Optional[str] = None, port: Optional[int] = None):
        """Kết nối tới laser controller"""
        target_ip = ip or self.ip
        target_port = port or self.port

        # Đóng kết nối cũ nếu tồn tại
        self.disconnect()

        log.info(f"Connecting to laser controller {target_ip}:{target_port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout_ms / 1000)
        sock.connect((target_ip, target_port))
        sock.setblocking(False)  # Non-blocking theo yêu cầu tài liệu

        self._socket = sock
        self.is_connected = True
        self.ip = target_ip
        self.port = target_port

        log.info("Laser socket connected (non-blocking)")
        return True

    def disconnect(self):
        """Ngắt kết nối laser"""
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
        self._socket = None
        self.is_connected = False

    # ------------------------------------------------------------------
    # Command helpers
    # ------------------------------------------------------------------
    def send_ga(self, script: str, timeout_ms: Optional[int] = None):
        """Gửi lệnh GA,<script>"""
        return self.send_raw_command(f"GA,{script}", expect_keyword="GA,0", timeout_ms=timeout_ms)

    def send_c2(self, script: str, block: str, content: str, timeout_ms: Optional[int] = None):
        """Gửi lệnh C2,<script>,<block>,<content>"""
        command = f"C2,{script},{block},{content}"
        return self.send_raw_command(command, expect_keyword="C2,0", timeout_ms=timeout_ms)

    def send_nt(self, timeout_ms: Optional[int] = None):
        """Gửi lệnh NT"""
        return self.send_raw_command("NT", expect_keyword="NT,0", timeout_ms=timeout_ms)

    def send_raw_command(
        self,
        command: str,
        expect_keyword: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ):
        """Gửi lệnh ASCII bất kỳ tới laser"""
        if not self.is_connected or not self._socket:
            raise RuntimeError("Laser controller is not connected")

        payload = command if command.endswith("\r\n") else f"{command}\r\n"
        timeout_ms = timeout_ms or self.timeout_ms

        log.info(f"Sending command to laser: {payload.strip()}")
        self._send_all(payload.encode("ascii"))

        response = self._read_response(timeout_ms)
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
    def _send_all(self, data: bytes):
        """Gửi toàn bộ bytes qua socket non-blocking"""
        total_sent = 0
        deadline = time.time() + (self.timeout_ms / 1000)

        while total_sent < len(data):
            try:
                sent = self._socket.send(data[total_sent:])  # type: ignore[arg-type]
                if sent == 0:
                    raise RuntimeError("Socket connection broken while sending data")
                total_sent += sent
            except BlockingIOError:
                if time.time() > deadline:
                    raise TimeoutError("Timeout while sending data to laser")
                time.sleep(0.01)  # Đợi 10ms rồi gửi tiếp

    def _read_response(self, timeout_ms: int) -> str:
        """
        Đọc response (nếu có) trong khoảng thời gian cho phép

        Returns:
            str: Response string (có thể rỗng nếu không nhận được gì)
        """
        deadline = time.time() + (timeout_ms / 1000)
        chunks = []

        while time.time() < deadline:
            try:
                data = self._socket.recv(1024)  # type: ignore[arg-type]
                if data:
                    chunks.append(data)

                    # Nếu response kết thúc bằng newline, dừng lại
                    if data.endswith(b"\n"):
                        break
                else:
                    break
            except BlockingIOError:
                time.sleep(0.01)

        if not chunks:
            return ""

        return b"".join(chunks).decode("ascii", errors="ignore").strip()

