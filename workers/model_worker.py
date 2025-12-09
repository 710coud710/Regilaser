"""
Model Worker - QThread worker để load dữ liệu model từ appdata
"""
import json
import os
from PySide6.QtCore import QObject, Signal, QThread
from utils.Logging import getLogger

log = getLogger()


class ModelWorker(QObject):
    """Worker để load dữ liệu model trong background thread"""
    
    # Signals
    dataLoaded = Signal(list)  # Dữ liệu đã load thành công
    error = Signal(str)  # Lỗi khi load dữ liệu
    progress = Signal(str)  # Tiến trình load
    loadRequested = Signal()  # Signal để trigger load
    
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
