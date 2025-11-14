"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Khởi động ứng dụng"""
    app = QApplication(sys.argv)
    
    # Tạo main window
    window = MainWindow()
    window.show()
    
    # Sau này sẽ thêm presenter ở đây để quản lý logic
    # presenter = MainPresenter(window)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

