"""
Project Presenter - Xử lý logic quản lý project (CRUD operations)
Tách riêng từ TopTopPresenter để tuân thủ Single Responsibility Principle
"""
import json
import os
from PySide6.QtCore import Signal, QThread
from presenter.base_presenter import BasePresenter
from workers.project_worker import ProjectWorker
from utils.Logging import getLogger
from utils.AppPathService import getAppDirectory

# Khởi tạo logger
log = getLogger()


class ProjectPresenter(BasePresenter):
    """Presenter xử lý CRUD operations cho project data"""
    
    # Signals
    projectDataLoaded = Signal(list)  # Dữ liệu project đã load
    projectUpdated = Signal(str)  # Project đã được update (project_name)
    projectDeleted = Signal(str)  # Project đã được xóa (project_name)
    projectAdded = Signal(str)  # Project mới đã được thêm (project_name)
    
    def __init__(self):
        super().__init__()
        
        # Đường dẫn appdata
        exe_dir = getAppDirectory()
        self.appdata_path = os.getenv("APPDATA")
        self.app_folder = os.path.join(self.appdata_path, "Regilazi")
        self.model_json_path = os.path.join(self.app_folder, "model.json")
        self.default_model_path = os.path.join(exe_dir, "default_model.json")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.app_folder, exist_ok=True)
        
        # Dữ liệu project
        self.project_data = []
        self.project_names = []
        
        # Khởi tạo QThread worker
        self.project_worker = ProjectWorker(self.model_json_path)
        self.project_thread = QThread()
        self.project_worker.moveToThread(self.project_thread)
        
        # Kết nối signals
        self._connectWorkerSignals()
        
        # Khởi động thread
        self.project_thread.start()
        
        # Load dữ liệu ngay khi khởi tạo
        self.loadProjectDataImmediate()
        
        log.info("ProjectPresenter initialized successfully")
    
    def _connectWorkerSignals(self):
        """Kết nối signals từ ProjectWorker"""
        self.project_worker.dataLoaded.connect(self.onProjectDataLoaded)
        self.project_worker.error.connect(self.onProjectError)
        self.project_worker.progress.connect(self.onProjectProgress)
        self.project_worker.projectUpdated.connect(self.onProjectUpdatedSuccess)
        self.project_worker.projectDeleted.connect(self.onProjectDeletedSuccess)
    
    def onProjectDataLoaded(self, data):
        """Xử lý khi dữ liệu project được load thành công"""
        try:
            self.project_data = data
            
            # Trích xuất danh sách Project_Name
            self.project_names = []
            for item in self.project_data:
                project_name = item.get("Project_Name", "")
                if project_name and project_name not in self.project_names:
                    self.project_names.append(project_name)
            
            # Emit signal
            self.projectDataLoaded.emit(self.project_data)
            
            self.show_success(f"Loaded {len(self.project_data)} projects")
            log.info(f"ProjectPresenter: Loaded {len(self.project_data)} projects")
            
        except Exception as e:
            self.show_error(f"Error processing project data: {str(e)}")
            log.error(f"ProjectPresenter: Error processing project data: {str(e)}")
    
    def onProjectError(self, error_msg):
        """Xử lý lỗi từ worker"""
        self.show_error(f"{error_msg}")
        log.error(f"ProjectPresenter: {error_msg}")
    
    def onProjectProgress(self, progress_msg):
        """Xử lý tiến trình từ worker"""
        self.show_info(progress_msg)
        log.info(f"ProjectPresenter: {progress_msg}")
    
    def onProjectUpdatedSuccess(self, project_name):
        """Xử lý khi project được update thành công"""
        self.projectUpdated.emit(project_name)
        self.show_success(f"Project '{project_name}' updated successfully")
        log.info(f"ProjectPresenter: Project '{project_name}' updated successfully")
    
    def onProjectDeletedSuccess(self, project_name):
        """Xử lý khi project được xóa thành công"""
        self.projectDeleted.emit(project_name)
        self.show_success(f"Project '{project_name}' deleted successfully")
        log.info(f"ProjectPresenter: Project '{project_name}' deleted successfully")
    
    # ==================== Public Methods ====================
    
    def loadProjectData(self):
        """Load dữ liệu project từ file JSON"""
        try:
            log.info(f"ProjectPresenter: Loading project data from {self.model_json_path}")
            
            if self.project_thread.isRunning():
                # Emit signal để trigger worker
                self.project_worker.loadRequested.emit()
            else:
                log.error("ProjectPresenter: Project worker thread is not running")
                self.show_error("Project worker thread is not running")
                # Fallback: load synchronously
                self.loadProjectDataSync()
                
        except Exception as e:
            error_msg = f"Error loading project data: {str(e)}"
            self.show_error(error_msg)
            log.error(f"ProjectPresenter: {error_msg}")
            # Fallback: load synchronously
            self.loadProjectDataSync()
    
    def loadProjectDataSync(self):
        """Load dữ liệu synchronously (fallback)"""
        try:
            log.info("ProjectPresenter: Loading project data synchronously")
            
            if not os.path.exists(self.model_json_path):
                self.show_error(f"Project data file not found: {self.model_json_path}")
                return
            
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Process data directly
            self.onProjectDataLoaded(data)
            
        except Exception as e:
            error_msg = f"Error loading project data synchronously: {str(e)}"
            log.error(f"ProjectPresenter: {error_msg}")
            self.show_error(error_msg)
    
    def loadProjectDataImmediate(self):
        """Load dữ liệu ngay lập tức trong main thread"""
        try:
            if os.path.exists(self.model_json_path):
                log.info(f"ProjectPresenter: Loading project data immediately from {self.model_json_path}")
                with open(self.model_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Process data directly
                self.onProjectDataLoaded(data)
            else:
                log.warning("ProjectPresenter: Project data file does not exist for immediate load")
                
        except Exception as e:
            error_msg = f"Error loading project data immediately: {str(e)}"
            log.error(f"ProjectPresenter: {error_msg}")
            self.show_error(error_msg)
    
    def getProjectData(self):
        """Lấy toàn bộ dữ liệu project"""
        return self.project_data
    
    def getProjectNames(self):
        """Lấy danh sách tất cả project names"""
        return self.project_names
    
    def getProjectInfo(self, project_name):
        """Lấy thông tin chi tiết của project"""
        try:
            for item in self.project_data:
                if item.get("Project_Name") == project_name:
                    return item
            return None
        except Exception as e:
            self.show_error(f"Error getting project info: {str(e)}")
            log.error(f"Error getting project info: {str(e)}")
            return None
    
    def updateProject(self, project_data):
        """Update project data trong model.json"""
        try:
            project_name = project_data.get("Project_Name", "")
            log.info(f"ProjectPresenter: Updating project '{project_name}'")
            
            # Validate project data
            if not project_name:
                self.show_error("Project name cannot be empty")
                return False
            
            # Call worker to update project
            self.project_worker.updateProject(project_data)
            
            return True
        except Exception as e:
            error_msg = f"Error updating project: {str(e)}"
            log.error(f"ProjectPresenter: {error_msg}")
            self.show_error(error_msg)
            return False
    
    def deleteProject(self, project_name):
        """Delete project từ model.json"""
        try:
            log.info(f"ProjectPresenter: Deleting project '{project_name}'")
            
            # Validate
            if not project_name:
                self.show_error("Project name cannot be empty")
                return False
            
            # Check if project exists
            if project_name not in self.project_names:
                self.show_error(f"Project '{project_name}' not found")
                return False
            
            # Call worker to delete project
            self.project_worker.deleteProject(project_name)
            
            return True
        except Exception as e:
            error_msg = f"Error deleting project: {str(e)}"
            log.error(f"ProjectPresenter: {error_msg}")
            self.show_error(error_msg)
            return False
    
    def addProject(self, project_data):
        """Thêm project mới vào model.json"""
        try:
            project_name = project_data.get("Project_Name", "")
            log.info(f"ProjectPresenter: Adding new project '{project_name}'")
            
            # Validate
            if not project_name:
                self.show_error("Project name cannot be empty")
                return False
            
            # Check if project already exists
            if project_name in self.project_names:
                self.show_error(f"Project '{project_name}' already exists")
                return False
            
            # Load current data
            if not os.path.exists(self.model_json_path):
                self.show_error(f"Project data file not found: {self.model_json_path}")
                return False
            
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            
            # Add new project
            model_data.append(project_data)
            
            # Save updated data
            with open(self.model_json_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
            
            self.show_success(f"Project '{project_name}' added successfully")
            log.info(f"ProjectPresenter: Project '{project_name}' added successfully")
            
            # Reload data
            self.loadProjectDataImmediate()
            
            # Emit signal
            self.projectAdded.emit(project_name)
            
            return True
            
        except Exception as e:
            error_msg = f"Error adding project: {str(e)}"
            log.error(f"ProjectPresenter: {error_msg}")
            self.show_error(error_msg)
            return False
    
    def refreshProjectData(self):
        """Refresh dữ liệu project từ file"""
        log.info("ProjectPresenter: Refreshing project data")
        self.loadProjectData()
    
    def projectExists(self, project_name):
        """Kiểm tra xem project có tồn tại không"""
        return project_name in self.project_names
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        try:
            if hasattr(self, 'project_worker'):
                self.project_worker.stop()
            
            # Dừng thread
            if hasattr(self, 'project_thread') and self.project_thread.isRunning():
                self.project_thread.quit()
                self.project_thread.wait(3000)  # Wait up to 3 seconds
                
            log.info("ProjectPresenter: Cleanup completed")
        except Exception as e:
            log.error(f"ProjectPresenter: Cleanup error: {str(e)}")

