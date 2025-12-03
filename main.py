"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from presenter.main_presenter import MainPresenter
from utils.Logging import getLogger
import signal

# Khởi tạo logger
log = getLogger()


def main():
    log.info("--------------------------------- Regilazi Laser Marking System started ---------------------------------")
    app = QApplication(sys.argv) # Khởi tạo application
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
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

