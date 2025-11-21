"""
SFIS Presenter - Xử lý logic giao tiếp SFIS
"""
from PySide6.QtCore import QObject, QThread, Signal
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker
from workers.start_signal_worker import StartSignalWorker


class SFISPresenter(QObject):
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
        
        # Khởi tạo Worker và Thread cho SFIS
        self.sfis_worker = SFISWorker()
        self.sfis_thread = QThread()
        self.sfis_worker.moveToThread(self.sfis_thread)
        
        # Khởi tạo Worker và Thread cho START signal
        self.start_worker = StartSignalWorker(self.sfis_worker)
        self.start_thread = QThread()
        self.start_worker.moveToThread(self.start_thread)
        
        # Kết nối signals
        self.connectSignals()
        
        # Khởi động threads
        self.sfis_thread.start()
        self.start_thread.start()
        
        # Trạng thái
        self.isConnected = False
        self.currentPort = None
    
    def connectSignals(self):
        """Kết nối signals giữa Worker và Model"""
        # SFIS Worker signals
        self.sfis_worker.data_received.connect(self.onDataReceived)
        self.sfis_worker.error_occurred.connect(self.onError)
        self.sfis_worker.connection_status_changed.connect(self.onConnectionChanged)
        
        # START Signal Worker signals
        self.start_worker.signal_sent.connect(self.onStartSignalSent)
        self.start_worker.log_message.connect(self.onStartWorkerLog)
        
        # SFIS Model signals
        self.sfis_model.data_parsed.connect(self.onDataParsed)
        self.sfis_model.validation_error.connect(self.onValidationError)
    
    def connect(self, portName):
        """
        Kết nối đến SFIS
        
        Args:
            portName (str): Tên COM port
            
        Returns:
            bool: True nếu kết nối thành công
        """
        self.logMessage.emit(f"Đang kết nối SFIS qua {portName}...", "INFO")
        
        success = self.sfis_worker.connect(portName)
        
        if success:
            self.currentPort = portName
            self.logMessage.emit(f"Kết nối SFIS thành công: {portName}", "SUCCESS")
        else:
            self.logMessage.emit(f"Kết nối SFIS thất bại: {portName}", "ERROR")
        
        return success
    
    def disconnect(self):
        """
        Ngắt kết nối SFIS
        
        Returns:
            bool: True nếu ngắt kết nối thành công
        """
        self.logMessage.emit("Đang ngắt kết nối SFIS...", "INFO")
        
        success = self.sfis_worker.disconnect()
        
        if success:
            self.currentPort = None
            self.logMessage.emit("Ngắt kết nối SFIS thành công", "INFO")
        else:
            self.logMessage.emit("Lỗi ngắt kết nối SFIS", "ERROR")
        
        return success
    
    def requestData(self, mo=None, allPartsSn=None):
        """
        Yêu cầu dữ liệu từ SFIS
        
        Args:
            mo (str): Manufacturing Order (optional)
            allPartsSn (str): ALL PARTS SN (optional)
            
        Returns:
            str: Dữ liệu nhận được, hoặc None nếu lỗi
        """
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            return None
        
        self.logMessage.emit("Đang chờ dữ liệu từ SFIS...", "INFO")
        
        # Đọc dữ liệu với timeout 5s
        response = self.sfis_worker.read_data(expected_length=70, timeout_ms=5000)
        
        if response:
            self.logMessage.emit(f"Nhận dữ liệu từ SFIS: {response}", "DEBUG")
            return response
        else:
            self.logMessage.emit("Timeout hoặc không nhận được dữ liệu từ SFIS", "ERROR")
            return None
    
    def sendStartSignal(self, mo, all_parts_no, panel_no):
        """
        Gửi tín hiệu START đến SFIS (fire and forget - không chờ phản hồi)
        Chạy trong QThread riêng
        
        Args:
            mo (str): Manufacturing Order
            all_parts_no (str): ALL PARTS Number
            panel_no (str): Panel Number
            
        Returns:
            bool: True nếu bắt đầu gửi thành công
        """
        if not self.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS", "ERROR")
            return False
        
        # Validate dữ liệu
        valid_mo, msg_mo = self.sfis_model.validateMo(mo)
        if not valid_mo:
            self.logMessage.emit(f"Validation error: {msg_mo}", "ERROR")
            return False
        
        valid_parts, msg_parts = self.sfis_model.validateAllPartsNo(all_parts_no)
        if not valid_parts:
            self.logMessage.emit(f"Validation error: {msg_parts}", "ERROR")
            return False
        
        valid_panel, msg_panel = self.sfis_model.validatePanelNo(panel_no)
        if not valid_panel:
            self.logMessage.emit(f"Validation error: {msg_panel}", "ERROR")
            return False
        
        # Tạo START signal
        start_message = self.sfis_model.createStartSignal(mo, all_parts_no, panel_no)
        
        if not start_message:
            self.logMessage.emit("Lỗi tạo START signal", "ERROR")
            return False
        
        # Gửi signal trong thread riêng (fire and forget)
        self.logMessage.emit("Bắt đầu gửi START signal...", "INFO")
        QThread.currentThread().msleep(10)  # Đảm bảo thread sẵn sàng
        
        # Invoke worker method trong thread của nó
        from PySide6.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self.start_worker,
            "send_start_signal",
            Qt.QueuedConnection,
            Q_ARG(str, start_message)
        )
        
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
            self.logMessage.emit("START signal đã gửi thành công", "SUCCESS")
        else:
            self.logMessage.emit(f"START signal gửi thất bại: {message}", "ERROR")
        
        # Emit signal để MainPresenter biết
        self.startSignalSent.emit(success, message)
    
    def onStartWorkerLog(self, message, level):
        """Forward log từ StartSignalWorker"""
        self.logMessage.emit(message, level)
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.isConnected:
            self.sfis_worker.disconnect()
        
        # Dừng các threads
        self.sfis_thread.quit()
        self.sfis_thread.wait()
        
        self.start_thread.quit()
        self.start_thread.wait()

