"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from gui.MainWindow import MainWindow
from gui.PathSetupDialog import PathSetupDialog
from presenter.main_presenter import MainPresenter
from utils.Logging import getLogger
<<<<<<< HEAD
from utils.SingleInstance import get_single_instance
=======
from utils.setting import settings_manager
>>>>>>> dev
import signal

# Khởi tạo logger sẽ được gọi sau khi check path
log = None


def check_and_setup_log_path():
    """
    Kiểm tra và setup đường dẫn log khi khởi động lần đầu
    Returns: True nếu setup thành công, False nếu user cancel
    """
    try:
        settings = settings_manager.get_settings()
        path_app = settings.get("advanced", {}).get("path_app", None)
        
        # Nếu path_app là null, hiển thị dialog
        if path_app is None:
            dialog = PathSetupDialog()
            result = dialog.exec()
            
            if result == PathSetupDialog.Accepted:
                selected_path = dialog.get_selected_path()
                if selected_path and selected_path != "logs":
                    # Lưu path vào settings
                    settings["advanced"]["path_app"] = selected_path
                    settings_manager.save_settings(settings)
                    print(f"Log path set to: {selected_path}")
                    return True
            # User chọn "Use Default" hoặc cancel
            return True
        
        return True
    except Exception as e:
        print(f"Error in check_and_setup_log_path: {e}")
        return True  # Continue anyway với default path


def main():
<<<<<<< HEAD
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
=======
    global log
    
    app = QApplication(sys.argv)  # Khởi tạo application trước
    
    # Check và setup log path nếu cần
    if not check_and_setup_log_path():
        print("Application setup cancelled by user")
        sys.exit(0)
    
    # Khởi tạo logger sau khi đã có path
    log = getLogger()
    log.info("--------------------------------- Regilazi Laser Marking System started ---------------------------------")
    
    window = MainWindow()  # Khởi tạo window
    presenter = MainPresenter(window)  # Khởi tạo presenter
    presenter.initialize()  # Khởi tạo kết nối và cấu hình ban đầu
    window.show()  # Hiển thị window
    signal.signal(signal.SIGINT, signal.SIG_DFL) 
    
    # Chạy ứng dụng và lấy exit code
    exit_code = app.exec()
    log.info("Application closing...............!!!")
    presenter.cleanup()
    log.info("--------------------------------- Application exited successfully ---------------------------------")
>>>>>>> dev
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

