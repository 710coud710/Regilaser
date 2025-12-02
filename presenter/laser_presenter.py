"""
Laser Presenter - Xử lý logic giao tiếp Laser Marking System
"""
from PySide6.QtCore import QTimer, Signal
from presenter.base_presenter import BasePresenter
from config import ConfigManager
from workers.laser_worker import LaserWorker
from utils.schema import LaserConnectMode
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()


class LaserPresenter(BasePresenter):
    connectionStatusChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        config = ConfigManager().get()
        self.laser_mode = config.LASER_MODE
        self.laser_ip = config.LASER_IP
        self.laser_port = config.LASER_PORT
        self.laser_com_port = getattr(config, "LASER_COM_PORT", None)
        self.laser_baudrate = getattr(config, "LASER_BAUDRATE", 9600)
        self.default_script = str(config.LASER_SCRIPT)
        self.command_timeout_ms = config.LASER_TIMEOUT_MS

        self.worker = LaserWorker(
            mode=self.laser_mode,
            ip=self.laser_ip,
            port=self.laser_port,
            timeout_ms=self.command_timeout_ms,
            com_port=self.laser_com_port,
            baudrate=self.laser_baudrate,
        )
        self.is_connected = False
        
        # Auto-reconnect timer (check mỗi 5 giây)
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._checkAndReconnect)
        self.reconnect_ms = 5000  # 5 giây
        self.auto_reconnect_enabled = True
        
        log.info("LaserPresenter initialized successfully")
    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def connect(self, ip_address=None, port=None, com_port=None, baudrate=None):
        """Kết nối đến Laser System"""
        description = ""
        try:
            if self.laser_mode == LaserConnectMode.TCP:
                target_ip = ip_address or self.laser_ip
                target_port = port or self.laser_port
                description = f"{target_ip}:{target_port}"
                self.show_info(f"Connecting to Laser Controller (TCP): {description}")
                log.info(f"Connecting to Laser Controller (TCP): {description}")
                self.worker.connect(target_ip, target_port)
            else:
                target_com = com_port or self.laser_com_port
                target_baud = baudrate or self.laser_baudrate
                if not target_com:
                    raise RuntimeError("Laser COM port is not configured")
                description = f"{target_com} @ {target_baud}bps"
                self.show_info(f"Connecting to Laser Controller (RS232): {description}")
                log.info(f"Connecting to Laser Controller (RS232): {description}")
                self.worker.connect(com_port=target_com, baudrate=target_baud)
        except Exception as exc:
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            self.show_error(f"Failed to connect to laser: {exc}")
            log.error(f"Failed to connect to laser: {exc}")
            return False
        else:
            self.is_connected = True
            self.connectionStatusChanged.emit(True)
            self.show_success(f"Laser controller connected successfully ({description})")
            log.info(f"Laser controller connected successfully ({description})")
            return True

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
    def activateScript(self, script_number=None):
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
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False
        except Exception as exc:
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False

    def setContent(self, script=None, content=None):
        """Gửi lệnh C2 để nạp dữ liệu vào block"""
        if not self._ensure_connection():
            self.show_error("Failed to connect to laser")
            log.error("Failed to connect to laser")
            return False
        script_id = str(script or self.default_script)
        try:
            self.worker.send_c2(script_id, content, timeout_ms=self.command_timeout_ms)
            self.show_success("C2 command completed")
            log.info("C2 command completed")
            return True
        except (RuntimeError, TimeoutError, OSError) as exc:
            # Phát hiện mất kết nối khi gửi lệnh thất bại
            self._handle_connection_lost()
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False
        except Exception as exc:
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False

    def startMarking(self):
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
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False
        except Exception as exc:
            self.show_error(f"Error: {exc}")
            log.error(f"Error: {exc}")
            return False

    # ------------------------------------------------------------------
    # High-level flows
    # ------------------------------------------------------------------
    def startLaserMarkingProcess(self, script=None, content=None):
        """Bắt đầu quy trình laser marking"""
        script_id = script or self.default_script

        self.show_info("=== START LASER MARKING ===")
        log.info("=== START LASER MARKING ===")
        if not self.activateScript(script_id):
            return False

        if not self.setContent(script_id, content):
            return False

        if not self.startMarking():
            return False

        self.show_success("===LASER MARKING COMPLETED===")
        log.info("===LASER MARKING COMPLETED===")
        return True

    def sendCustomCommand(self, command, expect_keyword=None):
        if not self._ensure_connection():
            return False

        self.show_info(f"Send custom command Manual: {command.strip()}")
        log.info(f"Send custom command Manual: {command.strip()}")
        try:
            response = self.worker.sendRawCommand(
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

    # def sendGAtoLaser(self):
    #     """Gửi lệnh GA với script mặc định"""
    #     if not self._ensure_connection():
    #         raise RuntimeError("Laser is not connected")

    #     script = str(self.default_script)
    #     try:
    #         self.worker.send_ga(script, timeout_ms=self.command_timeout_ms)
    #         self.show_success(f"Send GA,{script} to laser successfully")
    #         log.info(f"Send GA,{script} to laser successfully")
    #     except Exception as exc:
    #         self._handle_connection_lost()
    #         self.show_error(f"Failed to send GA,{script} to laser: {exc}")
    #         log.error(f"Failed to send GA,{script} to laser: {exc}")
    #         raise

    # def sendNTtoLaser(self):
    #     """Gửi lệnh NT"""
    #     if not self._ensure_connection():
    #         raise RuntimeError("Laser is not connected")

    #     try:
    #         response = self.worker.send_nt(timeout_ms=self.command_timeout_ms)
    #         self.show_success("Send NT to laser successfully")
    #         log.info(f"Send NT to laser successfully: {response or '(empty)'}")
    #         return response
    #     except Exception as exc:
    #         self._handle_connection_lost()
    #         self.show_error(f"Failed to send NT to laser: {exc}")
    #         log.error(f"Failed to send NT to laser: {exc}")
    #         raise

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_connection(self):
        if self.is_connected:
            if not self.worker.checkConnectionAlive():
                self.worker.is_connected = False
                self._handle_connection_lost()
                return False
            return True
        return self.connect()
    
    def _handle_connection_lost(self):
        """Xử lý khi phát hiện mất kết nối - cập nhật UI ngay lập tức"""
        if self.is_connected:
            self.worker.disconnect()
            self.is_connected = False
            self.connectionStatusChanged.emit(False)
            log.warning("Laser connection lost - updating UI immediately")
            self.show_warning("Laser connection lost")

    def startAutoConnectLaser(self):
        """Bắt đầu tự động kết nối và duy trì kết nối"""
        self.auto_reconnect_enabled = True
        log.info("Starting auto-connect for laser controller...")
        self.show_info("Auto-connecting to laser controller...")
        self._try_connect()
        self.reconnect_timer.start(self.reconnect_ms)
        log.info(f"Auto-reconnect timer started (interval: {self.reconnect_ms}ms)")

    def stopAutoConnect(self):
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
                if self.laser_mode == LaserConnectMode.TCP:
                    self.worker.connect(self.laser_ip, self.laser_port)
                    description = f"{self.laser_ip}:{self.laser_port}"
                else:
                    self.worker.connect(com_port=self.laser_com_port, baudrate=self.laser_baudrate)
                    description = f"{self.laser_com_port}@{self.laser_baudrate}"
                self.is_connected = True
                self.connectionStatusChanged.emit(True)
                log.info(f"Laser auto-connected: {description}")
        except Exception as exc:
            # Chỉ log khi lần đầu fail hoặc khi reconnect thành công sau khi fail
            if self.is_connected:
                # Nếu trước đó đã connected nhưng bây giờ fail, có thể connection bị mất
                self.is_connected = False
                self.connectionStatusChanged.emit(False)
                log.warning(f"Laser connection lost: {exc}")
            # Không log mỗi lần fail để tránh spam log

    def _checkAndReconnect(self):
        """Kiểm tra và tự động kết nối lại nếu bị ngắt"""
        if not self.auto_reconnect_enabled:
            return
        worker_connected = self.worker.checkConnectionAlive()
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
        self.stopAutoConnect()
        self.disconnect()
    