"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from presenter.main_presenter import MainPresenter
from utils.Logging import getLogger
from utils.SingleInstance import get_single_instance
import signal

# Khởi tạo logger
log = getLogger()


def main():
    log.info("--------------------------------- Regilaser Laser Marking System started ---------------------------------")
    single_instance = get_single_instance("Regilaser")
    
    if not single_instance.try_lock():
        log.warning("Another instance of Regilaser is already running")
        single_instance.show_already_running_message()
        sys.exit(1)
    
    try:
        log.info("Single instance lock acquired successfully")
        
        # Khởi tạo QApplication sau khi đã có lock
        app = QApplication(sys.argv)
        
        # Khởi tạo ứng dụng
        window = MainWindow() # Khởi tạo window
        presenter = MainPresenter(window) # Khởi tạo presenter
        presenter.initialize() # Khởi tạo kết nối và cấu hình ban đầu
        window.show() # Hiển thị window
        signal.signal(signal.SIGINT, signal.SIG_DFL) 
        
        # Chạy ứng dụng và lấy exit code
        exit_code = app.exec()
        log.info("Application closing...............!!!")
        presenter.cleanup()
        log.info("--------------------------------- Application exited successfully ---------------------------------")
        
    finally:
        # Đảm bảo unlock khi thoát
        single_instance.unlock()    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

