"""Giả lập PLC:
- MODE = 1: TCP server (ứng dụng PLC kết nối qua TCP)
- MODE = 2: RS232 (COM) server – ứng dụng PLC kết nối qua cổng COM
"""

import socket
import threading
import sys

import serial

# 1: TCP, 2: RS232 (COM)
MODE = 2
# Cấu hình TCP
HOST = "0.0.0.0"
PORT = 50001

# Cấu hình COM
COM = "COM2"
BAUDRATE = 9600
TIMEOUT_S = 1.0

shutdown_flag = threading.Event()
send_ready_event = threading.Event()


def bytes_to_hex(data: bytes, max_bytes: int = 100) -> str:
    """Chuyển bytes sang HEX string để log."""
    if len(data) <= max_bytes:
        return " ".join(f"{b:02X}" for b in data)
    hex_str = " ".join(f"{b:02X}" for b in data[:max_bytes])
    return f"{hex_str} ... ({len(data)} bytes total)"



def input_listener(send_func):
    print("Nhấn 's' để gửi READY, 'q' để thoát (không cần Enter).")
    # Sử dụng đọc ký tự không cần Enter
    try:
        if sys.platform.startswith('win'):
            import msvcrt
            getch = lambda: msvcrt.getch().decode('utf-8', errors='ignore')
        else:
            import termios, tty
            def getch():
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
    except Exception as e:
        print(f"[ERROR] getch setup failed: {e}")
        return

    while not shutdown_flag.is_set():
        try:
            ch = getch()
            if not ch:
                continue
            ch_lower = ch.lower()
            if ch_lower == 'q':
                shutdown_flag.set()
                print("[SHUTDOWN] Đã nhận lệnh tắt PLC giả lập.")
                break
            if ch_lower == 's':
                send_ready_event.set()
                send_func(b"READY\r\n")
                print("[PLC] >>> Sent READY")
        except (KeyboardInterrupt, EOFError):
            break


def handle_tcp_client(conn, addr):
    peer = f"{addr}"
    print(f"[CONNECTED] PLC client connected from {peer}")

    def send_bytes(data: bytes):
        try:
            conn.sendall(data)
        except Exception as exc:
            print(f"[ERROR] TCP send error: {exc}")

    listener_thread = threading.Thread(target=input_listener, args=(send_bytes,), daemon=True)
    listener_thread.start()

    try:
        while not shutdown_flag.is_set():
            conn.settimeout(1.0)
            try:
                data = conn.recv(4096)
                if not data:
                    print(f"[DISCONNECTED] Client {peer} closed connection")
                    break
                print(f"\n{'=' * 30}")
                print(f"[PLC RECEIVED TCP] From {peer}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")
            except socket.timeout:
                continue
            except Exception as exc:
                print(f"[ERROR] TCP receive error: {exc}")
                break
    finally:
        shutdown_flag.set()
        conn.close()
        print(f"[DISCONNECTED] TCP client {peer} disconnected")


def run_tcp_server():
    print(f"[STARTED] Fake PLC TCP Server listening on {HOST}:{PORT}")
    print("[INFO] Waiting for laser app to connect via TCP...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    try:
        server.settimeout(1)
        while not shutdown_flag.is_set():
            try:
                conn, addr = server.accept()
                handle_tcp_client(conn, addr)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down TCP PLC.")
        shutdown_flag.set()
    finally:
        server.close()
        print("[STOPPED] TCP PLC server exited cleanly.")


def run_com_server():
    print(f"[STARTED] Fake PLC COM Server on {COM} @ {BAUDRATE}bps")
    print("[INFO] Waiting for laser app to connect via COM...")

    try:
        ser = serial.Serial(
            port=COM,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT_S,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
    except Exception as exc:
        print(f"[ERROR] Cannot open COM port {COM}: {exc}")
        return

    def send_bytes(data: bytes):
        try:
            ser.write(data)
        except Exception as exc:
            print(f"[ERROR] COM send error: {exc}")

    listener_thread = threading.Thread(target=input_listener, args=(send_bytes,), daemon=True)
    listener_thread.start()

    try:
        while not shutdown_flag.is_set():
            try:
                data = ser.read(4096)
                if not data:
                    continue
                print(f"\n{'=' * 30}")
                print(f"[PLC RECEIVED COM] From {COM}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")
            except Exception as exc:
                print(f"[ERROR] COM receive error: {exc}")
                break
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down COM PLC.")
        shutdown_flag.set()
    finally:
        print("[SHUTDOWN] Closing COM port...")
        try:
            ser.close()
        except Exception:
            pass
        print("[STOPPED] COM PLC server exited cleanly.")


def main():
    if MODE == 1:
        run_tcp_server()
    else:
        run_com_server()


if __name__ == "__main__":
    main()

