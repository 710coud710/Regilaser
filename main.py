"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.MainWindow import MainWindow
import signal


def main():
    """Khởi động ứng dụng"""
    app = QApplication(sys.argv)
    
    # Tạo main window
    window = MainWindow()
    window.show()
    # presenter = MainPresenter(window)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # tắt để ứng dụng ctrl+C
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

