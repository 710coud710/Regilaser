import json
import os
from pydantic import BaseModel, StrictBool, StrictStr, StrictInt


class Config(BaseModel):
    """Pydantic model cho config - tương thích với code cũ"""
    model_config = {"extra": "allow"}
    
    # General settings
    STATION_NAME: StrictStr
    MO: StrictInt
    OP_NUM: StrictStr
    PANEL_NUM: StrictInt
    POST_RESULT_SFC: StrictBool
    
    # Laser settings
    LASER_MODE: StrictInt  # 1: TCP, 2: RS232/COM
    LASER_IP: StrictStr
    LASER_PORT: StrictInt
    LASER_SCRIPT: StrictInt = 20
    LASER_TIMEOUT_MS: StrictInt
    LASER_COM_PORT: StrictStr
    LASER_BAUDRATE: StrictInt
    
    # PLC settings
    PLC_COM: StrictStr
    
    # SFIS settings
    SFIS_COM: StrictStr
    
    # Other
    RAW_CONTENT: StrictStr = ""


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
    
    def get_config(self) -> Config:
        """
        Trả về Config object tương thích với code cũ sử dụng config.py
        Convert từ settings structure sang flat config structure
        """
        settings = self._settings
        
        # Lấy các giá trị từ settings structure
        general = settings.get("general", {})
        connection = settings.get("connection", {})
        sfc = connection.get("sfc", {})
        plc = connection.get("plc", {})
        laser = connection.get("laser", {})
        
        # Convert sang flat structure cho Config
        config_dict = {
            # General
            "STATION_NAME": general.get("station_name", "LM"),
            "MO": int(general.get("mo", "2790004600")),
            "OP_NUM": general.get("op_num", "F9385022"),
            "PANEL_NUM": int(general.get("panel_num", "5")),
            "POST_RESULT_SFC": general.get("post_result_sfc", True),
            
            # Laser
            "LASER_MODE": 2 if laser.get("use_com", False) else 1,  # 1: TCP, 2: COM
            "LASER_IP": laser.get("ip", "10.153.227.38"),
            "LASER_PORT": int(laser.get("port", 50002)),
            "LASER_SCRIPT": 20,
            "LASER_TIMEOUT_MS": int(laser.get("timeout_ms", 5000)),
            "LASER_COM_PORT": laser.get("com_port", "COM1"),
            "LASER_BAUDRATE": int(laser.get("baudrate", 9600)),
            
            # PLC
            "PLC_COM": plc.get("com_port", "COM3"),
            
            # SFIS
            "SFIS_COM": sfc.get("com_port", "COM8"),
            
            # Other
            "RAW_CONTENT": "",
        }
        
        return Config(**config_dict)


# Tạo instance global để sử dụng trong toàn bộ ứng dụng
settings_manager = SettingsManager()


class ConfigManager:
    """
    Wrapper class tương thích với code cũ sử dụng ConfigManager
    Chuyển hướng tất cả calls sang settings_manager
    """
    _instance = None
    
    def __new__(cls, filename=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get(self) -> Config:
        """Trả về Config object từ settings"""
        return settings_manager.get_config()
    
    def update(self, field: str, value):
        """Update một field và lưu vào settings"""
        # Convert field name từ uppercase sang lowercase và nested structure
        field_mapping = {
            "STATION_NAME": "general.station_name",
            "MO": "general.mo",
            "OP_NUM": "general.op_num",
            "PANEL_NUM": "general.panel_num",
            "POST_RESULT_SFC": "general.post_result_sfc",
            "LASER_MODE": "connection.laser.use_com",  # Special handling
            "LASER_IP": "connection.laser.ip",
            "LASER_PORT": "connection.laser.port",
            "LASER_TIMEOUT_MS": "connection.laser.timeout_ms",
            "LASER_COM_PORT": "connection.laser.com_port",
            "LASER_BAUDRATE": "connection.laser.baudrate",
            "PLC_COM": "connection.plc.com_port",
            "SFIS_COM": "connection.sfc.com_port",
        }
        
        if field in field_mapping:
            setting_key = field_mapping[field]
            
            # Special handling for LASER_MODE
            if field == "LASER_MODE":
                # 1: TCP, 2: COM
                settings_manager.set("connection.laser.use_com", value == 2)
            else:
                settings_manager.set(setting_key, value)
            
            settings_manager.save_settings()
            return True
        
        return False
