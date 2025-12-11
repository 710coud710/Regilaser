"""
Script để migrate từ config.yaml sang settings.json trong AppData
"""
import yaml
import json
import os


def migrate_config_to_settings():
    """Chuyển đổi config.yaml sang settings.json trong AppData"""
    
    # Đường dẫn config.yaml cũ
    config_yaml_path = "config.yaml"
    
    if not os.path.exists(config_yaml_path):
        print("config.yaml không tồn tại, không cần migrate")
        return False
    
    try:
        # Đọc config.yaml
        with open(config_yaml_path, "r", encoding="utf-8") as f:
            old_config = yaml.safe_load(f)
        
        # Chuyển đổi sang settings structure
        new_settings = {
            "general": {
                "station_name": old_config.get("STATION_NAME", "LM"),
                "mo": str(old_config.get("MO", "2790004600")),
                "op_num": old_config.get("OP_NUM", "F9385022"),
                "panel_num": str(old_config.get("PANEL_NUM", "5")),
                "post_result_sfc": old_config.get("POST_RESULT_SFC", True)
            },
            "connection": {
                "sfc": {
                    "use_com": True,
                    "com_port": old_config.get("SFIS_COM", "COM8"),
                    "baudrate": 9600,
                    "ip": "",
                    "port": 8080
                },
                "plc": {
                    "use_com": True,
                    "com_port": old_config.get("PLC_COM", "COM3"),
                    "baudrate": 9600,
                    "ip": "",
                    "port": 8080
                },
                "laser": {
                    "use_com": old_config.get("LASER_MODE", 1) == 2,  # 2 = COM
                    "com_port": old_config.get("LASER_COM_PORT", "COM1"),
                    "baudrate": old_config.get("LASER_BAUDRATE", 9600),
                    "ip": old_config.get("LASER_IP", "10.153.227.38"),
                    "port": old_config.get("LASER_PORT", 50002),
                    "timeout_ms": old_config.get("LASER_TIMEOUT_MS", 5000)
                }
            },
            "advanced": {
                "language": "en",
                "command_timeout_ms": 10000
            }
        }
        
        # Lưu vào AppData
        appdata = os.getenv("APPDATA")
        app_folder = os.path.join(appdata, "Regilazi")
        os.makedirs(app_folder, exist_ok=True)
        
        settings_path = os.path.join(app_folder, "settings.json")
        
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(new_settings, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Migration thành công!")
        print(f"  Config cũ: {config_yaml_path}")
        print(f"  Settings mới: {settings_path}")
        
        # Backup config.yaml cũ
        backup_path = "config.yaml.backup"
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(config_yaml_path, backup_path)
            print(f"  Backup: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi khi migrate: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Migration Tool: config.yaml → settings.json (AppData)")
    print("=" * 60)
    migrate_config_to_settings()

