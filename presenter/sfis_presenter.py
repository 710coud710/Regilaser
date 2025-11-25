"""
SFIS Presenter - Xử lý logic giao tiếp SFIS
"""
from PySide6.QtCore import QObject, QThread, Signal, QMetaObject, Qt, Q_ARG
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()


class SFISPresenter(QObject):
    """Presenter xử lý SFIS communication"""
    
    # Signals
    logMessage = Signal(str, str)  # (message, level)
    connectionStatusChanged = Signal(bool)  # Trạng thái kết nối
    dataReady = Signal(object)  # SFISData đã sẵn sàng
    startSignalSent = Signal(bool, str)  # (success, message) - START signal đã gửi
    
    def __init__(self):
        super().__init__()
        log.info("SFISPresenter.__init__ started")
        
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
        log.info("SFIS thread started")
        
        # Trạng thái
        self.isConnected = False
        self.currentPort = None
        
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
        self.logMessage.emit(f"Đang kết nối SFIS qua {portName}...", "INFO")
        log.info(f"Đang kết nối SFIS qua {portName}...")
        
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
            self.logMessage.emit(f"Kết nối SFIS thành công: {portName}", "SUCCESS")
            log.info(f"Kết nối SFIS thành công: {portName}")
        else:
            self.logMessage.emit(f"Kết nối SFIS thất bại: {portName}", "ERROR")
            log.error(f"Kết nối SFIS thất bại: {portName}")
        return success
    
    def disconnect(self):
        """Ngắt kết nối SFIS"""
        self.logMessage.emit("Disconnecting from SFIS...", "INFO")
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
            self.logMessage.emit("Ngắt kết nối SFIS thành công", "INFO")
            log.info("Ngắt kết nối SFIS thành công")
        else:
            self.logMessage.emit("Lỗi ngắt kết nối SFIS", "ERROR")
            log.error("Lỗi ngắt kết nối SFIS")
        
        return success
    
    def requestData(self, mo=None, allPartsSn=None):
        """
        Yêu cầu dữ liệu từ SFIS - Dữ liệu nhận được, hoặc None nếu lỗi        
        Args:
            mo (str): Manufacturing Order (không bắt buộc)
            allPartsSn (str): ALL PARTS SN (không bắt buộc)

        """
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            log.error("Chưa kết nối SFIS")
            return None
        
        self.logMessage.emit("Đang chờ dữ liệu từ SFIS...", "INFO")
        log.info("Đang chờ dữ liệu từ SFIS...")
        # Đọc dữ liệu với timeout 5s
        response = self.sfis_worker.read_data(expected_length=70, timeout_ms=5000)
        
        if response:
            self.logMessage.emit(f"Nhận dữ liệu từ SFIS: {response}", "DEBUG")
            log.debug(f"Nhận dữ liệu từ SFIS: {response}")
            return response
        else:
            self.logMessage.emit("Timeout hoặc không nhận được dữ liệu từ SFIS", "ERROR")
            log.error("Timeout hoặc không nhận được dữ liệu từ SFIS")
            return None
    
    def sendStartSignal(self, mo=None, panel_no=None):
        """
        Gửi tín hiệu START đến SFIS qua COM port (fire and forget)
        Flow:
        1. SFISModel tạo START message (49 bytes)
        2. SFISWorker gửi qua COM port trong thread riêng
        3. Không chờ phản hồi từ SFIS       
        """
        log.info("=" * 20)
        log.info("SFISPresenter.sendStartSignal() called")
        
        # Kiểm tra kết nối
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            log.error("SFIS not connected")
            return False
        
        # Lấy config để hiển thị Panel_Num
        from config import ConfigManager
        config = ConfigManager().get()
        panel_num = config.Panel_Num if config else "??"
        
        # Bước 1: SFISModel tạo START message
        log.info("Step 1: Creating START message via SFISModel...")
        start_message = self.sfis_model.createStartSignal(mo, None, panel_no)
        
        if not start_message:
            self.logMessage.emit("Lỗi tạo START signal", "ERROR")
            log.error("Failed to create START message")
            return False
        # LOG detailed message
        log.info("START Message created successfully:")
        log.info(f"  Data sent: {start_message}")
        log.info(f"  Length: {len(start_message)} bytes (expected: 49)")
        log.info("=" * 20)
        
        # UI Log
        self.logMessage.emit("GỬI START SIGNAL:", "INFO")
        self.logMessage.emit(f"  DATA: {start_message}", "INFO")
        self.logMessage.emit(f"  Length: {len(start_message)} bytes", "INFO")
        self.logMessage.emit(f"  COM Port: {self.currentPort}", "INFO")
        
        # Bước 2: Gửi qua SFISWorker trong thread riêng
        log.info("Step 2: Invoking SFISWorker to send via COM port...")
        self.logMessage.emit("Sending START signal via COM port...", "INFO")
        
        # Invoke worker method trong thread của nó (fire and forget)
        QMetaObject.invokeMethod(
            self.sfis_worker,
            "send_start_signal",
            Qt.QueuedConnection,  # Không chờ kết quả
            Q_ARG(str, start_message)
        )
        
        log.info("SFISWorker invoked successfully (fire and forget)")
        log.info("Waiting for signal_sent callback...")
        log.info("=" * 70)
        return True
    
    def sendTestComplete(self, mo, panelNo):
        """
        Gửi thông báo hoàn thành test
        
        Args:
            mo (str): Manufacturing Order
            panelNo (str): Panel Number
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            return False
        
        message = self.sfis_model.createTestComplete(mo, panelNo)
        
        if message:
            self.logMessage.emit("Gửi test complete đến SFIS...", "INFO")
            success = self.sfis_worker.send_data(message)
            
            if success:
                self.logMessage.emit("Gửi test complete thành công", "SUCCESS")
                return True
            else:
                self.logMessage.emit("Gửi test complete thất bại", "ERROR")
                return False
        
        return False
    
    def sendTestError(self, mo, panelNo, errorCode):
        """
        Gửi thông báo lỗi test
        
        Args:
            mo (str): Manufacturing Order
            panelNo (str): Panel Number
            errorCode (str): Mã lỗi
            
        Returns:
            bool: True nếu gửi thành công
        """
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            return False
        
        message = self.sfis_model.create_test_error(mo, panelNo, errorCode)
        
        if message:
            self.logMessage.emit(f"Gửi test error ({errorCode}) đến SFIS...", "INFO")
            success = self.sfis_worker.send_data(message)
            
            if success:
                self.logMessage.emit("Gửi test error thành công", "SUCCESS")
                return True
            else:
                self.logMessage.emit("Gửi test error thất bại", "ERROR")
                return False
        
        return False
    
    def parseResponse(self, response):
        """
        Parse response từ SFIS
        
        Args:
            response (str): Response string
            
        Returns:
            SFISData: Dữ liệu đã parse, hoặc None nếu lỗi
        """
        return self.sfis_model.parse_response_new_format(response)
    
    def getCurrentData(self):
        """Lấy dữ liệu SFIS hiện tại"""
        return self.sfis_model.get_current_data()
    
    def onDataReceived(self, data):
        """
        Xử lý khi nhận được dữ liệu từ SFIS Worker
        Hiển thị TẤT CẢ dữ liệu nhận được lên log để phân tích
        """
        log.info("=" * 70)
        log.info("DATA RECEIVED FROM SFIS")
        log.info("=" * 70)
        log.info(f"Length: {len(data)} bytes")
        log.info(f"Data (text): '{data}'")
        log.info(f"Data (HEX):  {data.encode('ascii', errors='ignore').hex()}")
        
        # Phân tích chi tiết từng phần (mỗi 20 bytes)
        log.info("-" * 70)
        log.info("DETAILED BREAKDOWN (20-byte chunks):")
        for i in range(0, len(data), 20):
            chunk = data[i:i+20]
            chunk_hex = chunk.encode('ascii', errors='ignore').hex()
            log.info(f"  [{i:3d}-{i+len(chunk)-1:3d}] '{chunk}' (HEX: {chunk_hex})")
        log.info("=" * 70)
        
        # Hiển thị trên UI
        self.logMessage.emit("=" * 70, "INFO")
        self.logMessage.emit(f"✓ RECEIVED DATA FROM SFIS", "SUCCESS")
        self.logMessage.emit(f"  Length: {len(data)} bytes", "INFO")
        self.logMessage.emit(f"  Data: {data}", "INFO")
        self.logMessage.emit("=" * 70, "INFO")
        
        # Phân tích chi tiết trên UI (mỗi 20 bytes)
        self.logMessage.emit("DETAILED BREAKDOWN:", "INFO")
        for i in range(0, len(data), 20):
            chunk = data[i:i+20]
            self.logMessage.emit(f"  [{i:3d}-{i+len(chunk)-1:3d}] {chunk}", "INFO")
        self.logMessage.emit("=" * 70, "INFO")
        
        # Thử parse nếu có thể (không bắt buộc)
        try:
            log.info("Attempting to parse as PSN response...")
            parsedData = self.sfis_model.parseResponsePsn(data)
            
            if parsedData:
                log.info("✓ Successfully parsed as PSN response:")
                log.info(f"  MO: {parsedData.mo}")
                log.info(f"  Panel Number: {parsedData.panel_no}")
                log.info(f"  PSN count: {len(parsedData.psn_list)}")
                for i, psn in enumerate(parsedData.psn_list, 1):
                    log.info(f"  PSN{i}: {psn}")
                
                # Hiển thị parsed data trên UI
                self.logMessage.emit("PARSED DATA:", "SUCCESS")
                self.logMessage.emit(f"  MO: {parsedData.mo}", "INFO")
                self.logMessage.emit(f"  Panel: {parsedData.panel_no}", "INFO")
                for i, psn in enumerate(parsedData.psn_list, 1):
                    self.logMessage.emit(f"  PSN{i}: {psn}", "INFO")
            else:
                log.warning("Could not parse as PSN response (format may differ)")
                self.logMessage.emit("(Could not parse as PSN format)", "WARNING")
        except Exception as e:
            log.warning(f"Parse attempt failed: {str(e)}")
            self.logMessage.emit(f"(Parse attempt failed: {str(e)})", "WARNING")
    
    def onDataParsed(self, sfisData):
        """Xử lý khi dữ liệu đã được parse thành công"""
        self.logMessage.emit("Parse SFIS data successfully", "SUCCESS")
        self.logMessage.emit(f"  Laser SN: {sfisData.laser_sn}", "INFO")
        self.logMessage.emit(f"  Security Code: {sfisData.security_code}", "INFO")
        self.logMessage.emit(f"  Status: {sfisData.status}", "INFO")
        
        # Emit signal để MainPresenter xử lý tiếp
        self.dataReady.emit(sfisData)
    
    def onError(self, errorMsg):
        """Xử lý lỗi từ SFIS Worker"""
        self.logMessage.emit(f"SFIS Error: {errorMsg}", "ERROR")
    
    def onValidationError(self, errorMsg):
        """Xử lý lỗi validation từ Model"""
        self.logMessage.emit(f"Validation Error: {errorMsg}", "ERROR")
    
    def onConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối thay đổi"""
        self.isConnected = isConnected
        status = "Đã kết nối" if isConnected else "Ngắt kết nối"
        self.logMessage.emit(f"SFIS: {status}", "INFO")
        
        # Emit signal để MainPresenter cập nhật UI
        self.connectionStatusChanged.emit(isConnected)
    
    def onStartSignalSent(self, success, message):
        """Xử lý khi START signal đã được gửi"""
        if success:
            log.info("START signal sent successfully")
            self.logMessage.emit("START signal sent successfully", "SUCCESS")
            
            # Bắt đầu nhận dữ liệu từ SFIS
            log.info("Starting to receive PSN data from SFIS...")
            self.logMessage.emit("Waiting for PSN data from SFIS...", "INFO")
            self.receiveResponsePsn()
        else:
            log.error(f"START signal failed: {message}")
            self.logMessage.emit(f"START signal sent failed: {message}", "ERROR")
        
        # Emit signal để MainPresenter biết
        self.startSignalSent.emit(success, message)
    
    def receiveResponsePsn(self):
        """
        Nhận TẤT CẢ dữ liệu từ SFIS sau khi gửi START signal
        Không giới hạn format hay độ dài, đọc tất cả có sẵn
        """
        try:
            log.info("=" * 70)
            log.info("Starting to receive data from SFIS...")
            log.info("Reading ALL available data (no format restriction)")
            
            # Đọc TẤT CẢ dữ liệu có sẵn từ COM port (timeout 10s)
            self.logMessage.emit("Waiting for data from SFIS...", "INFO")
            
            # Gọi read_data_all để đọc tất cả (không giới hạn độ dài)
            QMetaObject.invokeMethod(
                self.sfis_worker,
                "read_data_all",
                Qt.QueuedConnection,
                Q_ARG(int, 10000)  # 10 seconds timeout
            )
            
            log.info("Read request sent to worker (reading all available data)")
            log.info("=" * 70)
            
        except Exception as e:
            error_msg = f"Error receiving data from SFIS: {str(e)}"
            log.error(error_msg)
            log.debug("Exception details:", exc_info=True)
            self.logMessage.emit(error_msg, "ERROR")
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        log.info("SFISPresenter.cleanup() called")
        
        if self.isConnected:
            self.sfis_worker.disconnect()
        
        # Dừng thread
        self.sfis_thread.quit()
        self.sfis_thread.wait()
        
        log.info("SFISPresenter cleanup completed")

