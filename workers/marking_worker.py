from PySide6.QtCore import QObject, Signal, Slot
from utils.Logging import getLogger

log = getLogger()


class MarkingWorker(QObject):
    """Worker để xử lý marking process trong background thread"""
    
    # Signals
    statusChanged = Signal(str)  # Status changed (MARKING, COMPLETED, FAILED, ERROR)
    progressUpdate = Signal(str)  # Progress message
    finished = Signal(bool)  # Finished with success/failure
    error = Signal(str)  # Error message

    def __init__(self, sfis_presenter, laser_presenter, settings_manager):
        super().__init__()
        self.sfis_presenter = sfis_presenter
        self.laser_presenter = laser_presenter
        self.settings_manager = settings_manager
        self.is_running = False

    @Slot()
    def startMarking(self):
        """Start marking process"""
        try:
            self.is_running = True
            
            # Emit MARKING status
            self.statusChanged.emit("MARKING")
            self.progressUpdate.emit("Starting marking process...")
            log.info("Marking worker: Starting marking process")
            
            # Step 1: Get data from SFIS
            self.progressUpdate.emit("Step 1: Getting data from SFIS...")
            log.info("Marking worker: Getting data from SFIS")
            
            response = self.sfis_presenter.getDataFromSFIS()
            if not response:
                error_msg = "Cannot receive data from SFIS"
                log.error(f"Marking worker: {error_msg}")
                self.error.emit(error_msg)
                self.statusChanged.emit("FAILED")
                self.finished.emit(False)
                return
            
            self.progressUpdate.emit("Step 1: Data received from SFIS ✓")
            log.info("Marking worker: Data received from SFIS")
            
            # Step 2: Format content
            self.progressUpdate.emit("Step 2: Creating format content...")
            log.info("Marking worker: Creating format content")
            
            content = self.laser_presenter.CreateFormatContent(response)
            if not content:
                error_msg = "Cannot create format content for laser"
                log.error(f"Marking worker: {error_msg}")
                self.error.emit(error_msg)
                self.statusChanged.emit("ERROR")
                self.finished.emit(False)
                return
            
            self.progressUpdate.emit("Step 2: Format content created ✓")
            log.info("Marking worker: Format content created")
            
            # Step 3: Start laser marking
            self.progressUpdate.emit("Step 3: Starting laser marking...")
            log.info("Marking worker: Starting laser marking")
            
            laser_script = self.settings_manager.get("connection.laser.script", 20)
            success = self.laser_presenter.startLaserMarkingProcess(
                script=laser_script, 
                content=content
            )
            
            if not success:
                error_msg = "Cannot start laser marking process"
                log.error(f"Marking worker: {error_msg}")
                self.error.emit(error_msg)
                self.statusChanged.emit("FAILED")
                self.finished.emit(False)
                return
            
            self.progressUpdate.emit("Step 3: Laser marking completed ✓")
            log.info("Marking worker: Laser marking completed")
            
            # Step 4: Send complete to SFIS
            post_result_sfc = self.settings_manager.get("general.post_result_sfc", True)
            if post_result_sfc:
                self.progressUpdate.emit("Step 4: Sending complete to SFIS...")
                log.info("Marking worker: Sending complete to SFIS")
                
                mo = response.mo
                panel_no = response.panel_no
                
                success = self.sfis_presenter.sendComplete(mo, panel_no)
                if not success:
                    error_msg = "Cannot send complete to SFIS"
                    log.error(f"Marking worker: {error_msg}")
                    self.error.emit(error_msg)
                    self.statusChanged.emit("ERROR")
                    self.finished.emit(False)
                    return
                
                self.progressUpdate.emit("Step 4: Complete sent to SFIS ✓")
                log.info("Marking worker: Complete sent to SFIS")
            
            # Success
            self.progressUpdate.emit("Marking process completed successfully!")
            log.info("Marking worker: Process completed successfully")
            self.statusChanged.emit("COMPLETED")
            self.finished.emit(True)
            
        except Exception as e:
            error_msg = f"Error in marking process: {str(e)}"
            log.error(f"Marking worker: {error_msg}")
            self.error.emit(error_msg)
            self.statusChanged.emit("ERROR")
            self.finished.emit(False)
            
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop worker"""
        self.is_running = False
        log.info("Marking worker: Stopped")

