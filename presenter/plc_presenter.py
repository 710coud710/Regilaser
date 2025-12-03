"""
PLC Presenter - Xử lý logic giao tiếp PLC (Programmable Logic Controller)
"""
from PySide6.QtCore import QThread, QMetaObject, Qt, Q_ARG, Signal, QTimer

from presenter.base_presenter import BasePresenter
from workers.plc_worker import PLCWorker
from utils.Logging import getLogger


log = getLogger()


class PLCPresenter(BasePresenter):
    """Presenter xử lý PLC communication"""
    logMessage = Signal(str, str)
    readyReceived = Signal(str)
    connectionStatusChanged = Signal(bool)  # (is_connected)

    def __init__(self):
        super().__init__()
        self.plc_worker = PLCWorker()
        self.plc_thread = QThread()
        self.plc_worker.moveToThread(self.plc_thread)
        self._connect_worker_signals()
        self.plc_thread.start()

        self.is_connected = False
        self.current_port = self.plc_worker.port_name

        # Auto-reconnect timer
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._checkAndReconnect)
        self.reconnect_ms = 5000  # 5 giây
        self.auto_reconnect_enabled = False

    def _connect_worker_signals(self):
        self.plc_worker.error_occurred.connect(self.onPLCError)
        self.plc_worker.connectionStatusChanged.connect(self.onConnectionChanged)

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def connect(self, port_name):
        """Kết nối đến PLC"""
        self.show_info(f"Connecting PLC on {port_name}...")
        QMetaObject.invokeMethod(
            self.plc_worker,
            "connect",
            Qt.BlockingQueuedConnection,
            Q_ARG(str, port_name),
        )
        if self.plc_worker.is_connected:
            self.is_connected = True
            self.current_port = port_name
            self.show_success(f"PLC connected on {port_name}")
        else:
            self.show_error(f"Failed to connect PLC on {port_name}")
        return self.plc_worker.is_connected

    def disconnect(self):
        """Ngắt kết nối PLC"""
        QMetaObject.invokeMethod(
            self.plc_worker,
            "disconnect",
            Qt.BlockingQueuedConnection,
        )
        self.is_connected = False
        self.current_port = ""
        return True

    # ------------------------------------------------------------------
    # Auto connect / reconnect
    # ------------------------------------------------------------------
    def startAutoConnectPLC(self, port_name: str | None = None):
        """
        Bắt đầu tự động kết nối PLC.
        - Nếu port_name None: dùng current_port / cấu hình mặc định trong worker.
        """
        self.auto_reconnect_enabled = True
        if port_name:
            self.current_port = port_name
        self.show_info(f"[PLC] Auto-connect enabled on {self.current_port}")
        log.info(f"[PLC] Auto-connect enabled on {self.current_port}")
        # Thử kết nối ngay một lần
        self._try_connect()
        # Bắt đầu timer định kỳ
        self.reconnect_timer.start(self.reconnect_ms)

    def stopAutoConnectPLC(self):
        """Dừng tự động kết nối PLC."""
        self.auto_reconnect_enabled = False
        self.reconnect_timer.stop()
        log.info("[PLC] Auto-connect stopped")

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    def sendData_PLC(self, label: str, payload: str = ""):
        command = self.plc_model.build_command(label, payload)
        if not command:
            return False
        self.show_info(f"PLC command: {command}")
        return QMetaObject.invokeMethod(
            self.plc_worker,
            "sendData_PLC",
            Qt.BlockingQueuedConnection,
            Q_ARG(str, command),
        )

    def sendLaserOK(self):
        return self.sendData_PLC("L_OK")

    def sendLaserNG(self):
        return self.sendData_PLC("L_NG")

    def sendCheckOK(self):
        return self.sendData_PLC("CHE_OK")

    def sendCheckNG(self):
        return self.sendData_PLC("CHE_NG")


    def onPLCError(self, errorMsg):
        self.show_error(f"[PLC] Error: {errorMsg}")
        log.error(f"[PLC] {errorMsg}")

    def onConnectionChanged(self, isConnected):
        self.is_connected = isConnected
        status = "Connected" if isConnected else "Disconnected"
        self.show_info(f"[PLC] {status}")
        # Thông báo ra ngoài (MainPresenter / UI)
        self.connectionStatusChanged.emit(isConnected)

    # ------------------------------------------------------------------
    # Auto-reconnect helpers
    # ------------------------------------------------------------------
    def _try_connect(self):
        """Thử kết nối PLC (không log nhiều để tránh spam)."""
        if not self.auto_reconnect_enabled:
            return
        if self.is_connected:
            return

        try:
            # Gọi connect trên worker (trong thread của worker)
            QMetaObject.invokeMethod(
                self.plc_worker,
                "connect",
                Qt.BlockingQueuedConnection,
                Q_ARG(str, self.current_port),
            )
            if self.plc_worker.is_connected:
                self.is_connected = True
                self.show_success(f"[PLC] Auto-connected on {self.current_port}")
                log.info(f"[PLC] Auto-connected on {self.current_port}")
        except Exception as exc:
            log.warning(f"[PLC] Auto-connect failed: {exc}")

    def _checkAndReconnect(self):
        """Kiểm tra và tự động kết nối lại nếu PLC bị ngắt."""
        if not self.auto_reconnect_enabled:
            return

        worker_connected = self.plc_worker.checkConnectionAlive()
        if self.is_connected != worker_connected:
            self.is_connected = worker_connected
            self.plc_worker.connectionStatusChanged.emit(worker_connected)

        if not self.is_connected:
            self._try_connect()

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self):
        self.disconnect()
        self.plc_thread.quit()
        self.plc_thread.wait()