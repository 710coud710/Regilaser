"""
SFIS Presenter - Xử lý logic giao tiếp SFIS
"""
from PySide6.QtCore import QThread, Signal, QMetaObject, Qt, Q_ARG, QTimer
from utils.setting import settings_manager
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
# Khởi tạo logger
log = getLogger()

class SFISPresenter(BasePresenter):
    """Presenter xử lý SFIS communication"""
    # Signals
    logMessage = Signal(str, str)  # (message, level)
    connectionStatusChanged = Signal(bool)  # Trạng thái kết nối
    dataReady = Signal(object)  # SFISData đã sẵn sàng
    startSignalSent = Signal()  # (success, message) - START signal đã gửi
    
    def __init__(self):
        super().__init__()        
        # Khởi tạo Model
        self.sfis_model = SFISModel()
        
        # Khởi tạo Worker và Thread cho SFIS (chỉ cần 1 worker)
        self.sfis_worker = SFISWorker()
        self.sfis_thread = QThread()
        self.sfis_worker.moveToThread(self.sfis_thread)
        # Kết nối signals
        self._connectSignals()
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
    
    def _connectSignals(self):
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
            op_number = settings_manager.get("general.op_num", "")  # Lấy OP_Number từ instance 
        message_op = "{:<20}END\r\n".format(op_number if op_number else "")
        if not self.sfis_worker.sendData_SFIS(message_op):
            self.show_error("Failed to send OP number to SFIS")
            log.error("Failed to send OP number to SFIS")
            return False
    # Auto connect / reconnect
    # ------------------------------------------------------------------
    def startAutoConnectSFIS(self, portName: str | None = None):
        """Bắt đầu tự động kết nối SFIS"""
        self.auto_reconnect_enabled = True
        if portName:
            self.currentPort = portName
        elif not self.currentPort:
            self.currentPort = self.sfis_worker.port_name
        # self.show_info(f"[SFIS] Auto-connect enabled on {self.currentPort}")
        # log.info(f"[SFIS] Auto-connect enabled on {self.currentPort}")
        self._tryConnect()
        self.reconnect_timer.start(self.reconnect_ms)
        log.info(f"SFIS auto-connect started ({self.reconnect_ms}ms)")
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
    
    def getDataFromSFIS(self):
        try:
            log.info("getDataFromSFIS started")
            mode = settings_manager.get("project.SFIS_format", 1)
            log.info(f"Mode: {mode}")
            if mode == 1:
                return self.getDataFromSFIS_MODE1()
            elif mode == 2:
                return self.getDataFromSFIS_MODE2()
            else:
                log.error("Error in getDataFromSFIS: Invalid mode")
                return False
        except Exception as e:
            self.show_error(f"Error in getDataFromSFIS: {e}")
            log.error(f"Error in getDataFromSFIS: {e}")
            return False

    def getDataFromSFIS_MODE2(self):
        mo = settings_manager.get("general.mo", '')
        pcb_product_name = settings_manager.get("general.pcb_product_name", '')
        pcb_number = settings_manager.get("general.pcb_number", '')
        
        return False

    def getDataFromSFIS_MODE1(self):
        mo = settings_manager.get("general.mo", '')
        panel_num = settings_manager.get("general.panel_num", '')
        try:
            needpsn_message = self.sfis_model.createFormatNeedPSN(mo, panel_num)
            if not needpsn_message:
                self.show_error("Failed to create NEEDPSN message")
                log.error("Failed to create NEEDPSN message")
                return False
            if not self.sfis_worker.sendData_SFIS(needpsn_message):
                self.show_error("Failed to send NEEDPSN message to SFIS")
                log.error("Failed to send NEEDPSN message to SFIS")
                return False
            data_res = self.sfis_worker.readData_SFIS(timeout_ms=10000)
            # log.info(f"Data received from SFIS: {data_res}")
            if not data_res:
                self.show_error("Timeout or no data received from SFIS")
                log.error("Timeout or no data received from SFIS")
                return False
            sfisData = self.sfis_model.parseResponsePsn(data_res)
            # log.info(f"Parsed data: {sfisData}")
            return sfisData
        except Exception as e:
            self.show_error(f"Error in getDataFromSFIS: {e}")
            log.error(f"Error in getDataFromSFIS: {e}")
            return False


    def sendNEEDPSN(self, mo=None,panel_num=None):
        if not self.isConnected:
            self.show_error("SFIS is not connected")
            log.error("SFIS not connected")
            return False
        
        if panel_num is None:
            panel_num = settings_manager.get("general.panel_num", '') 
        if mo is None:
            mo = settings_manager.get("general.mo", '')  
        # tạo format gửi lên SFIS
        start_message = self.sfis_model.createFormatNeedPSN(mo, panel_num)
        if not start_message:
            self.show_error("Failed to create START message")
            log.error("Failed to create START message")
            return False
        # Invoke worker method trong thread của nó (fire and forget)
        # success = self.sfis_worker.send_Signal(start_message)
        QMetaObject.invokeMethod(
            self.sfis_worker,
            "send_Signal",
            Qt.QueuedConnection,
            Q_ARG(str, start_message)
        )        
        log.info("SFISWorker invoked successfully-->waiting for signal_sent callback...")
        return True
    
    def sendComplete(self, mo=None, panelNo=None) -> bool:
        """   thông báo hoàn thành test"""
        if not self.isConnected:
            self.show_info("Chưa kết nối SFIS", "ERROR")
            return False
        
        message = self.sfis_model.createTestComplete(mo, panelNo)
        
        if message:
            # self.show_info("send complete to SFIS...")
            # log.info(f"send complete to SFIS... {message}")
            success = self.sfis_worker.sendData_SFIS(message)
            if success:
                res = self.sfis_worker.readData_SFIS(timeout_ms=10000)
                if res:
                    self.show_success("Send test complete successfully")
                    log.info("Send test complete successfully")
                    return True
                else:
                    self.show_error("Timeout or no data received from SFIS")
                    log.error("Timeout or no data received from SFIS")
                    return False
            else:
                log.error("Send test complete failed")
                return False  
        log.error("Create test complete failed")
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
        try:
            data = self.sfis_model.parseResponsePsn(response)
            log.info(f"Parsed data: {data}")
            if not data:
                self.show_error("Failed to parse response from SFIS")
                log.error("Failed to parse response from SFIS")
                return False
            return data
        except Exception as e:
            self.show_error(f"Error in parseResponse: {e}")
            log.error(f"Error in parseResponse: {e}")
            return False
    
    def getCurrentData(self):
        """Lấy dữ liệu SFIS hiện tại"""
        return self.sfis_model.getCurrentData()
    
    def onDataReceived(self, data):
        log.info("DATA RECEIVED FROM SFIS")
        log.info(f"Length: {len(data)} bytes")
        log.info(f"Data (text): {data}")
        self.show_info(f" RECEIVED DATA FROM SFIS")
        self.show_info(f"  Length: {len(data)} bytes")
        self.show_info(f"  Data: {data}")
        
        # Thử parse nếu có thể (không bắt buộc)
        try:
            # log.info("Attempting to parse as PSN response...")
            parsedData = self.sfis_model.parseResponsePsn(data)
            if parsedData:
                log.info("PSN response parsed successfully:")
                # log.info(f"  Keyword: {parsedData.keyword}")
                # log.info(f"  MO: {parsedData.mo}")
                # log.info(f"  Panel Number: {parsedData.panel_no}")
                # log.info(f"  PSN count: {len(parsedData.psn_list)}")
                # self.show_info(f"  Keyword: {parsedData.keyword}")
                # self.show_info("PSN response parsed successfully:")
                # self.show_info(f"  MO: {parsedData.mo}")
                # self.show_info(f"  Panel Number: {parsedData.panel_no}")
                # self.show_info(f"  PSN count: {len(parsedData.psn_list)}")
                # for i, psn in enumerate(parsedData.psn_list, 1):
                #     self.show_info(f"  PSN {i}: {psn}")
                #     log.info(f"  PSN {i}: {psn}")   
                return parsedData
                
            else:
                log.warning("Could not parse as PSN response (format may differ)")
                self.show_info("Could not parse as PSN response (format may differ)")
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
    def _tryConnect(self):
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
            self._tryConnect()
    
    def onStartSignalSent(self, success, message):
        """Xử lý khi START signal đã được gửi"""
        log.info(f"Success: {success}")
        log.info(f"Message: {message}")
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
        self.startSignalSent.emit
    
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
        #dọn dẹp auto-reconnect
        self.auto_reconnect_enabled = False
        if self.reconnect_timer.isActive():
            self.reconnect_timer.stop()
    
        # Disconnect
        if self.isConnected:
            self.disconnect()
        
        # Dừng thread
        self.sfis_thread.quit()
        self.sfis_thread.wait()
        
        log.info("SFISPresenter cleanup completed")

   