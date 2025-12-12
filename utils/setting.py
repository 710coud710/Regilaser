import json
import os


class SettingsManager:
    def __init__(self):
        appdata = os.getenv("APPDATA")
        self.app_folder = os.path.join(appdata, "Regilazi")
        os.makedirs(self.app_folder, exist_ok=True)
        self.config_path = os.path.join(self.app_folder, "settings.json")
        # Default settings nằm ở thư mục chính của project
        self.default_setting_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "default_setting.json")
        )
        
        # Load settings
        self._settings = self._loadSettings()
    
    def _loadSettings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._loadDefaultSettings()
        else:
            return self._loadDefaultSettings()
    
    def _loadDefaultSettings(self):
        try:
            with open(self.default_setting_path, "r", encoding="utf-8") as df:
                default_settings = json.load(df)
            self.save_settings(default_settings)
            return default_settings
        except Exception as e:
            print(f"Error loading default settings: {e}")
            return {}
    
    def get_settings(self):
        return self._settings.copy()
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        keys = key.split('.')
        settings = self._settings
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        settings[keys[-1]] = value
    
    def save_settings(self, settings=None):
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
        self._settings = self._loadSettings()
    
    def reset_to_default(self):
        self._settings = self._loadDefaultSettings()


# Tạo instance global để sử dụng trong toàn bộ ứng dụng
settings_manager = SettingsManager()
