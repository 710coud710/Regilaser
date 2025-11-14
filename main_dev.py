"""
Development Entry Point - Main với Hot Reload
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from hot_reload import HotReloader


# Global reference để hot reload có thể truy cập
main_window = None
hot_reloader = None


def create_main_window():
    """Factory function để tạo main window"""
    return MainWindow()


def main():
    """Khởi động ứng dụng với hot reload"""
    global main_window, hot_reloader
    
    app = QApplication(sys.argv)
    
    # Tạo main window
    main_window = create_main_window()
    main_window.show()
    
    # Khởi động hot reloader
    hot_reloader = HotReloader(app, main_window, create_main_window)
    hot_reloader.start()
    
    # Sau này sẽ thêm presenter ở đây
    # presenter = MainPresenter(main_window)
    
    try:
        sys.exit(app.exec())
    finally:
        hot_reloader.stop()


if __name__ == "__main__":
    main()

