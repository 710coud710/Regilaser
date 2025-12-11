"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from re import L
from PySide6.QtCore import Signal
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from presenter.toptop_presenter import TopTopPresenter
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
from utils.setting import settings_manager
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
        self.toptop_presenter = TopTopPresenter()
        self.setting_window = None
        self.about_window = None
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
        self.main_window.setting_clicked.connect(self.onSettingClicked)
        self.main_window.about_clicked.connect(self.onAboutClicked)
        # self.main_window.sendPLCPOK_clicked.connect(self.onSendPLCPOK)
        # self.main_window.sendPLCNG_clicked.connect(self.onSendPLCNG)

        self.main_window.sendActivateSFIS_clicked.connect(self.onSendActivateSFIS)
        self.main_window.sendNeedPSN_clicked.connect(self.onSendNEEDPSNManual)
        self.main_window.project_clicked.connect(self.onProjectClicked)
        # View signals - TopTop Panel (Model Selection)
        top_top_panel = self.main_window.getTopTopPanel()
        top_top_panel.modelChanged.connect(self.onModelChanged)
        
        # View signals - Bottom Status Bar (Connection Control)
        bottom_status = self.main_window.getBottomStatus()
        bottom_status.sfisChanged.connect(self.onSfisPortChanged)
        bottom_status.sfisConnectRequested.connect(self.onSfisConnectRequested)
        bottom_status.plcChanged.connect(self.onPlcPortChanged)
        bottom_status.plcConnectRequested.connect(self.onPlcConnectRequested)
        bottom_status.laserConnectRequested.connect(self.onLaserConnectRequested)
        
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
        
        # TopTop Presenter signals
        self.toptop_presenter.logMessage.connect(self.forwardLog)
        self.toptop_presenter.modelChanged.connect(self.onModelChangedFromPresenter)
        
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
        topPanel = self.main_window.getTopPanel()
        bottomStatus = self.main_window.getBottomStatus()
        
        # Set initial status
        topPanel.setLaserConnectionStatus(False, "Initializing...")
        bottomStatus.setLaserConnectionStatus(False, "Initializing...")
        
        # Tự động kết nối SFIS, PLC và laser (chạy song song với QTimer)
        self.laser_presenter.startAutoConnectLaser()
        self.sfis_presenter.startAutoConnectSFIS()
        self.plc_presenter.startAutoConnectPLC()
        self.plc_presenter.startReceiverPLC()

        self.show_info(f"[_______SYSTEM IS READY!_______]")
        log.info("[_______SYSTEM IS READY!_______]")

    def onSfisConnectRequested(self, shouldConnect, portName):
        """Xử lý yêu cầu kết nối/ngắt kết nối SFIS từ nút toggle"""
        topPanel = self.main_window.getTopPanel()
        bottomStatus = self.main_window.getBottomStatus()
        
        if shouldConnect:
            # Kết nối SFIS
            success = self.sfis_presenter.connect(portName)
            log.info(f"SFIS connected on port: {portName}")
            topPanel.setSFISConnectionStatus(success, "Connected" if success else "Failed")
            bottomStatus.setSFISConnectionStatus(success, "Connected" if success else "Failed")
        else:
            # Ngắt kết nối SFIS
            success = self.sfis_presenter.disconnect()
            log.info(f"SFIS disconnected on port: {portName}")
            topPanel.setSFISConnectionStatus(False, "Disconnected" if success else "Error")
            bottomStatus.setSFISConnectionStatus(False, "Disconnected" if success else "Error")
    
    
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
                if self.startMarkingLaserProcess():
                    self.plc_presenter.sendPLC_OK()
                    log.info("=========MARKING LASER PROCESS SUCCESSFULLY=========")
                    self.show_success("=========MARKING LASER PROCESS SUCCESSFULLY=========")
                    return True
                else:
                    return False                
            else:
                log.info(f"PLC received:[{message}] --> Wrong signal cannot start")
                self.show_info(f"PLC received:[{message}] --> Wrong signal cannot start")
        except Exception as e:
            log.error(f"Error starting automation marking laser: {e}")
            self.show_error(f"Error starting automation marking laser: {e}")

    def startMarkingLaserProcess(self) -> bool:
        """Bắt đầu khắc laser trong QThread"""
        try:
            response = self.sfis_presenter.getDataFromSFIS()
            if not response:
                self.show_error("Cannot receive data from SFIS")
                log.error("Cannot receive data from SFIS")
                self.isRunning = False
                return False
         
            #Đã Format dữ liệu từ SFIS
            content = self.laser_presenter.CreateFormatContent(response)
            if not content:
                self.show_error("Cannot create format content for laser")
                log.error("Cannot create format content for laser")
                self.isRunning = False
                return False
            # Get laser script from settings
            laser_script = settings_manager.get("connection.laser.script", 20)
            success = self.laser_presenter.startLaserMarkingProcess(script=laser_script, content=content)
            if not success:
                self.show_error("Cannot start laser marking process")
                log.error("Cannot start laser marking process")
                self.isRunning = False
                return False
            
            #Send complete to SFIS
            mo = response.mo
            panel_no = response.panel_no
            # log.info(f"Send complete to SFIS: {mo}, {panel_no}")
            post_result_sfc = settings_manager.get("general.post_result_sfc", True)
            if post_result_sfc:
                success = self.sfis_presenter.sendComplete(mo, panel_no)
                if not success:
                    self.show_error("Cannot send complete to SFIS")
                    log.error("Cannot send complete to SFIS")
                    self.isRunning = False
                    return False
                
            return True

        except Exception as e:
            log.error(f"Error starting automation marking laser: {e}")
            self.show_error(f"Error starting automation marking laser: {e}")
            self.isRunning = False
            return False
    
    def onSfisConnectionChanged(self, isConnected):
        """Cập nhật trạng thái SFIS trên cả TopPanel và BottomStatus"""
        topPanel = self.main_window.getTopPanel()
        bottomStatus = self.main_window.getBottomStatus()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setSFISConnectionStatus(isConnected, status_text)
        bottomStatus.setSFISConnectionStatus(isConnected, status_text)
    
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
        bottomStatus = self.main_window.getBottomStatus()

        if shouldConnect:
            success = self.plc_presenter.connect(portName)
            log.info(f"PLC connect request on {portName}: {success}")
            topPanel.setPLCConnectionStatus(success, "Connected" if success else "Failed")
            bottomStatus.setPLCConnectionStatus(success, "Connected" if success else "Failed")
        else:
            success = self.plc_presenter.disconnect()
            log.info(f"PLC disconnect request on {portName}: {success}")
            topPanel.setPLCConnectionStatus(False, "Disconnected" if success else "Error")
            bottomStatus.setPLCConnectionStatus(False, "Disconnected" if success else "Error")

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
        bottomStatus = self.main_window.getBottomStatus()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setPLCConnectionStatus(isConnected, status_text)
        bottomStatus.setPLCConnectionStatus(isConnected, status_text)
    
    def onLaserConnectRequested(self, shouldConnect):
        """Xử lý yêu cầu kết nối/ngắt kết nối Laser từ nút toggle"""
        if shouldConnect:
            # Kết nối Laser
            success = self.laser_presenter.connect()
            log.info(f"Laser connect request: {success}")
        else:
            # Ngắt kết nối Laser
            success = self.laser_presenter.disconnect()
            log.info(f"Laser disconnect request: {success}")

    def onLaserConnectionChanged(self, isConnected):
        """Xử lý khi trạng thái kết nối laser thay đổi"""
        topPanel = self.main_window.getTopPanel()
        bottomStatus = self.main_window.getBottomStatus()
        status_text = "Connected" if isConnected else "Disconnected"
        topPanel.setLaserConnectionStatus(isConnected, status_text)
        bottomStatus.setLaserConnectionStatus(isConnected, status_text)
        log.info(f"Laser status: {status_text}")
    
    def onModelChanged(self, project_name):
        """Xử lý khi user thay đổi project từ TopTopPanel"""
        self.show_info(f"Project selected: {project_name}")
        log.info(f"Project selected: {project_name}")
        
        # Lấy thông tin chi tiết của project
        project_info = self.toptop_presenter.getProjectInfo(project_name)
        if project_info:
            lm_script = project_info.get('LM_Script_Name')
            lm_num = project_info.get('LM_Num')
            psn_pre = project_info.get('PSN_PRE')
            
            self.show_info(f"Project details - Script: {lm_script}, LM_Num: {lm_num}, PSN_PRE: {psn_pre}")
            log.info(f"Project details - Script: {lm_script}, LM_Num: {lm_num}, PSN_PRE: {psn_pre}")
            
            # Có thể cập nhật config dựa trên project được chọn
            # Ví dụ: config.LASER_SCRIPT = lm_script
        
    def onModelChangedFromPresenter(self, project_name):
        """Xử lý khi TopTopPresenter thông báo project đã thay đổi"""
        self.show_info(f"Project updated by presenter: {project_name}")
        log.info(f"Project updated by presenter: {project_name}")
    
    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.toptop_presenter.cleanup()
        self.show_info("Cleanup sub-presenters completed")
        log.info("Cleanup sub-presenters completed")

    ###################Laser menu###################
    def onSendC2(self):
        """Handle menu 'Send C2 to LASER'"""
        fixed_command = settings_manager.get("general.raw_content", "")
        laser_script = settings_manager.get("connection.laser.script", 20)
        success = self.laser_presenter.setContent(script=laser_script, content=fixed_command) 

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

