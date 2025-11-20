"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from PySide6.QtCore import QObject, Signal
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from presenter.ccd_presenter import CCDPresenter


class MainPresenter(QObject):
    """Presenter chính - điều phối toàn bộ ứng dụng"""
    
    # Signals để cập nhật UI
    logMessage = Signal(str, str)  # (message, level)
    statusChanged = Signal(str)  # Status text
    testResult = Signal(bool, str)  # (success, message)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Khởi tạo các Presenter con
        self.sfis_presenter = SFISPresenter()
        self.plc_presenter = PLCPresenter()
        self.laser_presenter = LaserPresenter()
        self.ccd_presenter = CCDPresenter()
        
        # Kết nối signals
        self.connectSignals()
        
        # Trạng thái
        self.isRunning = False
        
    def connectSignals(self):
        """Kết nối các signals giữa View và các Presenter con"""
        
        # View signals - Left Panel
        left_panel = self.main_window.getLeftPanel()
        left_panel.startClicked.connect(self.onStartClicked)
        
        # View signals - Top Panel
        top_panel = self.main_window.getTopPanel()
        top_panel.sfisChanged.connect(self.onSfisPortChanged)
        top_panel.sfisConnectRequested.connect(self.onSfisConnectRequested)
        
        # SFIS Presenter signals
        self.sfis_presenter.logMessage.connect(self.forwardLog)
        self.sfis_presenter.connectionStatusChanged.connect(self.onSfisConnectionChanged)
        self.sfis_presenter.dataReady.connect(self.onSfisDataReady)
        
        # PLC Presenter signals
        self.plc_presenter.logMessage.connect(self.forwardLog)
        
        # Laser Presenter signals
        self.laser_presenter.logMessage.connect(self.forwardLog)
        
        # CCD Presenter signals
        self.ccd_presenter.logMessage.connect(self.forwardLog)
        
        # Presenter signals to View
        self.logMessage.connect(self.updateLog)
        self.statusChanged.connect(self.updateStatusBar)
    
    def forwardLog(self, message, level):
        """Forward log từ các presenter con đến View"""
        self.logMessage.emit(message, level)
    
    def updateLog(self, message, level):
        """Cập nhật log display"""
        logDisplay = self.main_window.result_display
        if level == "INFO":
            logDisplay.addInfo(message)
        elif level == "WARNING":
            logDisplay.addWarning(message)
        elif level == "ERROR":
            logDisplay.addError(message)
        elif level == "SUCCESS":
            logDisplay.addSuccess(message)
        elif level == "DEBUG":
            logDisplay.addDebug(message)
        else:
            logDisplay.addInfo(message)
    
    def updateStatusBar(self, statusText):
        """Cập nhật status bar"""
        # TODO: Implement status bar update
        pass
    
    def initialize(self):
        """Khởi tạo kết nối và cấu hình ban đầu"""
        self.logMessage.emit("Hệ thống đang khởi động...", "INFO")
        self.logMessage.emit("Hệ thống đã sẵn sàng!", "INFO")
    
    def onSfisConnectRequested(self, shouldConnect, portName):
        """
        Xử lý yêu cầu kết nối/ngắt kết nối SFIS từ nút toggle
        
        Args:
            shouldConnect (bool): True = kết nối, False = ngắt kết nối
            portName (str): Tên COM port
        """
        topPanel = self.main_window.getTopPanel()
        
        if shouldConnect:
            # Kết nối SFIS
            success = self.sfis_presenter.connect(portName)
            topPanel.setSFISConnectionStatus(success, "Connected" if success else "Failed")
        else:
            # Ngắt kết nối SFIS
            success = self.sfis_presenter.disconnect()
            topPanel.setSFISConnectionStatus(False, "Disconnected" if success else "Error")
    
    
    def onStartClicked(self):
        """Xử lý khi nhấn nút START"""
        if self.isRunning:
            self.logMessage.emit("Hệ thống đang chạy, vui lòng đợi...", "WARNING")
            return
        
        self.logMessage.emit("=== BẮT ĐẦU QUY TRÌNH TEST ===", "INFO")
        
        # Kiểm tra kết nối SFIS
        if not self.sfis_presenter.isConnected:
            self.logMessage.emit("Chưa kết nối SFIS. Vui lòng bật SFIS trước.", "ERROR")
            return
        
        # Lấy dữ liệu từ GUI
        topPanel = self.main_window.getTopPanel()
        mo = topPanel.getMO()
        allPartsSn = topPanel.getAllPartsSN()
        
        # Bắt đầu quy trình
        self.isRunning = True
        self.startTestProcess(mo, allPartsSn)
    
    def startTestProcess(self, mo, allPartsSn):
        """
        Bắt đầu quy trình test trong QThread
        
        Args:
            mo (str): Manufacturing Order
            allPartsSn (str): ALL PARTS SN
        """
        # Bước 1: Nhận dữ liệu từ SFIS (đã chạy trong QThread của sfis_presenter)
        response = self.sfis_presenter.requestData(mo, allPartsSn)
        
        if not response:
            self.logMessage.emit("Không nhận được dữ liệu từ SFIS", "ERROR")
            self.isRunning = False
            return
        
        # Parse dữ liệu
        sfisData = self.sfis_presenter.parseResponse(response)
        
        if not sfisData:
            self.logMessage.emit("Lỗi parse dữ liệu SFIS", "ERROR")
            self.isRunning = False
            return
        
        # Data đã sẵn sàng, tiếp tục quy trình
        self.onSfisDataReady(sfisData)
    
    def onSfisDataReady(self, sfisData):
        """
        Xử lý khi dữ liệu SFIS đã sẵn sàng
        
        Args:
            sfisData (SFISData): Dữ liệu từ SFIS
        """
        self.logMessage.emit("Dữ liệu SFIS sẵn sàng", "SUCCESS")
        self.logMessage.emit(f"  Laser SN: {sfisData.laser_sn}", "INFO")
        self.logMessage.emit(f"  Security Code: {sfisData.security_code}", "INFO")
        
        # Bước 2: Laser marking
        # TODO: Implement laser marking
        # success = self.laser_presenter.markPsn("1", sfisData.security_code)
        # if not success:
        #     self.logMessage.emit("Lỗi laser marking", "ERROR")
        #     self.sfis_presenter.sendTestError(sfisData.mo, sfisData.panel_no, "LMERR1")
        #     self.isRunning = False
        #     return
        
        # Bước 3: Verify bằng CCD
        # TODO: Implement CCD verification
        # success = self.ccd_presenter.verifyCode(sfisData.security_code)
        # if not success:
        #     self.logMessage.emit("Lỗi verify CCD", "ERROR")
        #     self.sfis_presenter.sendTestError(sfisData.mo, sfisData.panel_no, "CCDERR")
        #     self.plc_presenter.sendCheckNg()
        #     self.isRunning = False
        #     return
        
        # Bước 4: Gửi kết quả thành công
        # self.sfis_presenter.sendTestComplete(sfisData.mo, sfisData.panel_no)
        # self.plc_presenter.sendLaserOk()
        # self.plc_presenter.sendCheckOk()
        
        self.isRunning = False
        self.logMessage.emit("=== KẾT THÚC QUY TRÌNH ===", "INFO")
    
    def onSfisConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối SFIS thay đổi"""
        # Trạng thái đã được cập nhật trong sfis_presenter
        pass
    
    def onSfisPortChanged(self, portName):
        """Xử lý khi thay đổi COM port SFIS"""
        self.logMessage.emit(f"SFIS port được chọn: {portName}", "INFO")
        
        # Nếu đang kết nối, cảnh báo user
        if self.sfis_presenter.isConnected:
            self.logMessage.emit("Cảnh báo: Đang kết nối SFIS. Ngắt kết nối trước khi đổi port.", "WARNING")
    
    
    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        self.logMessage.emit("Đang dọn dẹp tài nguyên...", "INFO")
        
        # Cleanup các presenter con
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.ccd_presenter.cleanup()
        
        self.logMessage.emit("Dọn dẹp hoàn tất", "INFO")

