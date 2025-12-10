import sys
import time
import subprocess
import psutil
import os

def safe_print(msg):
    try:
        print(msg)
    except:
        pass

def main():
    if len(sys.argv) < 3:
        safe_print("Usage: RestartHelper.exe <app_path> <pid>")
        return

    app_path = sys.argv[1]
    pid = int(sys.argv[2])

    safe_print(f"[RestartHelper] Target app: {app_path}")
    safe_print(f"[RestartHelper] Waiting for PID: {pid}")

    # Chờ app chính thoát hẳn
    try:
        p = psutil.Process(pid)
        p.wait(timeout=10)    # chờ tối đa 10s
    except psutil.NoSuchProcess:
        pass
    except psutil.TimeoutExpired:
        safe_print("[RestartHelper] Force kill old process…")
        try:
            p.kill()
        except:
            pass

    time.sleep(0.5)

    safe_print("[RestartHelper] Restarting app…")
    subprocess.Popen([app_path], shell=True)

    safe_print("[RestartHelper] Done. Exiting.")
    time.sleep(0.2)

if __name__ == "__main__":
    main()
