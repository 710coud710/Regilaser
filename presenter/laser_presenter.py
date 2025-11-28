"""
Laser Presenter - Xử lý logic giao tiếp Laser Marking System
"""
from PySide6.QtCore import QTimer, Signal
from presenter.base_presenter import BasePresenter
from config import ConfigManager
from workers.laser_worker import LaserWorker
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()

class LaserPresenter(BasePresenter):
    """Presenter xử lý Laser Marking communication (TCP)"""
    
    # Signal để thông báo trạng thái kết nối thay đổi
    connectionStatusChanged = Signal(bool)  # (is_connected)

    def __init__(self):
        super().__init__()
        config = ConfigManager().get()
        self.laser_ip = config.LASER_IP
        self.laser_port = config.LASER_PORT
        self.default_script = str(config.LASER_SCRIPT)
        self.command_timeout_ms = config.LASER_TIMEOUT_MS

        self.worker = LaserWorker(self.laser_ip, self.laser_port, self.command_timeout_ms)
        self.is_connected = False
        
        # Auto-reconnect timer (check mỗi 5 giây)
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._check_and_reconnect)
        self.reconnect_interval_ms = 5000  # 5 giây
        self.auto_reconnect_enabled = True
        
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
            self.connectionStatusChanged.emit(True)
            self.show_success("Laser controller connected successfully")
            log.info("Laser controller connected successfully")
            return True
        except Exception as exc:
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            self.show_error(f"Failed to connect to laser: {exc}")
            log.error(f"Failed to connect to laser: {exc}")
            return False

    def disconnect(self):
        """Ngắt kết nối Laser System"""
        self.auto_reconnect_enabled = False
        self.reconnect_timer.stop()
        
        if not self.is_connected:
            return

        self.worker.disconnect()
        self.is_connected = False
        self.connectionStatusChanged.emit(False)
        self.show_info("Disconnected from laser controller")
        log.info("Disconnected from laser controller")

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
            log.info("GA command completed")
            return True
        except (RuntimeError, TimeoutError, OSError) as exc:
            # Phát hiện mất kết nối khi gửi lệnh thất bại
            self._handle_connection_lost()
            self.show_error(f"GA command error: {exc}")
            log.error(f"GA command error: {exc}")
            return False
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
            log.info("C2 command completed")
            return True
        except (RuntimeError, TimeoutError, OSError) as exc:
            # Phát hiện mất kết nối khi gửi lệnh thất bại
            self._handle_connection_lost()
            self.show_error(f"C2 command error: {exc}")
            log.error(f"C2 command error: {exc}")
            return False
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
            log.info("NT command completed")
            return True
        except (RuntimeError, TimeoutError, OSError) as exc:
            # Phát hiện mất kết nối khi gửi lệnh thất bại
            self._handle_connection_lost()
            self.show_error(f"NT command error: {exc}")
            log.error(f"NT command error: {exc}")
            return False
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

        self.show_success("Laser marking completed")
        log.success("Laser marking completed")
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
            log.info(f"Laser response: {response or '(empty)'}")
            return True
        except (RuntimeError, TimeoutError, OSError) as exc:
            # Phát hiện mất kết nối khi gửi lệnh thất bại
            self._handle_connection_lost()
            self.show_error(f"Custom command error: {exc}")
            log.error(f"Custom command error: {exc}")
            return False
        except Exception as exc:
            self.show_error(f"Custom command error: {exc}")
            log.error(f"Custom command error: {exc}")
            return False

    def sendGAtoLaser(self, Script):
        """Gửi lệnh GA,05"""
        try:
            return self.worker.send_ga(Script)
        except Exception as e:
            log.error(f"Failed to send GA,{Script} to laser: {e}")
            raise Exception(f"Failed to send GA,{Script} to laser: {e}")
           
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_connection(self):
        if self.is_connected:
            # Kiểm tra xem connection còn valid không
            if not self.worker.is_connected:
                self._handle_connection_lost()
                return False
            return True
        return self.connect(self.laser_ip, self.laser_port)
    
    def _handle_connection_lost(self):
        """Xử lý khi phát hiện mất kết nối - cập nhật UI ngay lập tức"""
        if self.is_connected:
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            log.warning("Laser connection lost - updating UI immediately")
            self.show_warning("Laser connection lost")

    def start_auto_connect(self):
        """Bắt đầu tự động kết nối và duy trì kết nối"""
        self.auto_reconnect_enabled = True
        log.info("Starting auto-connect for laser controller...")
        self.show_info("Auto-connecting to laser controller...")
        
        # Thử kết nối ngay lập tức
        self._try_connect()
        
        # Bắt đầu timer để check và reconnect định kỳ
        self.reconnect_timer.start(self.reconnect_interval_ms)
        log.info(f"Auto-reconnect timer started (interval: {self.reconnect_interval_ms}ms)")

    def stop_auto_connect(self):
        """Dừng tự động kết nối"""
        self.auto_reconnect_enabled = False
        self.reconnect_timer.stop()
        log.info("Auto-reconnect stopped")

    def _try_connect(self):
        """Thử kết nối đến laser (không log nhiều để tránh spam)"""
        if not self.auto_reconnect_enabled:
            return
        
        try:
            if not self.is_connected:
                self.worker.connect(self.laser_ip, self.laser_port)
                self.is_connected = True
                self.connectionStatusChanged.emit(True)
                log.info(f"Laser auto-connected: {self.laser_ip}:{self.laser_port}")
        except Exception as exc:
            # Chỉ log khi lần đầu fail hoặc khi reconnect thành công sau khi fail
            if self.is_connected:
                # Nếu trước đó đã connected nhưng bây giờ fail, có thể connection bị mất
                self.is_connected = False
                self.connectionStatusChanged.emit(False)
                log.warning(f"Laser connection lost: {exc}")
            # Không log mỗi lần fail để tránh spam log

    def _check_and_reconnect(self):
        """Kiểm tra và tự động kết nối lại nếu bị ngắt"""
        if not self.auto_reconnect_enabled:
            return
        
        # Đồng bộ trạng thái với worker
        worker_connected = self.worker.is_connected
        
        # Kiểm tra socket state nếu worker báo là connected
        if worker_connected and self.worker._socket:
            try:
                # Thử kiểm tra socket state
                self.worker._socket.getpeername()
            except (OSError, AttributeError):
                # Socket không còn valid
                log.warning("Laser socket invalid, marking as disconnected")
                self.worker.is_connected = False
                worker_connected = False
        
        # Nếu trạng thái không khớp, cập nhật ngay lập tức
        if self.is_connected != worker_connected:
            self.is_connected = worker_connected
            self.connectionStatusChanged.emit(worker_connected)
            if not worker_connected:
                log.warning("Laser connection lost detected, attempting to reconnect...")
                self.show_warning("Laser connection lost - reconnecting...")
        
        # Nếu chưa kết nối, thử kết nối lại
        if not self.is_connected:
            self._try_connect()

    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        self.stop_auto_connect()
        self.disconnect()
    