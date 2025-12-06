import yaml
import threading
import time
import os
from pydantic import BaseModel, StrictBool, StrictStr, StrictInt, ValidationError
from utils.Logging import getLogger
from utils.schema import LaserConnectMode
# Khởi tạo logger
log = getLogger()

class Config(BaseModel):
    model_config = {"extra": "allow"}  # cho phép thêm key khác (FrontPSN_Num, etc.)
    STATION_NAME: StrictStr
    MO: StrictInt
    OP_NUM: StrictStr
    PANEL_NUM: StrictInt  # Panel Number để tạo NEEDPSNxx
    LASER_MODE: LaserConnectMode # 1: "TCP" or 2: "RS232"
    LASER_IP: StrictStr
    LASER_PORT: StrictInt
    LASER_SCRIPT: StrictInt
    LASER_TIMEOUT_MS: StrictInt
    LASER_COM_PORT: StrictStr
    LASER_BAUDRATE: StrictInt
    PLC_COM: StrictStr
    SFIS_COM: StrictStr
    RAW_CONTENT: StrictStr
    POST_RESULT_SFC: StrictBool
# === CONFIG MANAGER (singleton + hot reload + thread-safe) ===
class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, filename="config.yaml"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.filename = filename
                    cls._instance._config = None
                    cls._instance._file_mtime = 0
                    cls._instance._load()
                    cls._instance._start_hot_reload()
        return cls._instance

    def _load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._config = Config(**data)
            self._file_mtime = os.path.getmtime(self.filename)
            log.info(f"Config loaded successfully from {self.filename}")
        except (ValidationError, Exception) as e:
            log.error(f"Config load error:\n{e}")

    def get(self) -> Config:
        return self._config

    # Auto-reload khi file thay đổi
    def _start_hot_reload(self):
        def watcher():
            while True:
                try:
                    current_mtime = os.path.getmtime(self.filename)
                    if current_mtime != self._file_mtime:
                        with self._lock:
                            self._load()
                    time.sleep(1)
                except Exception:
                    time.sleep(1)
        t = threading.Thread(target=watcher, daemon=True)
        t.start()

    # update + validate + save YAML
    def update(self, field: str, value):
        with self._lock:
            data = self._config.model_dump()
            data[field] = value

            try:
                new_config = Config(**data)
            except ValidationError as e:
                log.error(f"Validation error:\n{e}")
                return False

            with open(self.filename, "w", encoding="utf-8") as f:
                yaml.dump(new_config.model_dump(), f, allow_unicode=True)
            log.info(f"Config updated successfully and saved to {self.filename}")
            return True
