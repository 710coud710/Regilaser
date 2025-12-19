import os
import sys
import json
import subprocess
from utils.Logging import getLogger
from utils.AppPathService import getAppDirectory
log = getLogger()

def restartApp(app_path = None):
    exe_dir = getAppDirectory()
    """
    Ghi file service.json vào AppData để yêu cầu restart app.
    app_path: đường dẫn exe của ứng dụng cần restart
    """ 
    try:
        if app_path is None:
            app_path = sys.executable
        else:
            app_path = os.path.abspath(app_path)
        log.info(f"Restart app path: {app_path}")
        appdata = os.getenv("APPDATA")
        service_folder = os.path.join(appdata, "Regilaser")
        os.makedirs(service_folder, exist_ok=True)

        service_file = os.path.join(service_folder, "service.json")
        log.info(f"Restart service file: {service_file}")
        data = {
            "app_path": app_path,
            "action": "restart"
        }
        log.info(f"Restart data: {data}")
        try:
            with open(service_file, "w") as f:
                json.dump(data, f)
            log.info(f"Restart request written to {service_file}")

            ps_script = os.path.join(exe_dir, "restart.ps1")  # Đường dẫn script PowerShell
            if os.path.exists(ps_script):
                subprocess.run([
                    "powershell",
                    "-ExecutionPolicy", "Bypass",
                    "-WindowStyle", "Hidden",  
                    "-File", ps_script
                ], check=True)
                log.info("PowerShell restart script executed successfully.")
            else:
                log.error(f"{ps_script} not found")
        except Exception as e:
            log.error(f"{e}")
            return False

        return True
    except Exception as e:
        log.error(f"Error restarting app: {e}")
        return False