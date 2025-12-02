"""
PLC Presenter - Xử lý logic giao tiếp PLC (Programmable Logic Controller)
"""
from PySide6.QtCore import QThread, QMetaObject, Qt, Q_ARG, Signal

from presenter.base_presenter import BasePresenter
from model.plc_model import PLCModel
from workers.plc_worker import PLCWorker
from utils.Logging import getLogger


log = getLogger()


class PLCPresenter(BasePresenter):
    """Presenter xử lý PLC communication"""
    logMessage = Signal(str, str)
    readyReceived = Signal(str)

    def __init__(self):
        super().__init__()
        self.plc_model = PLCModel()
        self.plc_worker = PLCWorker()
        self.plc_thread = QThread()
        self.plc_worker.moveToThread(self.plc_thread)
        self._connect_worker_signals()
        self.plc_thread.start()

        self.is_connected = False
        self.current_port = self.plc_worker.port_name

    def _connect_worker_signals(self):
        self.plc_worker.data_received.connect(self.onDataReceived)
        self.plc_worker.error_occurred.connect(self.onError)
        self.plc_worker.connectionStatusChanged.connect(self.onConnectionChanged)

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def connect(self, port_name="COM3"):
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
    # Commands
    # ------------------------------------------------------------------
    def send_command(self, label: str, payload: str = ""):
        command = self.plc_model.build_command(label, payload)
        if not command:
            return False
        self.show_info(f"PLC command: {command}")
        return QMetaObject.invokeMethod(
            self.plc_worker,
            "send_command",
            Qt.BlockingQueuedConnection,
            Q_ARG(str, command),
        )

    def wait_for_signal(self, expected_signal: str, timeout_ms=3000):
        self.show_info(f"Waiting PLC signal: {expected_signal}")
        return QMetaObject.invokeMethod(
            self.plc_worker,
            "wait_for_signal",
            Qt.BlockingQueuedConnection,
            Q_ARG(str, expected_signal),
            Q_ARG(int, timeout_ms),
        )

    def send_laser_ok(self):
        return self.send_command("L_OK")

    def send_laser_ng(self):
        return self.send_command("L_NG")

    def send_check_ok(self):
        return self.send_command("CHE_OK")

    def send_check_ng(self):
        return self.send_command("CHE_NG")

    # ------------------------------------------------------------------
    # Worker callbacks
    # ------------------------------------------------------------------
    def onDataReceived(self, data):
        # In toàn bộ dữ liệu nhận từ COM ra log + UI
        log.info(f"[PLC] data_received from COM: {data}")
        self.show_info(f"[PLC] Received: {data}")
        parsed = self.plc_model.parse_response(data)
        # Nếu PLC gửi READY / Ready / ready... thì phát tín hiệu để MainPresenter xử lý start test
        if parsed and "ready" or "READY" or "Ready" in parsed.lower():
            self.show_info("[PLC] READY signal detected -> request start test")
            self.readyReceived.emit(parsed)

    def onError(self, errorMsg):
        self.show_error(f"[PLC] Error: {errorMsg}")
        log.error(f"[PLC] {errorMsg}")

    def onConnectionChanged(self, isConnected):
        self.is_connected = isConnected
        status = "Connected" if isConnected else "Disconnected"
        self.show_info(f"[PLC] {status}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self):
        self.disconnect()
        self.plc_thread.quit()
        self.plc_thread.wait()