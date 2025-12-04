"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from PySide6.QtCore import Signal
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
from config import ConfigManager

# Khởi tạo logger
log = getLogger()

config = ConfigManager().get()



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
        # Trạng thái
        self.isRunning = False
        log.info("MainPresenter initialized successfully")
        
    def connectSignals(self):
        """Kết nối các signals giữa View và các Presenter con"""
        
        # View signals - Left Panel
        left_panel = self.main_window.getLeftPanel()
        left_panel.startClicked.connect(self.onStartClicked)
        
        # Menu actions
        self.main_window.sendC2_clicked.connect(self.onSendC2)
        self.main_window.sendGA_clicked.connect(self.onSendGA)
        self.main_window.sendNT_clicked.connect(self.onSendNT)
        # self.main_window.sendPLCPOK_clicked.connect(self.onSendPLCPOK)
        # self.main_window.sendPLCNG_clicked.connect(self.onSendPLCNG)

        self.main_window.sendActivateSFIS_clicked.connect(self.onSendActivateSFIS)
        self.main_window.sendNeedPSN_clicked.connect(self.onSendNEEDPSNManual)
        # View signals - Top Panel
        top_panel = self.main_window.getTopPanel()
        top_panel.sfisChanged.connect(self.onSfisPortChanged)
        top_panel.sfisConnectRequested.connect(self.onSfisConnectRequested)
        top_panel.plcChanged.connect(self.onPlcPortChanged)
        top_panel.plcConnectRequested.connect(self.onPlcConnectRequested)
        
        # SFIS Presenter signals
        self.sfis_presenter.logMessage.connect(self.forwardLog)
        self.sfis_presenter.connectionStatusChanged.connect(self.onSfisConnectionChanged)
        self.sfis_presenter.startSignalSent.connect(self.onStartSignalSent)
        
        # PLC Presenter signals
        self.plc_presenter.logMessage.connect(self.forwardLog)
        self.plc_presenter.connectionStatusChanged.connect(self.onPlcConnectionChanged)
        # Khi PLC gửi tín hiệu READY thì tự động bắt đầu quy trình test (giống như bấm START)
        self.plc_presenter.readyReceived.connect(self.startAutomationMarkingLaser)
        
        # Laser Presenter signals
        self.laser_presenter.logMessage.connect(self.forwardLog)
        self.laser_presenter.connectionStatusChanged.connect(self.onLaserConnectionChanged)
        
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
        # Cập nhật trạng thái laser ban đầu (disconnected)
        topPanel = self.main_window.getTopPanel()
        topPanel.setLaserConnectionStatus(False, "Initializing...")
        # Tự động kết nối SFIS, PLC và laser
        self.laser_presenter.startAutoConnectLaser()
        self.sfis_presenter.startAutoConnectSFIS()
        self.plc_presenter.startAutoConnectPLC()
        self.plc_presenter.startReceiverPLC()

        self.show_info(f"[_______SYSTEM IS READY!_______]")
        log.info("[_______SYSTEM IS READY!_______]")

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
        success = self.sfis_presenter.sendNEEDPSN()
        
        if not success:
            log.error("Failed to initiate START signal sending")
            self.show_error("Cannot initiate START signal sending")
            self.isRunning = False
            return
        
        log.info("START signal sent successfully - waiting for response...")
        self.show_info("START signal sent successfully - waiting for response...")
    
    def startAutomationMarkingLaser(self,message):
        try:
            if message == "Ready" or "READY":
                log.info(f"PLC received:[{message}] --> start marking process")
                self.show_info(f"PLC received:[{message}] --> start marking process")
                log.info(f"=========START AUTOMATION MARKING LASER=========")
                self.show_info(f"=========START AUTOMATION MARKING LASER=========")
                self.startMarkingLaserProcess()
                
            else:
                log.info(f"PLC received:[{message}] --> Wrong signal cannot start")
                self.show_info(f"PLC received:[{message}] --> Wrong signal cannot start")
        except Exception as e:
            log.error(f"Error starting automation marking laser: {e}")
            self.show_error(f"Error starting automation marking laser: {e}")

    def startMarkingLaserProcess(self):
        """Bắt đầu khắc laser trong QThread"""
        #Lấy dữ liệu từ SFIS
        response = self.sfis_presenter.getDataPSNFromSFIS()

        if not response:
            self.show_error("Cannot receive data from SFIS")
            log.error("Cannot receive data from SFIS")
            self.isRunning = False
            return False
        log.info(f"Received data from SFIS: {response}")
        self.show_info(f"Received data from SFIS: {response}")
        # Parse dữ liệu
        sfisData = self.sfis_presenter.parseResponse(response)
        self.show_info(f"Parsed data from SFIS: {sfisData}")
        if not sfisData:
            self.show_error("Error parsing SFIS data")
            log.error("Error parsing SFIS data")
            self.isRunning = False
            return False
    
    def onSfisConnectionChanged(self, isConnected):
        topPanel = self.main_window.getTopPanel()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setSFISConnectionStatus(isConnected, status_text)
    
    def onStartSignalSent(self):
        """Flow: SFISWorker → SFISPresenter → MainPresenter (callback này)"""  
        self.isRunning = False
        # self.log.info("START signal sent successfully")
    
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

    #Theo dõi thay đổi COM port PLC*
    def onPlcPortChanged(self, portName): 
        self.show_info(f"PLC port selected: {portName}")
        log.info(f"PLC port selected: {portName}")
        if self.plc_presenter.is_connected:
            self.show_warning("Warning: PLC is connected. Disconnect before changing port.")
            log.warning("Warning: PLC is connected. Disconnect before changing port.")

    def onPlcConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối PLC thay đổi (cập nhật UI như bấm nút Connect)."""
        topPanel = self.main_window.getTopPanel()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setPLCConnectionStatus(isConnected, status_text)

    def onLaserConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối laser thay đổi"""
        topPanel = self.main_window.getTopPanel()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setLaserConnectionStatus(isConnected, status_text)
        log.info(f"Laser status: {status_text}")
    
    
    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.show_info("Cleanup sub-presenters completed")
        log.info("Cleanup sub-presenters completed")

    ###################Laser menu###################
    def onSendC2(self):
        """Handle menu 'Send C2 to LASER'"""
        fixed_command = config.RAW_CONTENT
        success = self.laser_presenter.setContent(script=config.LASER_SCRIPT, content=fixed_command) 

        if success:
            self.show_success("C2 command sent to laser successfully")
        else:
            self.show_error("Failed to send C2 command to laser")

    def onSendGA(self):
        try:
            self.laser_presenter.activateScript()
            self.show_success(f"Send GA to laser successfully")
            log.info(f"Send GA to laser successfully")
        except Exception as e:
            self.show_error(f"Failed to send GA to laser: {e}")
            log.error(f"Failed to send GA to laser: {e}")


    def onSendNT(self):
        """Handle menu 'Send NT to LASER'"""
        try:
            self.laser_presenter.startMarking()
            self.show_success(f"Send NT to laser successfully")
            log.info(f"Send NT to laser successfully")
        except Exception as e:
            self.show_error(f"Failed to send NT to laser: {e}")
            log.error(f"Failed to send NT to laser: {e}")

    ###################PLC menu###################
    def onSendPLCPOK(self):
        """Handle menu 'Send OK to PLC'"""
        try:
            success = self.plc_presenter.send_check_ok()
            if success:
                self.show_success("OK command sent to PLC successfully")
            else:
                self.show_error("Failed to send OK command to PLC")
        except Exception as e:
            self.show_error(f"Failed to send OK command to PLC: {e}")
            log.error(f"Failed to send OK command to PLC: {e}")
            return False

    def onSendPLCNG(self):
        """Handle menu 'Send NG to PLC'"""
        try:
            self.plc_presenter.send_check_ng()
            self.show_success("NG command sent to PLC successfully")
            log.info("NG command sent to PLC successfully")
        except Exception as e:
            self.show_error(f"Failed to send NG command to PLC: {e}")
            log.error(f"Failed to send NG command to PLC: {e}")

    ###################SFIS menu###################
    def onSendActivateSFIS(self):
        """Handle menu 'Activate SFIS'"""
        try:
            self.sfis_presenter.activateSFIS()
            self.show_success("Activate SFIS successfully")
            log.info("Activate SFIS successfully")
        except Exception as e:
            self.show_error(f"Failed to activate SFIS: {e}")
            log.error(f"Failed to activate SFIS: {e}")

    def onSendNEEDPSNManual(self):
        """Handle menu 'Send NEEDPSN to SFIS'"""
        log.info("Send NEEDPSN to SFIS manual")
        self.show_info("Send NEEDPSN to SFIS manual")
        try:
            self.sfis_presenter.sendNEEDPSN()
            self.show_success("Send NEEDPSN SFIS Manual successfully")
            log.info("Send NEEDPSN SFIS Manual successfully")
        except Exception as e:
            self.show_error(f"Failed to send NEEDPSN to SFIS: {e}")
            log.error(f"Failed to send NEEDPSN to SFIS: {e}")