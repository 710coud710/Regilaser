"""
TopTop Presenter - Xử lý logic chọn model và quản lý model.json trong appdata
"""
import json
import os
from PySide6.QtCore import Signal, QThread
from presenter.base_presenter import BasePresenter
from workers.model_worker import ModelWorker
from utils.Logging import getLogger

# Khởi tạo logger
log = getLogger()


class TopTopPresenter(BasePresenter):
    """Presenter xử lý model selection và model.json management"""
    
    # Signals
    modelChanged = Signal(str)  # Model đã thay đổi
    modelDataLoaded = Signal(list)  # Dữ liệu model đã load
    projectNamesLoaded = Signal(list)  # Danh sách Project_Name đã load
    
    def __init__(self):
        super().__init__()
        
        # Đường dẫn appdata
        self.appdata_path = os.getenv("APPDATA")
        self.app_folder = os.path.join(self.appdata_path, "Regilazi")
        self.model_json_path = os.path.join(self.app_folder, "model.json")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.app_folder, exist_ok=True)
        
        # Model hiện tại
        self.current_model = ""  # Sẽ được set khi load data
        self.model_data = []
        self.project_names = []
        
        # Khởi tạo QThread worker
        self.model_worker = ModelWorker(self.model_json_path)
        self.model_thread = QThread()
        self.model_worker.moveToThread(self.model_thread)
        
        # Kết nối signals
        self._connectWorkerSignals()
        
        # Khởi động thread
        self.model_thread.start()
        
        # Đợi thread sẵn sàng
        import time
        time.sleep(0.1)
        
        # Khởi tạo model.json trong appdata
        self.initialize()
        # Load dữ liệu ngay lập tức (file JSON nhỏ, không cần async)
        self.loadModelDataImmediate()
        
    def initialize(self):
        """Khởi tạo model.json trong appdata nếu chưa tồn tại"""
        try:
            if os.path.exists(self.model_json_path):
                # Nếu đã tồn tại, load dữ liệu
                self.show_info(f"Model file exists in appdata: {self.model_json_path}")
                self.loadModelData()
            else:
                # Nếu chưa tồn tại, copy từ project root
                # self.copyModelJsonToAppdata()
                self.show_info(f"Model data copied to appdata: {self.model_json_path}")
        except Exception as e:
            self.show_error(f"Error initializing model.json: {str(e)}")

    def _connectWorkerSignals(self):
        """Kết nối signals từ ModelWorker"""
        self.model_worker.dataLoaded.connect(self.onModelLoaded)
        self.model_worker.error.connect(self.modelLoadedError)
        self.model_worker.progress.connect(self.modelLoadedProgress)
    
    def onModelLoaded(self, data):
        """Xử lý khi dữ liệu model được load thành công"""
        try:
            self.model_data = data
            
            # Trích xuất danh sách Project_Name
            self.project_names = []
            for item in data:
                project_name = item.get("Project_Name", "")
                if project_name and project_name not in self.project_names:
                    self.project_names.append(project_name)
            
            # Set model mặc định là project đầu tiên
            if self.project_names and not self.current_model:
                self.current_model = self.project_names[0]
            
            # Emit signals
            self.modelDataLoaded.emit(self.model_data)
            self.projectNamesLoaded.emit(self.project_names)
            
            self.show_success(f"Loaded {len(self.project_names)} project names")
            log.info(f"TopTopPresenter: Loaded {len(self.project_names)} project names")
            
        except Exception as e:
            self.show_error(f"Error processing model data: {str(e)}")
            log.error(f"TopTopPresenter: Error processing model data: {str(e)}")
    
    def modelLoadedError(self, error_msg):
        """Xử lý lỗi khi load dữ liệu model"""
        self.show_error(f"{error_msg}")
        log.error(f"{error_msg}")
    
    def modelLoadedProgress(self, progress_msg):
        """Xử lý tiến trình load dữ liệu model"""
        self.show_info(progress_msg)
        log.info(f"{progress_msg}")
    

    #ko dùng
    def copyModelJsonToAppdata(self):
        """Copy model.json từ project root vào appdata"""
        try:
            # Đường dẫn model.json trong project
            project_model_path = os.path.join(os.getcwd(), "model.json")
            
            if os.path.exists(project_model_path):
                with open(project_model_path, "r", encoding="utf-8") as source:
                    model_data = json.load(source)
                
                with open(self.model_json_path, "w", encoding="utf-8") as target:
                    json.dump(model_data, target, indent=2, ensure_ascii=False)
                
                # Load dữ liệu sau khi copy
                self.loadModelData()
                self.show_success("Model data successfully copied to appdata")
            else:
                # Tạo file model.json trống nếu không tìm thấy
                self.model_data = []
                with open(self.model_json_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
                self.show_warning("Project model.json not found, created empty model data")
                
        except Exception as e:
            self.show_error(f"Error copying model.json: {str(e)}")
            self.model_data = []
    
    def loadModelData(self):
        """Load dữ liệu từ model.json trong appdata sử dụng worker thread"""
        try:
            log.info(f"TopTopPresenter: Starting to load model data from {self.model_json_path}")
            
            if self.model_thread.isRunning():
                log.info("TopTopPresenter: Thread is running, emitting load signal")
                # Emit signal để trigger worker
                self.model_worker.loadRequested.emit()
            else:
                log.error("TopTopPresenter: Model worker thread is not running")
                self.show_error("Model worker thread is not running")
                # Fallback: load synchronously
                self.loadModelDataSync()
                
        except Exception as e:
            error_msg = f"Error starting model data load: {str(e)}"
            self.show_error(error_msg)
            log.error(f"TopTopPresenter: {error_msg}")
            # Fallback: load synchronously
            self.loadModelDataSync()
    
    def loadModelDataSync(self):
        """Load dữ liệu synchronously (fallback)"""
        try:
            log.info("TopTopPresenter: Loading model data synchronously")
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Process data directly
            self.onModelLoaded(data)
            
        except Exception as e:
            error_msg = f"Error loading model data synchronously: {str(e)}"
            log.error(f"TopTopPresenter: {error_msg}")
            self.show_error(error_msg)
    
    def loadModelDataImmediate(self):
        """Load dữ liệu ngay lập tức trong main thread"""
        try:
            if os.path.exists(self.model_json_path):
                log.info(f"TopTopPresenter: Loading model data immediately from {self.model_json_path}")
                with open(self.model_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Process data directly
                self.onModelLoaded(data)
            else:
                log.warning("TopTopPresenter: Model file does not exist for immediate load")
                
        except Exception as e:
            error_msg = f"Error loading model data immediately: {str(e)}"
            log.error(f"TopTopPresenter: {error_msg}")
            self.show_error(error_msg)
    
    def change_model(self, project_name):
        """Thay đổi model hiện tại (project name)"""
        try:
            if project_name in self.project_names:
                old_model = self.current_model
                self.current_model = project_name
                
                # Emit signal
                self.modelChanged.emit(project_name)
                
                # Log thay đổi
                self.show_info(f"Project changed from '{old_model}' to '{project_name}'")
                log.info(f"Project changed from '{old_model}' to '{project_name}'")
                
                # Lấy thông tin chi tiết của project
                project_info = self.getProjectInfo(project_name)
                if project_info:
                    self.show_info(f"Project info: LM_Script={project_info.get('LM_Script_Name')}, LM_Num={project_info.get('LM_Num')}, PSN_PRE={project_info.get('PSN_PRE')}")
                    log.info(f"Project info: LM_Script={project_info.get('LM_Script_Name')}, LM_Num={project_info.get('LM_Num')}, PSN_PRE={project_info.get('PSN_PRE')}")
                return True
            else:
                self.show_error(f"Invalid project name: {project_name}")
                return False
                
        except Exception as e:
            self.show_error(f"Error changing project: {str(e)}")
            return False
    
    def getProjectInfo(self, project_name):
        """Lấy thông tin chi tiết của project"""
        try:
            for item in self.model_data:
                if item.get("Project_Name") == project_name:
                    return item
            return None
        except Exception as e:
            self.show_error(f"Error getting project info: {str(e)}")
            return None
    
    def getProjectNames(self):
        """Lấy danh sách tất cả project names"""
        return self.project_names
    
    def wait_for_data_loaded(self, timeout_ms=5000):
        """Đợi cho đến khi dữ liệu được load xong"""
        import time
        start_time = time.time()
        while len(self.project_names) == 0 and (time.time() - start_time) * 1000 < timeout_ms:
            time.sleep(0.1)  # Sleep 100ms
        return len(self.project_names) > 0
    
    
    def getCurrentModel(self):
        """Lấy model hiện tại"""
        return self.current_model
    
    def getModelData(self):
        """Lấy toàn bộ dữ liệu model"""
        return self.model_data
    
    def getAppdataPath(self):
        """Lấy đường dẫn appdata"""
        return self.app_folder
    
    def refreshModelData(self):
        """Refresh dữ liệu model từ appdata"""
        self.loadModelData()
    
    def saveModelData(self, data):
        """Lưu dữ liệu model vào appdata"""
        try:
            with open(self.model_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.model_data = data
            self.modelDataLoaded.emit(self.model_data)
            self.show_success("Model data saved successfully")
            return True
            
        except Exception as e:
            self.show_error(f"Error saving model data: {str(e)}")
            return False
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        try:
            # Dừng worker
            if hasattr(self, 'model_worker'):
                self.model_worker.stop()
            
            # Dừng thread
            if hasattr(self, 'model_thread') and self.model_thread.isRunning():
                self.model_thread.quit()
                self.model_thread.wait(3000)  # Wait up to 3 seconds
                
            log.info("TopTopPresenter cleanup completed")
        except Exception as e:
            log.error(f"TopTopPresenter cleanup error: {str(e)}")
