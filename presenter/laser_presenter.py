"""
Laser Presenter - Xử lý logic giao tiếp Laser Marking System
"""
from presenter.base_presenter import BasePresenter
from config import ConfigManager
from workers.laser_worker import LaserWorker
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()

class LaserPresenter(BasePresenter):
    """Presenter xử lý Laser Marking communication (TCP)"""

    def __init__(self):
        super().__init__()
        config = ConfigManager().get()
        self.laser_ip = config.LASER_IP
        self.laser_port = config.LASER_PORT
        self.default_script = str(config.LASER_SCRIPT)
        self.command_timeout_ms = config.LASER_TIMEOUT_MS

        self.worker = LaserWorker(self.laser_ip, self.laser_port, self.command_timeout_ms)
        self.is_connected = False
        log.info("LaserPresenter initialized successfully")
    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def connect(self, ip_address=None, port=None):
        """Kết nối đến Laser System"""
        target_ip = ip_address or self.laser_ip
        target_port = port or self.laser_port

        self.show_info(f"Connecting to Laser Controller: {target_ip}:{target_port}")
        log.info(f"Connecting to Laser Controller: {target_ip}:{target_port}")
        try:
            self.worker.connect(target_ip, target_port)
            self.is_connected = True
            self.show_success("Laser controller connected successfully")
            log.success("Laser controller connected successfully")
            return True
        except Exception as exc:
            self.is_connected = False
            self.show_error(f"Failed to connect to laser: {exc}")
            log.error(f"Failed to connect to laser: {exc}")
            return False

    def disconnect(self):
        """Ngắt kết nối Laser System"""
        if not self.is_connected:
            return

        self.worker.disconnect()
        self.is_connected = False
        self.show_info("Disconnected from laser controller")
        log.infor("Disconnected from laser controller")

    # ------------------------------------------------------------------
    # GA / C2 / NT helpers
    # ------------------------------------------------------------------
    def activate_script(self, script_number=None):
        """Gửi lệnh GA để chọn script"""
        if not self._ensure_connection():
            return False

        script = str(script_number or self.default_script)
        self.show_info(f"Send GA command with script {script}")
        log.info(f"Send GA command with script {script}")
        try:
            self.worker.send_ga(script, timeout_ms=self.command_timeout_ms)
            self.show_success("GA command completed")
            log.success("GA command completed")
            return True
        except Exception as exc:
            self.show_error(f"GA command error: {exc}")
            log.error(f"GA command error: {exc}")
            return False

    def set_content(self, script=None, block="2", content=""):
        """Gửi lệnh C2 để nạp dữ liệu vào block"""
        if not self._ensure_connection():
            return False

        script_id = str(script or self.default_script)
        self.show_info(f"Send C2 command (script={script_id}, block={block})")
        log.info(f"Send C2 command (script={script_id}, block={block})")
        try:
            self.worker.send_c2(script_id, block, content, timeout_ms=self.command_timeout_ms)
            self.show_success("C2 command completed")
            log.success("C2 command completed")
            return True
        except Exception as exc:
            self.show_error(f"C2 command error: {exc}")
            log.error(f"C2 command error: {exc}")
            return False

    def start_marking(self):
        """Gửi lệnh NT để bắt đầu khắc"""
        if not self._ensure_connection():
            return False

        self.show_info("Gửi NT command (start marking)")
        try:
            self.worker.send_nt(timeout_ms=self.command_timeout_ms)
            self.show_success("NT command completed")
            log.success("NT command completed")
            return True
        except Exception as exc:
            self.show_error(f"NT command error: {exc}")
            log.error(f"NT command error: {exc}")
            return False

    # ------------------------------------------------------------------
    # High-level flows
    # ------------------------------------------------------------------
    def mark_psn(self, security_code, script=None):
        """
        Thực hiện laser marking với flow GA -> C2 -> NT

        Args:
            security_code (str): chuỗi Security Code cần nạp
            script (str|None): script override, None = lấy từ config
        """
        if not security_code:
            self.show_error("Security code is not valid")
            log.error("Security code is not valid")
            return False

        script_id = script or self.default_script

        self.show_info("=== START LASER MARKING ===")
        log.info("=== START LASER MARKING ===")
        self.show_debug(f"Script={script_id}, SecurityCode={security_code}")

        if not self.activate_script(script_id):
            return False

        if not self.set_content(script_id, "2", security_code):
            return False

        if not self.start_marking():
            return False

        self.show_success("Laser marking hoàn tất")
        return True

    def send_custom_command(self, command, expect_keyword=None):
        if not self._ensure_connection():
            return False

        self.show_info(f"Send custom command Manual: {command.strip()}")
        log.info(f"Send custom command Manual: {command.strip()}")
        try:
            response = self.worker.send_raw_command(
                command,
                expect_keyword=expect_keyword,
                timeout_ms=self.command_timeout_ms,
            )
            self.show_success(f"Laser response: {response or '(empty)'}")
            log.success(f"Laser response: {response or '(empty)'}")
            return True
        except Exception as exc:
            self.show_error(f"Custom command error: {exc}")
            log.error(f"Custom command error: {exc}")
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_connection(self):
        if self.is_connected:
            return True
        return self.connect(self.laser_ip, self.laser_port)

    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        self.disconnect()
