"""
Single Instance Manager - Đảm bảo chỉ có một instance của ứng dụng chạy
Sử dụng Windows Mutex API và file locking cho Unix
"""
import sys
import os
import tempfile
import atexit
from utils.Logging import getLogger

log = getLogger()


class SingleInstanceWindows:
    """Single instance cho Windows sử dụng Windows Mutex API"""
    
    def __init__(self, app_name="Regilaser"):
        self.app_name = app_name
        self.mutex_name = f"Global\\{app_name}_Mutex"
        self.mutex_handle = None
        self.is_locked = False
        
        # Import Windows API
        try:
            import ctypes
            from ctypes import wintypes
            self.kernel32 = ctypes.windll.kernel32
            self.ERROR_ALREADY_EXISTS = 183
            log.info(f"SingleInstanceWindows: Mutex name: {self.mutex_name}")
        except ImportError:
            log.error("SingleInstanceWindows: Failed to import ctypes")
            self.kernel32 = None
    
    def try_lock(self):
        """Thử tạo mutex. Trả về True nếu thành công, False nếu đã tồn tại"""
        if not self.kernel32:
            log.error("SingleInstanceWindows: Windows API not available")
            return False
        
        try:
            # Tạo mutex
            self.mutex_handle = self.kernel32.CreateMutexW(
                None,  # Security attributes
                True,  # Initial owner
                self.mutex_name  # Mutex name
            )
            
            if self.mutex_handle:
                # Kiểm tra xem mutex đã tồn tại chưa
                last_error = self.kernel32.GetLastError()
                if last_error == self.ERROR_ALREADY_EXISTS:
                    log.warning("SingleInstanceWindows: Mutex already exists - another instance is running")
                    self.kernel32.CloseHandle(self.mutex_handle)
                    self.mutex_handle = None
                    return False
                else:
                    self.is_locked = True
                    log.info("SingleInstanceWindows: Successfully created mutex")
                    return True
            else:
                log.error("SingleInstanceWindows: Failed to create mutex")
                return False
                
        except Exception as e:
            log.error(f"SingleInstanceWindows: Error creating mutex: {e}")
            return False
    
    def unlock(self):
        """Giải phóng mutex"""
        if self.mutex_handle and self.is_locked:
            try:
                self.kernel32.ReleaseMutex(self.mutex_handle)
                self.kernel32.CloseHandle(self.mutex_handle)
                self.mutex_handle = None
                self.is_locked = False
                log.info("SingleInstanceWindows: Mutex released")
            except Exception as e:
                log.error(f"SingleInstanceWindows: Error releasing mutex: {e}")
    
    def show_already_running_message(self):
        """Hiển thị thông báo khi ứng dụng đã chạy"""
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "Regilaser Laser Marking System is already running!\n\n"
                "Only one instance can run at a time.\n"
                "Please close the existing instance before starting a new one.",
                "Regilaser Already Running",
                0x30  # MB_ICONWARNING
            )
            log.info("SingleInstanceWindows: Showed 'already running' message")
        except Exception as e:
            log.error(f"SingleInstanceWindows: Error showing message: {e}")
            print("ERROR: Regilaser is already running!")
    
    def __del__(self):
        """Destructor"""
        self.unlock()


class SingleInstanceUnix:
    """Single instance cho Unix/Linux sử dụng file locking (fcntl)"""
    
    def __init__(self, app_name="Regilaser"):
        self.app_name = app_name
        self.lock_file = None
        self.lock_fd = None
        self.is_locked = False
        
        # Tạo lock file trong /tmp
        self.lock_file_path = f"/tmp/{app_name}.lock"
        log.info(f"SingleInstanceUnix: Lock file path: {self.lock_file_path}")
    
    def try_lock(self):
        """Thử khóa ứng dụng"""
        try:
            import fcntl
            
            # Mở file với O_CREAT để tạo nếu chưa tồn tại
            self.lock_fd = os.open(
                self.lock_file_path, 
                os.O_CREAT | os.O_TRUNC | os.O_RDWR,
                0o600  # Chỉ owner có quyền đọc/ghi
            )
            
            # Thử khóa file (non-blocking)
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Ghi PID vào file
            pid_str = f"{os.getpid()}\n"
            os.write(self.lock_fd, pid_str.encode())
            os.fsync(self.lock_fd)
            
            self.is_locked = True
            log.info(f"SingleInstanceUnix: Successfully acquired lock (PID: {os.getpid()})")
            
            # Đăng ký cleanup khi exit
            atexit.register(self.unlock)
            
            return True
            
        except (OSError, IOError, ImportError) as e:
            log.warning(f"SingleInstanceUnix: Failed to acquire lock: {e}")
            if self.lock_fd:
                try:
                    os.close(self.lock_fd)
                except:
                    pass
                self.lock_fd = None
            return False
    
    def unlock(self):
        """Mở khóa"""
        if self.lock_fd and self.is_locked:
            try:
                import fcntl
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                
                # Xóa file lock
                if os.path.exists(self.lock_file_path):
                    os.unlink(self.lock_file_path)
                    
                log.info("SingleInstanceUnix: Lock released")
            except Exception as e:
                log.error(f"SingleInstanceUnix: Error releasing lock: {e}")
            finally:
                self.lock_fd = None
                self.is_locked = False
    
    def show_already_running_message(self):
        """Hiển thị thông báo (console cho Unix)"""
        print("ERROR: Regilaser Laser Marking System is already running!")
        print("Only one instance can run at a time.")
        log.info("SingleInstanceUnix: Showed 'already running' message")
    
    def __del__(self):
        self.unlock()


def get_single_instance(app_name="Regilaser"):
    """Factory function để tạo SingleInstance phù hợp với OS"""
    if sys.platform.startswith('win'):
        return SingleInstanceWindows(app_name)
    else:
        return SingleInstanceUnix(app_name)
