# Settings Manager Usage Guide

## Overview
Settings are now stored in the Windows AppData folder: `%APPDATA%\Regilazi\settings.json`

The settings manager provides a centralized way to load, save, and access application settings.

**⚠️ IMPORTANT CHANGE:** 
- `config.yaml` đã được thay thế bằng `settings.json` trong AppData
- Code cũ sử dụng `from config import SettingsManager` vẫn hoạt động (backward compatible)
- Tất cả giá trị cấu hình giờ được lưu trong AppData thay vì file config.yaml

## Migration từ config.yaml

Nếu bạn có file `config.yaml` cũ, chạy script migration:

```bash
python utils/migrate_config.py
```

Script sẽ tự động:
- Đọc config.yaml
- Chuyển đổi sang settings.json trong AppData
- Tạo backup config.yaml.backup

## Basic Usage

### Import the settings manager
```python
from utils.setting import settings_manager
```

### Get all settings
```python
all_settings = settings_manager.get_settings()
```

### Get a specific setting value
```python
# Get nested values using dot notation
station_name = settings_manager.get("general.station_name")
laser_ip = settings_manager.get("connection.laser.ip")
language = settings_manager.get("advanced.language")

# With default value
timeout = settings_manager.get("connection.laser.timeout_ms", 5000)
```

### Set a setting value
```python
# Set nested values using dot notation
settings_manager.set("general.station_name", "LM01")
settings_manager.set("connection.laser.ip", "192.168.1.100")
```

### Save settings to file
```python
# Save current settings
settings_manager.save_settings()

# Or save a complete settings dictionary
new_settings = {
    "general": {...},
    "connection": {...},
    "advanced": {...}
}
settings_manager.save_settings(new_settings)
```

### Reload settings from file
```python
settings_manager.reload()
```

### Reset to default settings
```python
settings_manager.reset_to_default()
```

## Settings Structure

```json
{
  "general": {
    "station_name": "LM",
    "mo": "2790004600",
    "op_num": "F9385022",
    "panel_num": "5",
    "post_result_sfc": true
  },
  "connection": {
    "sfc": {
      "use_com": true,
      "com_port": "COM8",
      "baudrate": 9600,
      "ip": "",
      "port": 8080
    },
    "plc": {
      "use_com": true,
      "com_port": "COM3",
      "baudrate": 9600,
      "ip": "",
      "port": 8080
    },
    "laser": {
      "use_com": false,
      "com_port": "COM1",
      "baudrate": 9600,
      "ip": "10.153.227.38",
      "port": 50002,
      "timeout_ms": 5000
    }
  },
  "advanced": {
    "language": "en",
    "command_timeout_ms": 10000
  }
}
```

## Example: Using settings in your code

### Cách 1: Sử dụng SettingsManager (tương thích với code cũ)

```python
from utils.setting import SettingsManager

# Code cũ vẫn hoạt động bình thường
config = SettingsManager().get()

# Truy cập các giá trị
station_name = config.STATION_NAME
laser_ip = config.LASER_IP
laser_mode = config.LASER_MODE  # 1: TCP, 2: COM
sfis_com = config.SFIS_COM

# Update giá trị
config_manager = SettingsManager()
config_manager.update("LASER_IP", "192.168.1.100")
config_manager.update("STATION_NAME", "LM01")
```

### Cách 2: Sử dụng settings_manager trực tiếp

```python
from utils.setting import settings_manager

# In your laser connection code
def connect_to_laser():
    use_com = settings_manager.get("connection.laser.use_com", False)
    
    if use_com:
        com_port = settings_manager.get("connection.laser.com_port")
        baudrate = settings_manager.get("connection.laser.baudrate")
        # Connect via COM
        print(f"Connecting to laser via {com_port} at {baudrate} baud")
    else:
        ip = settings_manager.get("connection.laser.ip")
        port = settings_manager.get("connection.laser.port")
        # Connect via TCP/IP
        print(f"Connecting to laser at {ip}:{port}")

# In your SFC connection code
def connect_to_sfc():
    com_port = settings_manager.get("connection.sfc.com_port")
    baudrate = settings_manager.get("connection.sfc.baudrate")
    print(f"Connecting to SFC via {com_port} at {baudrate} baud")
```

## Mapping giữa Config cũ và Settings mới

| Config cũ (YAML) | Settings mới (JSON) | SettingsManager field |
|------------------|---------------------|---------------------|
| STATION_NAME | general.station_name | config.STATION_NAME |
| MO | general.mo | config.MO |
| OP_NUM | general.op_num | config.OP_NUM |
| PANEL_NUM | general.panel_num | config.PANEL_NUM |
| POST_RESULT_SFC | general.post_result_sfc | config.POST_RESULT_SFC |
| LASER_MODE | connection.laser.use_com | config.LASER_MODE |
| LASER_IP | connection.laser.ip | config.LASER_IP |
| LASER_PORT | connection.laser.port | config.LASER_PORT |
| LASER_TIMEOUT_MS | connection.laser.timeout_ms | config.LASER_TIMEOUT_MS |
| LASER_COM_PORT | connection.laser.com_port | config.LASER_COM_PORT |
| LASER_BAUDRATE | connection.laser.baudrate | config.LASER_BAUDRATE |
| PLC_COM | connection.plc.com_port | config.PLC_COM |
| SFIS_COM | connection.sfc.com_port | config.SFIS_COM |

## Notes

- Settings are automatically loaded when the application starts
- The settings file is created in AppData if it doesn't exist
- Default settings are loaded from `utils/default_setting.json`
- The Settings Window automatically saves to AppData when you click "Apply" or "OK"

