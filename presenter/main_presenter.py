"""
Main Presenter - Điều phối giữa View (GUI) và các Presenter con
"""
from re import L
from PySide6.QtCore import Signal, QThread
from presenter.sfis_presenter import SFISPresenter
from presenter.plc_presenter import PLCPresenter
from presenter.laser_presenter import LaserPresenter
from presenter.toptop_presenter import TopTopPresenter
from presenter.project_presenter import ProjectPresenter
from workers.marking_worker import MarkingWorker
from PySide6.QtCore import QCoreApplication
from utils.Logging import getLogger
from presenter.base_presenter import BasePresenter
from utils.setting import settings_manager
from utils.restartApp import restartApp
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
        self.project_presenter = ProjectPresenter()
        self.setting_window = None
        self.about_window = None
        
        # Khởi tạo marking worker và thread
        self.marking_worker = MarkingWorker(
            self.sfis_presenter,
            self.laser_presenter,
            settings_manager
        )
        self.marking_thread = QThread()
        self.marking_worker.moveToThread(self.marking_thread)
        
        # Kết nối signals
        self.connectSignals()
        self._connectMarkingWorkerSignals()
        
        # Khởi động marking thread
        self.marking_thread.start()
        
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

        self.main_window.sendBOMVER_clicked.connect(self.onSendBOMVER)
        self.main_window.sendBOMVERNeedSN_clicked.connect(self.onSendBOMVERNeedSN)
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
        
        # Project Presenter signals
        self.project_presenter.logMessage.connect(self.forwardLog)
        self.project_presenter.projectDataLoaded.connect(self.onProjectDataLoadedFromPresenter)
        self.project_presenter.projectUpdated.connect(self.onProjectUpdatedFromPresenter)
        self.project_presenter.projectDeleted.connect(self.onProjectDeletedFromPresenter)
        
        # Presenter signals to View
        self.logMessage.connect(self.updateLog)
        self.statusChanged.connect(self.updateStatusBar)
    
    def _connectMarkingWorkerSignals(self):
        """Kết nối signals từ MarkingWorker"""
        self.marking_worker.statusChanged.connect(self.onMarkingStatusChanged)
        self.marking_worker.progressUpdate.connect(self.onMarkingProgressUpdate)
        self.marking_worker.finished.connect(self.onMarkingFinished)
        self.marking_worker.error.connect(self.onMarkingError)
    
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
        # TODO: Implement status bar update
        pass
    
    def initialize(self):
        """Khởi tạo kết nối và cấu hình ban đầu""" 
        topPanel = self.main_window.getTopPanel()
        bottomStatus = self.main_window.getBottomStatus()
        centerPanel = self.main_window.getCenterPanel()
        leftPanel = self.main_window.getLeftPanel()
        
        # Set initial status
        topPanel.setLaserConnectionStatus(False, "Initializing...")
        bottomStatus.setLaserConnectionStatus(False, "Initializing...")
        
        # Set center panel to STANDBY
        centerPanel.setStatus(centerPanel.STANDBY)
        
        # Reset timer
        leftPanel.resetTimer()
        
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
    
    def startAutomationMarkingLaser(self, message):
        try:
            if message == "Ready" or "READY":
                log.info(f"PLC received:[{message}] --> start marking process")
                self.show_info(f"PLC received:[{message}] --> start marking process")
                log.info(f"=========START AUTOMATION MARKING LASER=========")
                self.show_info(f"=========START AUTOMATION MARKING LASER=========")
                
                # Check if already running
                if self.isRunning:
                    log.warning("Marking process already running")
                    self.show_warning("Marking process already running, please wait...")
                    return False
                
                # Mark as running
                self.isRunning = True
                
                # Start timer
                left_panel = self.main_window.getLeftPanel()
                left_panel.startTimer()
                
                # Start marking in worker thread
                from PySide6.QtCore import QMetaObject, Qt
                QMetaObject.invokeMethod(
                    self.marking_worker,
                    "startMarking",
                    Qt.QueuedConnection
                )
                
                return True
            else:
                log.info(f"PLC received:[{message}] --> Wrong signal cannot start")
                self.show_info(f"PLC received:[{message}] --> Wrong signal cannot start")
                return False
        except Exception as e:
            log.error(f"Error starting automation marking laser: {e}")
            self.show_error(f"Error starting automation marking laser: {e}")
            self.isRunning = False
            return False
    
    def _resetToStandby(self):
        """Reset system to STANDBY state"""
        try:
            center_panel = self.main_window.getCenterPanel()
            left_panel = self.main_window.getLeftPanel()
            
            center_panel.setStatus(center_panel.STANDBY)
            left_panel.resetTimer()
            
            log.info("System reset to STANDBY")
        except Exception as e:
            log.error(f"Error resetting to standby: {e}")
    
    def onMarkingStatusChanged(self, status):
        """Handle status change from marking worker"""
        try:
            center_panel = self.main_window.getCenterPanel()
            center_panel.setStatus(status)
            log.info(f"Status changed to: {status}")
        except Exception as e:
            log.error(f"Error handling status change: {e}")
    
    def onMarkingProgressUpdate(self, message):
        """Handle progress update from marking worker"""
        self.show_info(message)
        log.info(f"Progress: {message}")
    
    def onMarkingFinished(self, success):
        """Handle marking process finished"""
        try:
            left_panel = self.main_window.getLeftPanel()
            left_panel.stopTimer()
            elapsed = left_panel.getElapsedTime()
            
            if success:
                self.plc_presenter.sendPLC_OK()
                self.show_success(f"Marking completed successfully in {elapsed}s")
                log.info(f"=========MARKING LASER PROCESS SUCCESSFULLY in {elapsed}s=========")
            else:
                self.show_error(f"Marking failed after {elapsed}s")
                log.error(f"=========MARKING LASER PROCESS FAILED in {elapsed}s=========")
            
            # Reset to STANDBY after delay
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, self._resetToStandby)
            
            # Mark as not running
            self.isRunning = False
            
        except Exception as e:
            log.error(f"Error handling marking finished: {e}")
            self.isRunning = False
    
    def onMarkingError(self, error_msg):
        """Handle error from marking worker"""
        self.show_error(error_msg)
        log.error(f"Marking error: {error_msg}")

    
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
            panel_num = project_info.get('Panel_Num')
            psn_pre = project_info.get('PSN_PRE')
            
            self.show_info(f"Project details - Script: {lm_script}, Panel_Num: {panel_num}, PSN_PRE: {psn_pre}")
            log.info(f"Project details - Script: {lm_script}, Panel_Num: {panel_num}, PSN_PRE: {psn_pre}")
            
            # Có thể cập nhật config dựa trên project được chọn
            # Ví dụ: config.LASER_SCRIPT = lm_script
        
    def onModelChangedFromPresenter(self, project_name):
        """Xử lý khi TopTopPresenter thông báo project đã thay đổi"""
        self.show_info(f"Project updated by presenter: {project_name}")
        log.info(f"Project updated by presenter: {project_name}")
    
    def onProjectDataLoadedFromPresenter(self, project_data):
        """Xử lý khi ProjectPresenter load xong dữ liệu"""
        log.info(f"Project data loaded: {len(project_data)} projects")
    
    def onProjectUpdatedFromPresenter(self, project_name):
        """Xử lý khi ProjectPresenter update project thành công"""
        log.info(f"Project updated notification: {project_name}")
    
    def onProjectDeletedFromPresenter(self, project_name):
        """Xử lý khi ProjectPresenter delete project thành công"""
        log.info(f"Project deleted notification: {project_name}")
    


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

    def onSendBOMVER(self):
        """Handle menu 'Send BOMVER to SFIS'"""
        log.info("Send BOMVER to SFIS")
        self.show_info("Send BOMVER to SFIS")
        try:
            self.sfis_presenter.sendBOMVER()
            self.show_success("Send BOMVER to SFIS successfully")
            log.info("Send BOMVER to SFIS successfully")
        except Exception as e:
            self.show_error(f"Failed to send BOMVER to SFIS: {e}")
            log.error(f"Failed to send BOMVER to SFIS: {e}")

    def onSendBOMVERNeedSN(self):
        """Handle menu 'Send BOMVERNeedSN to SFIS'"""
        log.info("Send BOMVERNeedSN to SFIS")
        self.show_info("Send BOMVERNeedSN to SFIS")
        try:
            self.sfis_presenter.sendBOMVERNeedSN()
            self.show_success("Send BOMVERNeedSN to SFIS successfully")
            log.info("Send BOMVERNeedSN to SFIS successfully")
        except Exception as e:
            self.show_error(f"Failed to send BOMVERNeedSN to SFIS: {e}")
            log.error(f"Failed to send BOMVERNeedSN to SFIS: {e}")

