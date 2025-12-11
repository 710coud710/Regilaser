import json
import os


class SettingsManager:
    """Quản lý settings lưu trong AppData"""
    
    def __init__(self):
        # Lấy folder AppData
        appdata = os.getenv("APPDATA")
        self.app_folder = os.path.join(appdata, "Regilazi")
        os.makedirs(self.app_folder, exist_ok=True)
        
        self.config_path = os.path.join(self.app_folder, "settings.json")
        self.default_setting_path = os.path.join(os.path.dirname(__file__), "default_setting.json")
        
        # Load settings
        self._settings = self._load_settings()
    
    def _load_settings(self):
        """Đọc settings từ AppData, nếu không có thì tạo từ default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._load_default_settings()
        else:
            return self._load_default_settings()
    
    def _load_default_settings(self):
        """Load default settings và lưu vào AppData"""
        try:
            with open(self.default_setting_path, "r", encoding="utf-8") as df:
                default_settings = json.load(df)
            self.save_settings(default_settings)
            return default_settings
        except Exception as e:
            print(f"Error loading default settings: {e}")
            return {}
    
    def get_settings(self):
        """Lấy toàn bộ settings"""
        return self._settings.copy()
    
    def get(self, key, default=None):
        """Lấy giá trị setting theo key (hỗ trợ nested keys với dấu chấm)"""
        keys = key.split('.')
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set giá trị setting theo key (hỗ trợ nested keys với dấu chấm)"""
        keys = key.split('.')
        settings = self._settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
    
    def save_settings(self, settings=None):
        """Lưu settings vào AppData"""
        if settings is not None:
            self._settings = settings
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def reload(self):
        """Reload settings từ file"""
        self._settings = self._load_settings()
    
    def reset_to_default(self):
        """Reset settings về mặc định"""
        self._settings = self._load_default_settings()


# Tạo instance global để sử dụng trong toàn bộ ứng dụng
settings_manager = SettingsManager()
