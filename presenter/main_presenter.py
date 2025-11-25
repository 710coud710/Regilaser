"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from PySide6.QtCore import QObject, Signal
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from presenter.ccd_presenter import CCDPresenter
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()


class MainPresenter(QObject):
    """Presenter chính - điều phối toàn bộ ứng dụng"""
    
    # Signals để cập nhật UI
    logMessage = Signal(str, str)  # (message, level)
    statusChanged = Signal(str)  # Status text
    testResult = Signal(bool, str)  # (success, message)
    
    def __init__(self, main_window):
        super().__init__()
        log.info("MainPresenter.__init__ started")
        
        self.main_window = main_window
        
        # Khởi tạo các Presenter con
        log.info("Initializing sub-presenters...")
        self.sfis_presenter = SFISPresenter()
        self.plc_presenter = PLCPresenter()
        self.laser_presenter = LaserPresenter()
        self.ccd_presenter = CCDPresenter()       
        # Kết nối signals
        self.connectSignals()
        log.info("Signals connected")
        
        # Trạng thái
        self.isRunning = False
        
        log.info("MainPresenter initialized successfully")
        
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
        self.sfis_presenter.startSignalSent.connect(self.onStartSignalSent)
        
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
        """Forward log from sub-presenters to View"""
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
        log.info("MainPresenter.initialize() called")
        self.logMessage.emit("Hệ thống đang khởi động...", "INFO")
        log.info("System initialization completed")
        self.logMessage.emit("Hệ thống đã sẵn sàng!", "INFO")
    
    def onSfisConnectRequested(self, shouldConnect, portName):
        """Xử lý yêu cầu kết nối/ngắt kết nối SFIS từ nút toggle"""
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
        log.info("MainPresenter.onStartClicked() - START button clicked")
        
        # Kiểm tra hệ thống đang chạy
        if self.isRunning:
            log.warning("System is already running")
            self.logMessage.emit("System is already running, please wait...", "WARNING")
            return
        self.logMessage.emit("== BUTTON START CLICKED ==", "INFO")
        
        # Kiểm tra kết nối SFIS
        if not self.sfis_presenter.isConnected:
            log.error("SFIS not connected - cannot send START signal")
            self.logMessage.emit("SFIS not connected - please connect SFIS before starting", "ERROR")
            return
        
        log.info(f"SFIS connected on port: {self.sfis_presenter.currentPort}")
        
        # Đánh dấu hệ thống đang chạy
        self.isRunning = True
        
        # Flow: MainPresenter → SFISPresenter → SFISModel → SFISWorker → COM Port
        log.info("Routing to SFISPresenter.sendStartSignal()...")
        self.logMessage.emit("Preparing to send START signal...", "INFO")
        
        success = self.sfis_presenter.sendStartSignal()
        
        if not success:
            log.error("Failed to initiate START signal sending")
            self.logMessage.emit("Cannot initiate START signal sending", "ERROR")
            self.isRunning = False
            return
        
        log.info("START signal routing successful - waiting for worker callback")
        self.logMessage.emit("Command sent to worker - waiting for response...", "INFO")
    
    def startTestProcess(self, mo, allPartsSn):
        """Bắt đầu quy trình test trong QThread"""
        # Bước 1: Nhận dữ liệu từ SFIS (đã chạy trong QThread của sfis_presenter)
        response = self.sfis_presenter.requestData(mo, allPartsSn)

        if not response:
            self.logMessage.emit("Cannot receive data from SFIS", "ERROR")
            log.error("Cannot receive data from SFIS")
            self.isRunning = False
            return
        
        # Parse dữ liệu
        sfisData = self.sfis_presenter.parseResponse(response)
        
        if not sfisData:
            self.logMessage.emit("Error parsing SFIS data", "ERROR")
            log.error("Error parsing SFIS data")
            self.isRunning = False
            return
        
        # Data đã sẵn sàng, tiếp tục quy trình
        self.onSfisDataReady(sfisData)
    
    def onSfisDataReady(self, sfisData):
        """Xử lý khi dữ liệu SFIS đã sẵn sàng"""
        self.logMessage.emit("SFIS data is ready", "SUCCESS")
        self.logMessage.emit(f"  Laser SN: {sfisData.laser_sn}", "INFO")
        
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
    
    def onStartSignalSent(self, success, message):
        """Flow: SFISWorker → SFISPresenter → MainPresenter (callback này)"""
        log.info("MainPresenter.onStartSignalSent() - Callback received")
        log.info(f"Success: {success}")
        log.info(f"Message: {message}")
        
        if success:
            log.info("START signal sent successfully via COM port")
            self.logMessage.emit("START signal sent successfully via COM port", "SUCCESS")
            self.logMessage.emit(f"  Port: {self.sfis_presenter.currentPort}", "INFO")
            
            # Có thể tiếp tục các bước tiếp theo ở đây
            # Ví dụ: Chờ nhận dữ liệu từ SFIS, hoặc bắt đầu laser marking, etc.
            log.info("Next steps: Wait for SFIS response or continue process...")
        else:
            log.error(f"Failed to send START signal: {message}")
            self.logMessage.emit("=" * 70, "INFO")
            self.logMessage.emit(f"✗ Gửi START signal thất bại", "ERROR")
            self.logMessage.emit(f"  Lỗi: {message}", "ERROR")
            self.logMessage.emit("=" * 70, "INFO")
        
        # Reset trạng thái running
        self.isRunning = False
        log.info("System status reset - ready for next operation")
        log.info("=" * 70)
    
    def onSfisPortChanged(self, portName):
        """Xử lý khi thay đổi COM port SFIS"""
        self.logMessage.emit(f"SFIS port được chọn: {portName}", "INFO")
        
        # Nếu đang kết nối, cảnh báo user
        if self.sfis_presenter.isConnected:
            self.logMessage.emit("Cảnh báo: Đang kết nối SFIS. Ngắt kết nối trước khi đổi port.", "WARNING")
    
    
    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        self.logMessage.emit("Đang dọn dẹp tài nguyên...", "INFO")
        log.info("Cleaning up sub-presenters...")
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.ccd_presenter.cleanup()
        self.logMessage.emit("Dọn dẹp hoàn tất", "INFO")
        log.info("MainPresenter cleanup completed")