#--------------------------------File menu--------------------------------
    def onProjectClicked(self):
        """Handle menu 'Projects' - Show project table dialog"""
        log.info("Opening project table dialog")
        self.show_info("Opening project table...")
        try:
            # Get project table dialog from main window
            project_dialog = self.main_window.getProjectTableDialog()
            if project_dialog:
                # Load data from toptop presenter
                model_data = self.toptop_presenter.getModelData()
                if model_data:
                    project_dialog.set_data(model_data)
                    # Connect project selection signal
                    project_dialog.project_selected.connect(self.onProjectSelected)
                    log.info(f"Loaded {len(model_data)} projects into table")
                else:
                    self.show_warning("No project data available")
                    log.warning("No project data available")
        except Exception as e:
            self.show_error(f"Failed to open project table: {e}")
            log.error(f"Failed to open project table: {e}")
    
    def onProjectSelected(self, project_name):
        """Handle project selection from project table"""
        log.info(f"Project selected: {project_name}")
        try:
            # Change model using toptop presenter
            success = self.toptop_presenter.change_model(project_name)
            if success:
                self.show_success(f"Project changed to: {project_name}")
                log.info(f"Project successfully changed to: {project_name}")
            else:
                self.show_error(f"Failed to change project to: {project_name}")
                log.error(f"Failed to change project to: {project_name}")
        except Exception as e:
            self.show_error(f"Error changing project: {e}")
            log.error(f"Error changing project: {e}")

#--------------------------------Help menu--------------------------------
    def onAboutClicked(self):
        """Open the about window from menu."""
        if self.about_window is None:
            from gui import AboutWindow
            self.about_window = AboutWindow(self.main_window)
        self.about_window.show()
        self.about_window.raise_()
        self.about_window.activateWindow()

    def onSettingClicked(self):
        """Open the setting window from menu."""
        if self.setting_window is None:
            from gui import MainSettingWindow
            self.setting_window = MainSettingWindow(self.main_window)
        self.setting_window.show()
        self.setting_window.raise_()
        self.setting_window.activateWindow()