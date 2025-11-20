"""
Base Presenter - Class cơ sở cho các presenter
"""
from PySide6.QtCore import QObject, Signal


class BasePresenter(QObject):
    """Base class cho tất cả các presenter"""
    
    # Common signals
    logMessage = Signal(str, str)  # (message, level)
    status_changed = Signal(str)  # Status text
    
    def __init__(self):
        super().__init__()
    
    def log_info(self, message):
        """Log thông tin"""
        self.logMessage.emit(message, "INFO")
    
    def log_success(self, message):
        """Log thành công"""
        self.logMessage.emit(message, "SUCCESS")
    
    def log_warning(self, message):
        """Log cảnh báo"""
        self.logMessage.emit(message, "WARNING")
    
    def log_error(self, message):
        """Log lỗi"""
        self.logMessage.emit(message, "ERROR")
    
    def log_debug(self, message):
        """Log debug"""
        self.logMessage.emit(message, "DEBUG")
    
    def update_status(self, status_text):
        """Cập nhật status bar"""
        self.status_changed.emit(status_text)
    
    def cleanup(self):
        """Dọn dẹp tài nguyên - override trong subclass"""
        pass

