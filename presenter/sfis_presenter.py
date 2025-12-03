"""
SFIS Presenter - Xử lý logic giao tiếp SFIS
"""
from PySide6.QtCore import QThread, Signal, QMetaObject, Qt, Q_ARG, QTimer
from config import ConfigManager
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
# Khởi tạo logger
log = getLogger()
config = ConfigManager().get()

class SFISPresenter(BasePresenter):
    """Presenter xử lý SFIS communication"""
    # Signals
    logMessage = Signal(str, str)  # (message, level)
    connectionStatusChanged = Signal(bool)  # Trạng thái kết nối
    dataReady = Signal(object)  # SFISData đã sẵn sàng
    startSignalSent = Signal(bool, str)  # (success, message) - START signal đã gửi
    
    def __init__(self):
        super().__init__()        
        # Khởi tạo Model
        self.sfis_model = SFISModel()
        
        # Khởi tạo Worker và Thread cho SFIS (chỉ cần 1 worker)
        self.sfis_worker = SFISWorker()
        self.sfis_thread = QThread()
        self.sfis_worker.moveToThread(self.sfis_thread)
        # Kết nối signals
        self.connectSignals()
        # Khởi động thread
        self.sfis_thread.start()
        # Trạng thái
        self.isConnected = False
        self.currentPort = None

        # Auto-reconnect timer
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._checkAndReconnect)
        self.reconnect_ms = 5000  # 5 giây
        self.auto_reconnect_enabled = False

        log.info("SFISPresenter initialized successfully")
    
    def connectSignals(self):
        """Kết nối signals giữa Worker và Model"""
        # SFIS Worker signals
        self.sfis_worker.data_received.connect(self.onDataReceived)
        self.sfis_worker.error_occurred.connect(self.onError)
        self.sfis_worker.connectionStatusChanged.connect(self.onConnectionChanged)
        self.sfis_worker.signal_sent.connect(self.onStartSignalSent)
        
        # SFIS Model signals
        self.sfis_model.data_parsed.connect(self.onDataParsed)
        self.sfis_model.validation_error.connect(self.onValidationError)
    
    def connect(self, portName):
        """Kết nối đến SFIS qua COM port"""
        self.show_info(f"Connecting to SFIS on port: {portName}...")
        log.info(f"Connecting to SFIS on port: {portName}...")
        
        # Gọi connect() trong thread của worker
        QMetaObject.invokeMethod(
            self.sfis_worker,
            "connect",
            Qt.BlockingQueuedConnection,  # Chờ kết quả
            Q_ARG(str, portName)
        )
        
        # Kiểm tra trạng thái kết nối
        success = self.sfis_worker.is_connected
        
        if success:
            self.currentPort = portName
            self.show_success(f"Connected to SFIS on port: {portName}")
            log.info(f"Connected to SFIS on port: {portName}")
        else:
            self.show_error(f"Failed to connect to SFIS on port: {portName}")
            log.error(f"Failed to connect to SFIS on port: {portName}")
        return success
    
    def disconnect(self):
        """Ngắt kết nối SFIS"""
        self.show_info("Disconnecting from SFIS...", "INFO")
        log.info("Disconnecting from SFIS...")
        
        # Gọi disconnect() trong thread của worker
        QMetaObject.invokeMethod(
            self.sfis_worker,
            "disconnect",
            Qt.BlockingQueuedConnection  # Chờ kết quả
        )
        
        success = not self.sfis_worker.is_connected
        
        if success:
            self.currentPort = None
            self.show_info("Ngắt kết nối SFIS thành công", "INFO")
            log.info("Ngắt kết nối SFIS thành công")
        else:
            self.show_info("Lỗi ngắt kết nối SFIS", "ERROR")
            log.error("Lỗi ngắt kết nối SFIS")
        
        return success

    def activateSFIS(self, op_number=None):
        """Gửi tín hiệu ACTIVATE (UNDO + OP Number) đến SFIS để bắt đầu quy trình EMP"""
        if not self.isConnected:
            self.show_error("SFIS is not connected")
            log.error("SFIS is not connected")
            return False
        #Reset SFIS
        message_undo = "UNDO\r\n"
        if not self.sfis_worker.sendData_SFIS(message_undo):
            self.show_error("Failed to send UNDO to SFIS")
            log.error("Failed to send UNDO to SFIS")
            return False

        import time
        time.sleep(0.2)

        # Send OP Number
        if op_number is None:
            op_number = getattr(config, 'OP_NUM', '')  # Lấy OP_Number từ instance 
        formatted_op = "{:<20}END\r\n".format(op_number if op_number else "")
        if not self.sfis_worker.sendData_SFIS(formatted_op):
            self.show_error("Failed to send OP number to SFIS")
            log.error("Failed to send OP number to SFIS")
            return False
    # Auto connect / reconnect
    # ------------------------------------------------------------------
    def startAutoConnectSFIS(self, portName: str | None = None):
        """
        Bắt đầu tự động kết nối SFIS.
        - Nếu portName None: dùng currentPort hoặc cấu hình mặc định trong worker.
        """
        self.auto_reconnect_enabled = True
        if portName:
            self.currentPort = portName
        elif not self.currentPort:
            # Nếu chưa có port cụ thể thì dùng port mặc định của worker
            self.currentPort = self.sfis_worker.port_name

        self.show_info(f"[SFIS] Auto-connect enabled on {self.currentPort}")
        log.info(f"[SFIS] Auto-connect enabled on {self.currentPort}")

        # Thử kết nối ngay một lần
        self._try_connect()
        # Bắt đầu timer định kỳ
        self.reconnect_timer.start(self.reconnect_ms)

    def stopAutoConnectSFIS(self):
        """Dừng tự động kết nối SFIS."""
        self.auto_reconnect_enabled = False
        self.reconnect_timer.stop()
        log.info("[SFIS] Auto-connect stopped")
    
    def requestDataSFIS(self, mo=None, panelNo=None):
        if not self.isConnected:
            self.show_error("[SFIS] not connected")
            log.error("[SFIS] not connected")
            return None
        
        self.show_info("[SFIS] Waiting for data from SFIS...")
        log.info("[SFIS] Waiting for data from SFIS...")
        # Đọc dữ liệu với timeout 5s
        response = self.sfis_worker.readData_PLC(expected_length=70, timeout_ms=5000, mo=mo, panelNo=panelNo)
        
        if response:
            self.show_info(f"Received data from SFIS: {response}")
            log.info(f"Received data from SFIS: {response}")
            return response
        else:
            self.show_error("Timeout hoặc không nhận được dữ liệu từ SFIS")
            log.error("Timeout hoặc không nhận được dữ liệu từ SFIS")
            return None
    
    def sendNEEDPSN(self, mo=None,panel_num=None):
        if not self.isConnected:
            self.show_error("SFIS is not connected")
            log.error("SFIS not connected")
            return False
        
        if panel_num is None:
            panel_num = getattr(config, 'PANEL_NUM', '')  # Lấy PANEL_NUM từ instance 
            
        # Bước 1: SFISModel tạo START message
        start_message = self.sfis_model.createStartSignal(mo, panel_num)

        if not start_message:
            self.show_error("Failed to create START message")
            log.error("Failed to create START message")
            return False
        # LOG detailed message
        log.info("START Message created successfully:")
        log.info(f"  Data sent: {start_message}")
        log.info(f"  Length: {len(start_message)} bytes (expected: 49)")

        # UI Log
        self.show_info(f"  DATA: {start_message} Length: {len(start_message)} bytes" )
        # Bước 2: Gửi qua SFISWorker trong thread riêng
        log.info("Invoking SFISWorker to send via COM port...")
        self.show_info("Sending START signal via COM port...")
        
        # Invoke worker method trong thread của nó (fire and forget)
        QMetaObject.invokeMethod(
            self.sfis_worker,
            "send_start_signal",
            Qt.QueuedConnection,  # Không chờ kết quả
            Q_ARG(str, start_message)
        )
        
        log.info("SFISWorker invoked successfully (fire and forget)")
        log.info("Waiting for signal_sent callback...")
        return True
    
    def sendComplete(self, mo, panelNo):
        """   thông báo hoàn thành test"""
        if not self.isConnected:
            self.show_info("Chưa kết nối SFIS", "ERROR")
            return False
        
        message = self.sfis_model.createTestComplete(mo, panelNo)
        
        if message:
            self.show_info("Gửi test complete đến SFIS...", "INFO")
            success = self.sfis_worker.sendData_SFIS(message)
            
            if success:
                self.show_info("Gửi test complete thành công", "SUCCESS")
                return True
            else:
                self.show_info("Gửi test complete thất bại", "ERROR")
                return False
        
        return False
    
    def sendTestError(self, mo, panelNo, errorCode):
        """  Gửi thông báo lỗi test"""
        if not self.isConnected:
            self.show_info("Chưa kết nối SFIS", "ERROR")
            return False
        
        message = self.sfis_model.create_test_error(mo, panelNo, errorCode)
        
        if message:
            self.show_info(f"Gửi test error ({errorCode}) đến SFIS...", "INFO")
            success = self.sfis_worker.sendData_SFIS(message)
            
            if success:
                self.show_info("Gửi test error thành công", "SUCCESS")
                return True
            else:
                self.show_info("Gửi test error thất bại", "ERROR")
                return False
        
        return False
    
    def parseResponse(self, response):
        """  Parse response từ SFIS"""
        return self.sfis_model.parse_response_new_format(response)
    
    def getCurrentData(self):
        """Lấy dữ liệu SFIS hiện tại"""
        return self.sfis_model.get_current_data()
    
    def onDataReceived(self, data):
        """
        Xử lý khi nhận được dữ liệu từ SFIS Worker
        Hiển thị TẤT CẢ dữ liệu nhận được lên log để phân tích
        """
        log.info("DATA RECEIVED FROM SFIS")
        log.info(f"Length: {len(data)} bytes")
        log.info(f"Data (text): '{data}'")
        
        # Phân tích chi tiết từng phần (mỗi 20 bytes)
        log.info("DETAILED BREAKDOWN (20-byte chunks):")
        for i in range(0, len(data), 20):
            chunk = data[i:i+20]
            chunk_hex = chunk.encode('ascii', errors='ignore').hex()
            log.info(f"  [{i:3d}-{i+len(chunk)-1:3d}] '{chunk}' (HEX: {chunk_hex})")
        
        # Hiển thị trên UI
        self.show_info(f" RECEIVED DATA FROM SFIS")
        self.show_info(f"  Length: {len(data)} bytes")
        self.show_info(f"  Data: {data}")
        
        # Phân tích chi tiết trên UI (mỗi 20 bytes)
        self.show_info("DETAILED BREAKDOWN:")
        for i in range(0, len(data), 20):
            chunk = data[i:i+20]
            self.show_info(f"  [{i:3d}-{i+len(chunk)-1:3d}] {chunk}")
        
        # Thử parse nếu có thể (không bắt buộc)
        try:
            log.info("Attempting to parse as PSN response...")
            parsedData = self.sfis_model.parseResponsePsn(data)
            
            if parsedData:
                log.info(" Successfully parsed as PSN response:")
                log.info(f"  MO: {parsedData.mo}")
                log.info(f"  Panel Number: {parsedData.panel_no}")
                # log.info(f"  PSN count: {len(parsedData.psn_list)}")
                for i, psn in enumerate(parsedData.psn_list, 1):
                    log.info(f"  PSN{i}: {psn}")
                
                # Hiển thị parsed data trên UI
                self.show_info("PARSED DATA:")
                self.show_info(f"  MO: {parsedData.mo}")
                self.show_info(f"  Panel: {parsedData.panel_no}")
                for i, psn in enumerate(parsedData.psn_list, 1):
                    self.show_info(f"  PSN{i}: {psn}")
            else:
                log.warning("Could not parse as PSN response (format may differ)")
                self.show_info("(Could not parse as PSN format)")
        except Exception as e:
            log.warning(f"Parse attempt failed: {str(e)}")
            self.show_info(f"(Parse attempt failed: {str(e)})")
    
    def onDataParsed(self, sfisData):
        """Xử lý khi dữ liệu đã được parse thành công"""
        self.show_info("Parse SFIS data successfully")
        self.show_info(f"  Laser SN: {sfisData.laser_sn}")
        self.show_info(f"  Status: {sfisData.status}")
        
        # Emit signal để MainPresenter xử lý tiếp
        self.dataReady.emit(sfisData)
    
    def onError(self, errorMsg):
        """Xử lý lỗi từ SFIS Worker"""
        self.show_error(f"SFIS Error: {errorMsg}")
        log.error(f"SFIS Error: {errorMsg}")
    
    def onValidationError(self, errorMsg):
        """Xử lý lỗi validation từ Model"""
        self.show_error(f"Validation Error: {errorMsg}")
    
    def onConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối thay đổi"""
        self.isConnected = isConnected
        status = "Connected" if isConnected else "Disconnected"
        self.show_info(f"SFIS: {status}")
        if isConnected:
            try:
                self.show_info("SFIS connected - auto ACTIVATE (UNDO + OP)")
                log.info("SFIS connected - auto calling activateSFIS()")
                self.activateSFIS()
            except Exception as exc:
                log.error(f"Auto activateSFIS failed: {exc}")
                self.show_error(f"Auto activateSFIS failed: {exc}")

        # Emit signal để MainPresenter cập nhật UI
        self.connectionStatusChanged.emit(isConnected)

    # ------------------------------------------------------------------
    # Auto-reconnect helpers
    # ------------------------------------------------------------------
    def _try_connect(self):
        """Thử kết nối SFIS (không log nhiều để tránh spam)."""
        if not self.auto_reconnect_enabled:
            return
        if self.isConnected:
            return

        try:
            # Gọi connect trên worker (trong thread của worker)
            QMetaObject.invokeMethod(
                self.sfis_worker,
                "connect",
                Qt.BlockingQueuedConnection,
                Q_ARG(str, self.currentPort),
            )
            if self.sfis_worker.is_connected:
                self.isConnected = True
                self.show_success(f"[SFIS] Auto-connected on {self.currentPort}")
                log.info(f"[SFIS] Auto-connected on {self.currentPort}")
        except Exception as exc:
            log.warning(f"[SFIS] Auto-connect failed: {exc}")

    def _checkAndReconnect(self):
        """Kiểm tra và tự động kết nối lại nếu SFIS bị ngắt."""
        if not self.auto_reconnect_enabled:
            return

        worker_connected = self.sfis_worker.checkConnectionAlive()
        if self.isConnected != worker_connected:
            self.isConnected = worker_connected
            self.connectionStatusChanged.emit(worker_connected)

        if not self.isConnected:
            self._try_connect()
    
    def onStartSignalSent(self, success, message):
        """Xử lý khi START signal đã được gửi"""
        if success:
            log.info("START signal sent successfully")
            self.show_success("START signal sent successfully")
            
            # Bắt đầu nhận dữ liệu từ SFIS
            log.info("Starting to receive PSN data from SFIS...")
            self.show_info("Waiting for PSN data from SFIS...")
            self.receiveResponsePsn()
        else:
            log.error(f"START signal failed: {message}")
            self.show_error(f"START signal sent failed: {message}")
        
        # Emit signal để MainPresenter biết
        self.startSignalSent.emit(success, message)
    
    def receiveResponsePsn(self):
        """
        Nhận TẤT CẢ dữ liệu từ SFIS sau khi gửi START signal
        """
        try:
            log.info("Starting to receive data from SFIS...")
            log.info("Reading ALL available data (no format restriction)")
            self.show_info("Waiting for data from SFIS...")
            
            QMetaObject.invokeMethod(
                self.sfis_worker,
                "readData_SFIS",
                Qt.QueuedConnection,
                Q_ARG(int, 10000)  # 10 seconds timeout
            )
            
            log.info("Read request sent to worker (reading all available data)")
            
        except Exception as e:
            error_msg = f"Error receiving data from SFIS: {str(e)}"
            log.error(error_msg)
            log.debug("Exception details:", exc_info=True)
            self.show_info(error_msg, "ERROR")
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        log.info("SFISPresenter.cleanup() called")
        
        if self.isConnected:
            self.sfis_worker.disconnect()
        
        # Dừng thread
        self.sfis_thread.quit()
        self.sfis_thread.wait()
        
        log.info("SFISPresenter cleanup completed")

   