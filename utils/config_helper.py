"""
Config Helper - Utilities để làm việc với config và settings
"""
from utils.setting import ConfigManager, settings_manager


def get_config():
    """
    Lấy config object hiện tại
    Sử dụng hàm này thay vì gọi ConfigManager().get() trực tiếp
    """
    return ConfigManager().get()


def reload_config():
    """
    Reload settings từ AppData và trả về config mới
    Sử dụng khi cần force reload config sau khi settings thay đổi
    """
    settings_manager.reload()
    return ConfigManager().get()


def update_config(field: str, value):
    """
    Update một field trong config và lưu vào settings
    
    Args:
        field: Tên field (uppercase, ví dụ: "LASER_IP")
        value: Giá trị mới
    
    Returns:
        bool: True nếu update thành công
    """
    config_manager = ConfigManager()
    return config_manager.update(field, value)


def get_setting(key: str, default=None):
    """
    Lấy giá trị setting theo key (nested với dot notation)
    
    Args:
        key: Key của setting (ví dụ: "connection.laser.ip")
        default: Giá trị mặc định nếu không tìm thấy
    
    Returns:
        Giá trị của setting
    """
    return settings_manager.get(key, default)


def set_setting(key: str, value):
    """
    Set giá trị setting theo key (nested với dot notation)
    
    Args:
        key: Key của setting (ví dụ: "connection.laser.ip")
        value: Giá trị mới
    """
    settings_manager.set(key, value)


def save_settings():
    """
    Lưu settings hiện tại vào AppData
    
    Returns:
        bool: True nếu lưu thành công
    """
    return settings_manager.save_settings()


# Convenience functions cho các settings thường dùng
def get_laser_ip():
    """Lấy Laser IP"""
    return get_setting("connection.laser.ip", "10.153.227.38")


def get_laser_port():
    """Lấy Laser Port"""
    return get_setting("connection.laser.port", 50002)


def get_laser_mode():
    """Lấy Laser Mode (COM hoặc TCP)"""
    use_com = get_setting("connection.laser.use_com", False)
    return 2 if use_com else 1  # 1: TCP, 2: COM


def get_sfc_com():
    """Lấy SFC COM Port"""
    return get_setting("connection.sfc.com_port", "COM8")


def get_plc_com():
    """Lấy PLC COM Port"""
    return get_setting("connection.plc.com_port", "COM3")


def get_station_name():
    """Lấy Station Name"""
    return get_setting("general.station_name", "LM")


def get_mo():
    """Lấy MO"""
    return get_setting("general.mo", "2790004600")


def get_op_num():
    """Lấy OP Number"""
    return get_setting("general.op_num", "F9385022")


def get_panel_num():
    """Lấy Panel Number"""
    return get_setting("general.panel_num", "5")

