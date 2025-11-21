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
    """Khởi động ứng dụng"""
    log.info("=" * 70)
    log.info("Khởi động ứng dụng Regilazi Laser Marking System...")
    log.info("=" * 70)
    
    app = QApplication(sys.argv)
    log.info("QApplication initialized")
    
    # Tạo main window
    window = MainWindow()
    log.info("MainWindow created")
    
    # Tạo presenter và kết nối với view
    presenter = MainPresenter(window)
    log.info("MainPresenter initialized")
    
    # Khởi tạo hệ thống
    presenter.initialize()
    
    # Hiển thị window
    window.show()
    log.info("Application window shown - Ready for user interaction")
    
    # Cho phép Ctrl+C tắt ứng dụng
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Chạy ứng dụng
    log.info("Application event loop starting...")
    exit_code = app.exec()
    
    # Dọn dẹp tài nguyên trước khi thoát
    log.info("Application closing...")
    presenter.cleanup()
    log.info("Cleanup completed")
    log.info("=" * 70)
    log.info("Application exited successfully")
    log.info("=" * 70)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