#--------------------------------File menu--------------------------------
    def onProjectClicked(self):
        """Handle menu 'Projects' - Show project table dialog"""
        log.info("Opening project table dialog")
        self.show_info("Opening project table...")
        try:
            # Refresh project data trước khi hiển thị
            self.project_presenter.loadProjectDataImmediate()
            
            # Get project table dialog from main window
            project_dialog = self.main_window.getProjectTableDialog()
            if project_dialog:
                # Load data from project presenter
                project_data = self.project_presenter.getProjectData()
                if project_data:
                    project_dialog.set_data(project_data) # Set data to the table
                    # Connect project signals
                    project_dialog.project_selected.connect(self.onProjectSelected)
                    project_dialog.project_edit.connect(self.onProjectEdit)
                    project_dialog.project_delete.connect(self.onProjectDelete)
                    project_dialog.project_add.connect(self.onProjectAdd)
                    log.info(f"Loaded {len(project_data)} projects into table")
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
                restartApp()
            else:
                self.show_error(f"Failed to change project to: {project_name}")
                log.error(f"Failed to change project to: {project_name}")
        except Exception as e:
            self.show_error(f"Error changing project: {e}")
            log.error(f"Error changing project: {e}")
    
    def onProjectEdit(self, project_data):
        """Handle project edit from project table"""
        project_name = project_data.get("Project_Name", "")
        log.info(f"Editing project: {project_name}")
        try:
            # Update project using project presenter
            success = self.project_presenter.updateProject(project_data)
            if success:
                self.show_success(f"Project updated: {project_name}")
                log.info(f"Project successfully updated: {project_name}")
                
                # Refresh toptop presenter data nếu project hiện tại bị thay đổi
                current_project = self.toptop_presenter.getCurrentModel()
                if current_project == project_name:
                    self.toptop_presenter.loadModelDataImmediate()
                
                # Refresh project table
                self.onProjectClicked()
            else:
                self.show_error(f"Failed to update project: {project_name}")
                log.error(f"Failed to update project: {project_name}")
        except Exception as e:
            self.show_error(f"Error updating project: {e}")
            log.error(f"Error updating project: {e}")
    
    def onProjectDelete(self, project_name):
        """Handle project delete from project table"""
        log.info(f"Deleting project: {project_name}")
        try:
            # Check if trying to delete current project
            current_project = self.toptop_presenter.getCurrentModel()
            if current_project == project_name:
                self.show_error(f"Cannot delete current active project: {project_name}")
                log.error(f"Cannot delete current active project: {project_name}")
                return
            
            # Delete project using project presenter
            success = self.project_presenter.deleteProject(project_name)
            if success:
                self.show_success(f"Project deleted: {project_name}")
                log.info(f"Project successfully deleted: {project_name}")
                
                # Refresh toptop presenter data
                self.toptop_presenter.loadModelDataImmediate()
                
                # Refresh project table
                self.onProjectClicked()
            else:
                self.show_error(f"Failed to delete project: {project_name}")
                log.error(f"Failed to delete project: {project_name}")
        except Exception as e:
            self.show_error(f"Error deleting project: {e}")
            log.error(f"Error deleting project: {e}")
    
    def onProjectAdd(self, project_data):
        """Handle add new project from project table"""
        project_name = project_data.get("Project_Name", "")
        log.info(f"Adding new project: {project_name}")
        try:
            # Add project using project presenter
            success = self.project_presenter.addProject(project_data)
            if success:
                self.show_success(f"Project added: {project_name}")
                log.info(f"Project successfully added: {project_name}")
                
                # Refresh toptop presenter data
                self.toptop_presenter.loadModelDataImmediate()
                
                # Refresh project table
                self.onProjectClicked()
            else:
                self.show_error(f"Failed to add project: {project_name}")
                log.error(f"Failed to add project: {project_name}")
        except Exception as e:
            self.show_error(f"Error adding project: {e}")
            log.error(f"Error adding project: {e}")

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












    def cleanup(self):
        """Dọn dẹp tài nguyên khi đóng ứng dụng"""
        # Stop marking worker
        if hasattr(self, 'marking_worker'):
            self.marking_worker.stop()
        QCoreApplication.processEvents()
        QThread.msleep(50) #Đợi 50ms để đảm bảo dữ liệu được gửi đi
        # Stop marking thread
        if hasattr(self, 'marking_thread') and self.marking_thread.isRunning():
            self.marking_thread.quit()
            self.marking_thread.wait(3000)
        
        # Cleanup presenters 
        self.sfis_presenter.cleanup()
        self.plc_presenter.cleanup()
        self.laser_presenter.cleanup()
        self.toptop_presenter.cleanup()
        self.project_presenter.cleanup()
        QThread.msleep(200) #Đợi 200ms để đảm bảo dữ liệu được gửi đi

        # Stop marking thread
        if hasattr(self, 'marking_thread') and self.marking_thread.isRunning():
            self.marking_thread.quit()
            if not self.marking_thread.wait(5000):
                self.marking_thread.terminate()
                self.marking_thread.wait()

        self.show_info("Cleanup completed")
        log.info("Cleanup completed")