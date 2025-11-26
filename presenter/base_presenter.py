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
    
    def show_info(self, message, level="INFO"):
        """Log thông tin"""
        self.logMessage.emit(message, level)
    
    def show_success(self, message, level="SUCCESS"):
        """Log thành công"""
        self.logMessage.emit(message, level)
    
    def show_warning(self, message, level="WARNING"):
        """Log cảnh báo"""
        self.logMessage.emit(message, level)
    
    def show_error(self, message, level="ERROR"):
        """Log lỗi"""
        self.logMessage.emit(message, level)
    
    def show_debug(self, message, level="DEBUG"):
        """Log debug"""
        self.logMessage.emit(message, level)
    
    def update_status(self, status_text):
        """Cập nhật status bar"""
        self.status_changed.emit(status_text)
    
    def cleanup(self):
        """Dọn dẹp tài nguyên - override trong subclass"""
        pass

