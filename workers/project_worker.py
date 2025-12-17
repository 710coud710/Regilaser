"""
Model Worker - QThread worker để load dữ liệu model từ appdata
"""
import json
import os
from PySide6.QtCore import QObject, Signal, QThread
from utils.Logging import getLogger

log = getLogger()


class ProjectWorker(QObject):
    """Worker để load dữ liệu model trong background thread"""
    
    # Signals
    dataLoaded = Signal(list)  # Dữ liệu đã load thành công
    error = Signal(str)  # Lỗi khi load dữ liệu
    progress = Signal(str)  # Tiến trình load
    loadRequested = Signal()  # Signal để trigger load
    projectUpdated = Signal(str)  # Project đã được update thành công
    projectDeleted = Signal(str)  # Project đã được xóa thành công
    
    def __init__(self, model_json_path):
        super().__init__()
        self.model_json_path = model_json_path
        self.is_running = False
        
        # Connect internal signal
        self.loadRequested.connect(self.loadModelData)
    
    def loadModelData(self):
        """Load dữ liệu model từ file JSON"""
        try:
            self.is_running = True
            self.progress.emit("Loading model data...")
            log.info(f"Loading data from {self.model_json_path}")
            
            if not os.path.exists(self.model_json_path):
                self.error.emit(f"File not found: {self.model_json_path}")
                return
            
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            
            if not isinstance(model_data, list):
                self.error.emit("Invalid data format - expected list")
                return
            
            self.progress.emit(f"Loaded {len(model_data)} model entries")
            log.info(f"Successfully loaded {len(model_data)} model entries")
            
            # Emit dữ liệu đã load
            self.dataLoaded.emit(model_data)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            log.error(f"{error_msg}")
            self.error.emit(error_msg)
            
        except Exception as e:
            error_msg = f"Error loading model data: {str(e)}"
            log.error(f"{error_msg}")
            self.error.emit(error_msg)
            
        finally:
            self.is_running = False
    
    def stop(self):
        """Dừng worker"""
        self.is_running = False
    
    def updateProject(self, project_data):
        """Update project data in JSON file"""
        try:
            self.progress.emit("Updating project data...")
            log.info(f"Updating project: {project_data.get('Project_Name', '')}")
            
            if not os.path.exists(self.model_json_path):
                self.error.emit(f"File not found: {self.model_json_path}")
                return
            
            # Load existing data
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            
            if not isinstance(model_data, list):
                self.error.emit("Invalid data format - expected list")
                return
            
            # Find and update the project
            project_name = project_data.get("Project_Name", "")
            updated = False
            for i, item in enumerate(model_data):
                if item.get("Project_Name") == project_name:
                    model_data[i] = project_data
                    updated = True
                    break
            
            if not updated:
                self.error.emit(f"Project not found: {project_name}")
                return
            
            # Save updated data
            with open(self.model_json_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
            
            self.progress.emit(f"Project updated: {project_name}")
            log.info(f"Successfully updated project: {project_name}")
            
            # Emit success signal
            self.projectUpdated.emit(project_name)
            # Reload data
            self.dataLoaded.emit(model_data)
            
        except Exception as e:
            error_msg = f"Error updating project: {str(e)}"
            log.error(error_msg)
            self.error.emit(error_msg)
    
    def deleteProject(self, project_name):
        """Delete project from JSON file"""
        try:
            self.progress.emit("Deleting project data...")
            log.info(f"Deleting project: {project_name}")
            
            if not os.path.exists(self.model_json_path):
                self.error.emit(f"File not found: {self.model_json_path}")
                return
            
            # Load existing data
            with open(self.model_json_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            
            if not isinstance(model_data, list):
                self.error.emit("Invalid data format - expected list")
                return
            
            # Find and delete the project
            initial_count = len(model_data)
            model_data = [item for item in model_data if item.get("Project_Name") != project_name]
            
            if len(model_data) == initial_count:
                self.error.emit(f"Project not found: {project_name}")
                return
            
            # Save updated data
            with open(self.model_json_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)
            
            self.progress.emit(f"Project deleted: {project_name}")
            log.info(f"Successfully deleted project: {project_name}")
            
            # Emit success signal
            self.projectDeleted.emit(project_name)
            # Reload data
            self.dataLoaded.emit(model_data)
            
        except Exception as e:
            error_msg = f"Error deleting project: {str(e)}"
            log.error(error_msg)
            self.error.emit(error_msg)
