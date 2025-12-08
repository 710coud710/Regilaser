import json
import os

# Lấy folder AppData
appdata = os.getenv("APPDATA")
app_folder = os.path.join(appdata, "Regilazi")
os.makedirs(app_folder, exist_ok=True)

config_path = os.path.join(app_folder, "settings.json")
default_setting_path = os.path.join(os.path.dirname(__file__), "default_setting.json")

# Đọc config nếu tồn tại, nếu không thì tạo file mới từ default_config trong thư mục hiện tại
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    with open(default_setting_path, "r", encoding="utf-8") as df:
        settings = json.load(df)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

# Ví dụ cập nhật giá trị
settings["LASER_MODE"] = 1

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2)
