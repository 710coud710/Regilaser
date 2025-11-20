"""
SFIS Presenter - Xử lý logic giao tiếp SFIS
"""
from PySide6.QtCore import QObject, QThread, Signal
from model.sfis_model import SFISModel
from workers.sfis_worker import SFISWorker


class SFISPresenter(QObject):
    """Presenter xử lý SFIS communication"""
    
    # Signals
    logMessage = Signal(str, str)  # (message, level)
    connectionStatusChanged = Signal(bool)  # Trạng thái kết nối
    dataReady = Signal(object)  # SFISData đã sẵn sàng
    
    def __init__(self):
        super().__init__()
        
        # Khởi tạo Model
        self.sfis_model = SFISModel()
        
        # Khởi tạo Worker và Thread
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
    
    def connectSignals(self):
        """Kết nối signals giữa Worker và Model"""
        # SFIS Worker signals
        self.sfis_worker.data_received.connect(self.onDataReceived)
        self.sfis_worker.error_occurred.connect(self.onError)
        self.sfis_worker.connection_status_changed.connect(self.onConnectionChanged)
        
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
        
        message = self.sfis_model.create_test_complete(mo, panelNo)
        
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
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.isConnected:
            self.sfis_worker.disconnect()
        
        self.sfis_thread.quit()
        self.sfis_thread.wait()

