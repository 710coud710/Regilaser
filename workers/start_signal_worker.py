"""
Start Signal Worker - Xử lý gửi tín hiệu START đến SFIS (fire and forget)
"""
from PySide6.QtCore import QObject, Signal, QThread
import time


class StartSignalWorker(QObject):
    """Worker xử lý gửi tín hiệu START đến SFIS trong thread riêng"""
    
    # Signals
    signal_sent = Signal(bool, str)  # (success, message)
    log_message = Signal(str, str)  # (message, level)
    
    def __init__(self, sfis_worker):
        """

        Args:
            sfis_worker: SFISWorker instance để gửi dữ liệu
        """
        super().__init__()
        self.sfis_worker = sfis_worker
        self._is_running = False
    
    def send_start_signal(self, start_message):
        """
        Gửi tín hiệu START đến SFIS (không chờ phản hồi)
        
        Args:
            start_message (str): Message START cần gửi
        """
        if self._is_running:
            self.log_message.emit("Worker đang xử lý, vui lòng đợi...", "WARNING")
            return
        
        self._is_running = True
        
        try:
            self.log_message.emit("Đang gửi tín hiệu START đến SFIS...", "INFO")
            
            # Gửi tín hiệu qua COM port
            success = self.sfis_worker.send_data(start_message)
            
            if success:
                self.log_message.emit(f"Đã gửi START signal: {start_message}", "SUCCESS")
                self.signal_sent.emit(True, "START signal sent successfully")
            else:
                self.log_message.emit("Lỗi gửi START signal", "ERROR")
                self.signal_sent.emit(False, "Failed to send START signal")
                
        except Exception as e:
            error_msg = f"Exception khi gửi START signal: {str(e)}"
            self.log_message.emit(error_msg, "ERROR")
            self.signal_sent.emit(False, error_msg)
        
        finally:
            self._is_running = False
    
    def is_running(self):
        """Kiểm tra worker có đang chạy không"""
        return self._is_running

