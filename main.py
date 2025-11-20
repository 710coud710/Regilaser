"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from presenter.main_presenter import MainPresenter
import signal


def main():
    """Khởi động ứng dụng"""
    app = QApplication(sys.argv)
    
    # Tạo main window
    window = MainWindow()
    
    # Tạo presenter và kết nối với view
    presenter = MainPresenter(window)
    
    # Khởi tạo hệ thống
    presenter.initialize()
    
    # Hiển thị window
    window.show()
    
    # Cho phép Ctrl+C tắt ứng dụng
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Chạy ứng dụng
    exit_code = app.exec()
    
    # Dọn dẹp tài nguyên trước khi thoát
    presenter.cleanup()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

