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
        """
        Kết nối đến SFIS qua COM port
        
        Args:
            portName (str): Tên COM port
            
        Returns:
            bool: True nếu kết nối thành công
        """
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
        """
        Ngắt kết nối SFIS
        
        Returns:
            bool: True nếu ngắt kết nối thành công
        """
        self.logMessage.emit("Đang ngắt kết nối SFIS...", "INFO")
        log.info("Đang ngắt kết nối SFIS...")
        
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
    
    def sendStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
        """
        Gửi tín hiệu START đến SFIS qua COM port (fire and forget)
        
        Flow:
        1. SFISModel tạo START message (49 bytes)
        2. SFISWorker gửi qua COM port trong thread riêng
        3. Không chờ phản hồi từ SFIS
        
        Format: MO(20) + Panel_Number(20) + NEEDPSN08(9) = 49 bytes
        - MO: Lấy từ config.yaml nếu không truyền vào
        - Panel Number: Để trống (20 spaces)
        - NEEDPSN08: Keyword cố định (9 bytes)
        
        Args:
            mo (str, optional): Manufacturing Order
            all_parts_no (str, optional): ALL PARTS Number (không dùng)
            panel_no (str, optional): Panel Number (không dùng)
        
        Returns:
            bool: True nếu bắt đầu gửi thành công
        """
        log.info("=" * 70)
        log.info("SFISPresenter.sendStartSignal() called")
        
        # Kiểm tra kết nối
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            log.error("SFIS not connected")
            return False
        
        # Bước 1: SFISModel tạo START message
        log.info("Step 1: Creating START message via SFISModel...")
        start_message = self.sfis_model.createStartSignal(mo, all_parts_no, panel_no)
        
        if not start_message:
            self.logMessage.emit("Lỗi tạo START signal", "ERROR")
            log.error("Failed to create START message")
            return False
        
        # Lấy MO thực tế đã dùng
        actual_mo = self.sfis_model.current_data.mo
        
        # LOG chi tiết message
        log.info("START Message created successfully:")
        log.info(f"  MO (from config): '{actual_mo}'")
        log.info(f"  Format: MO(20) + Panel(20) + NEEDPSN08(9)")
        log.info(f"  Length: {len(start_message)} bytes (expected: 49)")
        log.info(f"  Content (text): '{start_message}'")
        log.info(f"  Content (HEX): {start_message.encode('ascii').hex()}")
        log.info("=" * 70)
        
        # UI Log
        self.logMessage.emit("=" * 70, "INFO")
        self.logMessage.emit("CHUẨN BỊ GỬI START SIGNAL:", "INFO")
        self.logMessage.emit(f"  MO: {actual_mo}", "INFO")
        self.logMessage.emit(f"  Format: MO(20) + Panel(20) + NEEDPSN08(9)", "INFO")
        self.logMessage.emit(f"  Length: {len(start_message)} bytes", "INFO")
        self.logMessage.emit(f"  COM Port: {self.currentPort}", "INFO")
        self.logMessage.emit("=" * 70, "INFO")
        
        # Bước 2: Gửi qua SFISWorker trong thread riêng
        log.info("Step 2: Invoking SFISWorker to send via COM port...")
        self.logMessage.emit("Đang gửi START signal qua COM port...", "INFO")
        
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
        """Xử lý khi nhận được dữ liệu từ SFIS Worker"""
        self.logMessage.emit(f"SFIS Data: {data}", "DEBUG")
        
        # Parse dữ liệu
        parsedData = self.sfis_model.parse_response_new_format(data)
        
        if not parsedData:
            self.logMessage.emit("Lỗi parse dữ liệu SFIS", "ERROR")
    
    def onDataParsed(self, sfisData):
        """Xử lý khi dữ liệu đã được parse thành công"""
        self.logMessage.emit("Parse dữ liệu SFIS thành công", "SUCCESS")
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
            self.logMessage.emit("✓ START signal đã gửi thành công", "SUCCESS")
        else:
            log.error(f"START signal failed: {message}")
            self.logMessage.emit(f"✗ START signal gửi thất bại: {message}", "ERROR")
        
        # Emit signal để MainPresenter biết
        self.startSignalSent.emit(success, message)
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        log.info("SFISPresenter.cleanup() called")
        
        if self.isConnected:
            self.sfis_worker.disconnect()
        
        # Dừng thread
        self.sfis_thread.quit()
        self.sfis_thread.wait()
        
        log.info("SFISPresenter cleanup completed")

