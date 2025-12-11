# Settings Manager Usage Guide

## Overview
Settings are now stored in the Windows AppData folder: `%APPDATA%\Regilazi\settings.json`

The settings manager provides a centralized way to load, save, and access application settings.

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

## Notes

- Settings are automatically loaded when the application starts
- The settings file is created in AppData if it doesn't exist
- Default settings are loaded from `utils/default_setting.json`
- The Settings Window automatically saves to AppData when you click "Apply" or "OK"

