"""
Hot Reload Module - Tự động reload GUI khi có thay đổi code
"""
import sys
import importlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import QTimer


class HotReloadHandler(FileSystemEventHandler):
    """Handler để theo dõi thay đổi file"""
    
    def __init__(self, app, window_class, reload_callback):
        super().__init__()
        self.app = app
        self.window_class = window_class
        self.reload_callback = reload_callback
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self._do_reload)
        self.pending_reload = False
        
    def on_modified(self, event):
        """Được gọi khi file bị modified"""
        if event.is_directory:
            return
            
        # Chỉ reload khi file .py trong gui/ hoặc model/ thay đổi
        file_path = Path(event.src_path)
        if file_path.suffix == '.py' and (
            'gui' in file_path.parts or 
            'model' in file_path.parts or
            'presenter' in file_path.parts
        ):
            print(f"🔄 Phát hiện thay đổi: {file_path.name}")
            # Debounce: chờ 500ms trước khi reload
            if not self.pending_reload:
                self.pending_reload = True
                self.reload_timer.start(500)
    
    def _do_reload(self):
        """Thực hiện reload"""
        self.pending_reload = False
        print(" Đang reload...")
        self.reload_callback()


class HotReloader:
    """Class quản lý hot reload"""
    
    def __init__(self, app, main_window, create_window_func):
        self.app = app
        self.main_window = main_window
        self.create_window_func = create_window_func
        self.observer = None
        
    def start(self):
        """Bắt đầu theo dõi thay đổi"""
        project_root = Path(__file__).parent
        
        # Tạo handler
        handler = HotReloadHandler(
            self.app,
            type(self.main_window),
            self._reload_window
        )
        
        # Tạo observer
        self.observer = Observer()
        self.observer.schedule(handler, str(project_root), recursive=True)
        self.observer.start()
        
        print("🔥 Hot Reload đã được kích hoạt!")
        print(f"📁 Đang theo dõi: {project_root}")
        print("💡 Mọi thay đổi trong gui/, model/, presenter/ sẽ tự động reload\n")
    
    def stop(self):
        """Dừng theo dõi"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def _reload_window(self):
        """Reload window với các modules mới"""
        try:
            # Lưu trạng thái window cũ
            old_geometry = self.main_window.geometry()
            
            # Đóng window cũ
            self.main_window.close()
            
            # Reload tất cả modules trong gui/
            self._reload_modules('gui')
            self._reload_modules('model')
            self._reload_modules('presenter')
            
            # Tạo window mới
            self.main_window = self.create_window_func()
            self.main_window.setGeometry(old_geometry)
            self.main_window.show()
            
            print("✅ Reload thành công!\n")
            
        except Exception as e:
            print(f"❌ Lỗi khi reload: {e}")
            import traceback
            traceback.print_exc()
    
    def _reload_modules(self, package_name):
        """Reload tất cả modules trong một package"""
        modules_to_reload = []
        
        # Tìm tất cả modules cần reload
        for name, module in list(sys.modules.items()):
            if name.startswith(f'{package_name}.') or name == package_name:
                modules_to_reload.append((name, module))
        
        # Reload theo thứ tự ngược (từ submodule đến parent)
        for name, module in reversed(modules_to_reload):
            if module is not None:
                try:
                    importlib.reload(module)
                    print(f"  ↻ Reloaded: {name}")
                except Exception as e:
                    print(f"  ⚠ Không thể reload {name}: {e}")

