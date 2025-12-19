"""
Main Entry Point - Khởi tạo ứng dụng
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from gui.MainWindow import MainWindow
from gui.PathSetupDialog import PathSetupDialog
from presenter.main_presenter import MainPresenter
from utils.Logging import getLogger
from utils.SingleInstance import get_single_instance
import signal
log = getLogger()   

# def check_and_setup_log_path():
#     """
#     Kiểm tra và setup đường dẫn log khi khởi động lần đầu
#     Returns: True nếu setup thành công, False nếu user cancel
#     """
#     try:
#         settings = settings_manager.get_settings()
#         path_app = settings.get("advanced", {}).get("path_app", None)
        
#         # Nếu path_app là null, hiển thị dialog
#         if path_app is None:
#             dialog = PathSetupDialog()
#             result = dialog.exec()
            
#             if result == PathSetupDialog.Accepted:
#                 selected_path = dialog.get_selected_path()
#                 if selected_path and selected_path != "logs":
#                     # Lưu path vào settings
#                     settings["advanced"]["path_app"] = selected_path
#                     settings_manager.save_settings(settings)
#                     print(f"Log path set to: {selected_path}")
#                     return True
#             # User chọn "Use Default" hoặc cancel
#             return True
        
#         return True
#     except Exception as e:
#         print(f"Error in check_and_setup_log_path: {e}")
#         return True  # Continue anyway với default path


def main():
    log.info("--------------------------------- Regilaser Laser Marking System started ---------------------------------")
    single_instance = get_single_instance("Regilaser")
    
    if not single_instance.try_lock():
        log.warning("Another instance of Regilaser is already running")
        single_instance.show_already_running_message()
        sys.exit(1)
    try:        
        app = QApplication(sys.argv)
        window = MainWindow()
        presenter = MainPresenter(window)
        presenter.initialize()
        window.show()
        signal.signal(signal.SIGINT, signal.SIG_DFL) 
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

