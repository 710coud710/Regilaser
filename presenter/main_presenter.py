"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from PySide6.QtCore import Signal
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
# Khởi tạo logger
log = getLogger()


class MainPresenter(BasePresenter):
    """Presenter chính - điều phối toàn bộ ứng dụng"""
    
    # Signals để cập nhật UI
    logMessage = Signal(str, str)  # (message, level)
    statusChanged = Signal(str)  # Status text
    testResult = Signal(bool, str)  # (success, message)
    
    def __init__(self, main_window):
        super().__init__()        
        self.main_window = main_window
        self.sfis_presenter = SFISPresenter()
        self.plc_presenter = PLCPresenter()
        self.laser_presenter = LaserPresenter()      
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
        
        # Menu actions
        self.main_window.sendLaserPsn20_clicked.connect(self.onSendLaserPsn20)
        self.main_window.sendLaserPsn16_clicked.connect(self.onSendLaserPsn16)
        self.main_window.sendGA_clicked.connect(self.onSendGA)
        self.main_window.sendNT_clicked.connect(self.onSendNT)
        # self.main_window.sendPLCPOK_clicked.connect(self.onSendPLCPOK)
        # self.main_window.sendPLCNG_clicked.connect(self.onSendPLCNG)
        # View signals - Top Panel
        top_panel = self.main_window.getTopPanel()
        top_panel.sfisChanged.connect(self.onSfisPortChanged)
        top_panel.sfisConnectRequested.connect(self.onSfisConnectRequested)
        top_panel.plcChanged.connect(self.onPlcPortChanged)
        top_panel.plcConnectRequested.connect(self.onPlcConnectRequested)
        
        # SFIS Presenter signals
        self.sfis_presenter.logMessage.connect(self.forwardLog)
        self.sfis_presenter.connectionStatusChanged.connect(self.onSfisConnectionChanged)
        self.sfis_presenter.dataReady.connect(self.onSfisDataReady)
        self.sfis_presenter.startSignalSent.connect(self.onStartSignalSent)
        
        # PLC Presenter signals
        self.plc_presenter.logMessage.connect(self.forwardLog)
        
        # Laser Presenter signals
        self.laser_presenter.logMessage.connect(self.forwardLog)
        
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
        self.show_info("System is ready!")
        log.info("System is ready!")
    
    def onSfisConnectRequested(self, shouldConnect, portName):
        """Xử lý yêu cầu kết nối/ngắt kết nối SFIS từ nút toggle"""
        topPanel = self.main_window.getTopPanel()
        
        if shouldConnect:
            # Kết nối SFIS
            success = self.sfis_presenter.connect(portName)
            log.info(f"SFIS connected on port: {portName}")
            topPanel.setSFISConnectionStatus(success, "Connected" if success else "Failed")
        else:
            # Ngắt kết nối SFIS
            success = self.sfis_presenter.disconnect()
            log.info(f"SFIS disconnected on port: {portName}")
            topPanel.setSFISConnectionStatus(False, "Disconnected" if success else "Error")
    
    
    def onStartClicked(self):    
        log.info("START button clicked")
        
        # Check if system is already running
        if self.isRunning:
            log.warning("System is already running")
            self.show_warning("System is already running, please wait...")
            return
        self.show_info("BUTTON START CLICKED")
        
        # Check if SFIS is connected
        if not self.sfis_presenter.isConnected:
            log.error("SFIS not connected - cannot send START signal")
            self.show_error("SFIS not connected - please connect SFIS before starting")
            return
        
        log.info(f"SFIS connected on port: {self.sfis_presenter.currentPort}")
        
        # Mark system as running
        self.isRunning = True
        # Flow: MainPresenter -> SFISPresenter -> SFISModel -> SFISWorker -> COM Port
        success = self.sfis_presenter.sendStartSignal()
        
        if not success:
            log.error("Failed to initiate START signal sending")
            self.show_error("Cannot initiate START signal sending")
            self.isRunning = False
            return
        
        log.info("START signal sent successfully - waiting for response...")
        self.show_info("START signal sent successfully - waiting for response...")
    
    def startTestProcess(self, mo, panelNo):
        """Bắt đầu quy trình test trong QThread"""
        # Step 1: Request data from SFIS (running in QThread of sfis_presenter)
        response = self.sfis_presenter.requestData()

        if not response:
            self.show_error("Cannot receive data from SFIS")
            log.error("Cannot receive data from SFIS")
            self.isRunning = False
            return
        
        # Parse dữ liệu
        sfisData = self.sfis_presenter.parseResponse(response)
        
        if not sfisData:
            self.show_error("Error parsing SFIS data")
            log.error("Error parsing SFIS data")
            self.isRunning = False
            return
        
        # Data đã sẵn sàng, tiếp tục quy trình
        self.onSfisDataReady(sfisData)
    
    def onSfisDataReady(self, sfisData):
        """Xử lý khi dữ liệu SFIS đã sẵn sàng"""
        self.show_success("SFIS data is ready")
        self.show_info(f"  Laser SN: {sfisData.laser_sn}")
        
        # Bước 2: Laser marking
        # TODO: Implement laser marking
        # success = self.laser_presenter.markPsn("1", sfisData.security_code)
        # if not success:
        #     self.show_error("Lỗi laser marking")
        #     self.sfis_presenter.sendTestError(sfisData.mo, sfisData.panel_no, "LMERR1")
        #     self.isRunning = False
        #     return
                
        # Bước 4: Gửi kết quả thành công
        # self.sfis_presenter.sendTestComplete(sfisData.mo, sfisData.panel_no)
        # self.plc_presenter.sendLaserOk()
        # self.plc_presenter.sendCheckOk()
        
        self.isRunning = False
        self.show_info("=== KẾT THÚC QUY TRÌNH ===")
    
    def onSfisConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối SFIS thay đổi"""
        pass
    
    def onStartSignalSent(self, success, message):
        """Flow: SFISWorker → SFISPresenter → MainPresenter (callback này)"""
        log.info("START signal sent callback received")
        log.info(f"Success: {success}")
        log.info(f"Message: {message}")
        
        if success:
            log.info("START signal sent successfully via COM port")
            self.show_success("START signal sent successfully via COM port")
            self.show_info(f"  Port: {self.sfis_presenter.currentPort}")
            
            # Có thể tiếp tục các bước tiếp theo ở đây
            # Ví dụ: Chờ nhận dữ liệu từ SFIS, hoặc bắt đầu laser marking, etc.
            log.info("Next steps: Wait for SFIS response or continue process...")
        else:
            log.error(f"Failed to send START signal: {message}")
            self.show_error(f"Failed to send START signal: {message}")

        self.isRunning = False
    
    def onSfisPortChanged(self, portName):
        """Xử lý khi thay đổi COM port SFIS"""
        self.show_info(f"SFIS port selected: {portName}")
        log.info(f"SFIS port selected: {portName}")
        # If connected, warn user
        if self.sfis_presenter.isConnected:
            self.show_warning("Warning: SFIS is connected. Disconnect before changing port.")
            log.warning("Warning: SFIS is connected. Disconnect before changing port.")

    def onPlcConnectRequested(self, shouldConnect, portName):
        """Xử lý yêu cầu kết nối/ngắt kết nối PLC"""
        topPanel = self.main_window.getTopPanel()

        if shouldConnect:
            success = self.plc_presenter.connect(portName)
            log.info(f"PLC connect request on {portName}: {success}")
            topPanel.setPLCConnectionStatus(success, "Connected" if success else "Failed")
        else:
            success = self.plc_presenter.disconnect()
            log.info(f"PLC disconnect request on {portName}: {success}")
            topPanel.setPLCConnectionStatus(False, "Disconnected" if success else "Error")

    def onPlcPortChanged(self, portName):
        """Xử lý khi thay đổi COM port PLC"""
        self.show_info(f"PLC port selected: {portName}")
        log.info(f"PLC port selected: {portName}")
        if self.plc_presenter.is_connected:
            self.show_warning("Warning: PLC is connected. Disconnect before changing port.")
            log.warning("Warning: PLC is connected. Disconnect before changing port.")
    
    
    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.show_info("Cleanup sub-presenters completed")
        log.info("Cleanup sub-presenters completed")

    def onSendLaserPsn20(self):
        """Handle menu 'Send PSN20 to LASER'"""
        fixed_command = (
            "C2,15,0,PX5BF03TI,2,2795001670,"
            "6,PT53QG0754670375ABCD,10,PT53QG0754670376EFGH,"
            "14,PT53QG0754670377IJKL,18,PT53QG0754670378MNOP,"
            "22,PT53QG0754670379QRST"
        )

        self.show_info("Menu: Send PSN20 to LASER triggered")

        success = self.laser_presenter.send_custom_command(fixed_command,expect_keyword="C2,0")

        if success:
            self.show_success("PSN20 command sent to laser successfully")
        else:
            self.show_error("Failed to send PSN20 command to laser")



    def onSendLaserPsn16(self):
        """Handle menu 'Send PSN20 to LASER'"""
        fixed_command = (
            "C2,15,0,PX5BF03TI,2,2795001670,"
            "6,PT53QG0754670375,10,PT53QG0754670376,"
            "14,PT53QG0754670377,18,PT53QG0754670378,"
            "22,PT53QG0754670379"
        )

        self.show_info("Menu: Send PSN16 to LASER triggered")

        success = self.laser_presenter.send_custom_command(fixed_command,expect_keyword="C2,0")

        if success:
            self.show_success("PSN16 command sent to laser successfully")
        else:
            self.show_error("Failed to send PSN16 command to laser")

    def onSendPLCPOK(self):
        """Handle menu 'Send OK to PLC'"""
        success = self.plc_presenter.send_check_ok()
        if success:
            self.show_success("OK command sent to PLC successfully")
        else:
            self.show_error("Failed to send OK command to PLC")

    def onSendPLCNG(self):
        """Handle menu 'Send NG to PLC'"""
        self.plc_presenter.send_check_ng()

    def onSendGA(self):
        """Handle menu 'Send GA,05 to LASER'"""
        Script_Laser = "05"
        try:
            self.laser_presenter.sendGAtoLaser(Script_Laser)
            self.show_success("Send GA,{Script_Laser} to laser successfully")
            log.success(f"Send GA,{Script_Laser} to laser successfully")
        except Exception as e:
            self.show_error(f"Failed to send GA,{Script_Laser} to laser: {e}")
            log.error(f"Failed to send GA,{Script_Laser} to laser: {e}")


    def onSendNT(self):
        """Handle menu 'Send NT to LASER'"""
        success = self.laser_presenter.start_marking()