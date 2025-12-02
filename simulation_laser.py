"""
Giả lập Laser Controller cho test:
- MODE = 1: TCP server (giữ nguyên như trước)
- MODE = 2: RS232 (COM) server – giả lập laser trên cổng COM
"""

import socket
import threading
import time
import sys

import serial


# 1: TCP, 2: RS232 (COM)
MODE = 2

# Cấu hình TCP
HOST = "0.0.0.0"  # Hoặc IP cụ thể
PORT = 50002

# Cấu hình COM
COM = "COM4"
BAUDRATE = 9600
TIMEOUT_S = 1.0


shutdown_flag = threading.Event()


def bytes_to_hex(data: bytes, max_bytes: int = 100) -> str:
    """Chuyển bytes sang HEX string để log"""
    if len(data) <= max_bytes:
        return " ".join(f"{b:02X}" for b in data)
    else:
        hex_str = " ".join(f"{b:02X}" for b in data[:max_bytes])
        return f"{hex_str} ... ({len(data)} bytes total)"


def process_buffer(buffer: bytes, send_func, peer_name: str) -> bytes:
    """
    Xử lý buffer, tách các lệnh theo \r\n / \n và gửi response qua send_func(bytes).
    Trả về buffer còn dư (nếu không đủ để tạo 1 dòng).
    """
    while b"\r\n" in buffer or (b"\n" in buffer and b"\r\n" not in buffer):
        if b"\r\n" in buffer:
            line, buffer = buffer.split(b"\r\n", 1)
        else:
            line, buffer = buffer.split(b"\n", 1)

        if not line:
            continue

        try:
            command = line.decode("ascii", errors="replace").strip()
            print(f"\n[COMMAND from {peer_name}] '{command}'")

            # Giả lập xử lý lệnh
            response = None
            if command.startswith("GA,"):
                time.sleep(0.5)  # Giả lập xử lý
                response = "GA,0"
            elif command.startswith("C2,"):
                time.sleep(1.0)  # Giả lập xử lý lâu hơn cho C2
                # Có thể trả về C2,0 (success) hoặc C2,1,Sxxx (error)
                response = "C2,0"
            elif command == "NT" or command.startswith("NT,"):
                time.sleep(0.5)
                response = "NT,0"
            else:
                # Log lệnh không xác định nhưng vẫn phản hồi
                print(f"[WARNING] Unknown command from {peer_name}: '{command}'")
                response = "ERROR,UNKNOWN_COMMAND"

            if response:
                response_line = f"{response}\r\n".encode("ascii")
                send_func(response_line)
                print(f"[RESPONSE to {peer_name}] '{response.strip()}'")
                print(f"  HEX: {bytes_to_hex(response_line)}")

        except Exception as e:
            print(f"[ERROR] Error processing command from {peer_name}: {e}")
            error_response = f"ERROR,{str(e)}\r\n".encode("ascii")
            send_func(error_response)

    return buffer


def handle_client(conn, addr):
    """Xử lý 1 client TCP"""
    peer = f"{addr}"
    print(f"[CONNECTED] TCP client connected from {peer}")
    buffer = b""
    try:
        while not shutdown_flag.is_set():
            conn.settimeout(1.0)
            try:
                data = conn.recv(4096)
                if not data:
                    print(f"[DISCONNECTED] TCP client {peer} closed connection")
                    break

                # Log toàn bộ dữ liệu nhận được
                print(f"\n{'=' * 60}")
                print(f"[RECEIVED TCP] From {peer}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  Raw HEX: {bytes_to_hex(data)}")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")

                buffer += data

                # Xử lý buffer thành các lệnh
                buffer = process_buffer(buffer, conn.sendall, peer)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[ERROR] TCP receive error from {peer}: {e}")
                break

    except Exception as e:
        print(f"[ERROR] TCP client handler error ({peer}): {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] TCP client {peer} disconnected")


def input_listener():
    print("Nhấn 'q' rồi Enter để tắt server.")
    while not shutdown_flag.is_set():
        try:
            if sys.version_info >= (3, 0):
                line = input()
            else:
                line = raw_input()
        except EOFError:
            break
        if line.strip().lower() == "q":
            shutdown_flag.set()
            print("[SHUTDOWN] Đã nhận lệnh tắt server.")
            break


def run_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    # Lấy địa chỉ IP thực tế của server
    if HOST == "0.0.0.0":
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "N/A"
        print(f"[STARTED] Fake Laser TCP Server listening on {HOST}:{PORT}")
        print(f"[INFO] Server will accept connections on all interfaces")
        if local_ip != "N/A":
            print(f"[INFO] Local IP: {local_ip}:{PORT}")
    else:
        print(f"[STARTED] Fake Laser TCP Server listening on {HOST}:{PORT}")
    print(f"[INFO] Ready to receive laser commands (GA, C2, NT, etc.) via TCP")
    print(f"[INFO] Press 'q' + Enter to shutdown\n")

    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    client_threads = []

    try:
        while not shutdown_flag.is_set():
            server.settimeout(1)
            try:
                conn, addr = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
                client_threads.append(client_thread)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down TCP server.")
        shutdown_flag.set()
    finally:
        print("[SHUTDOWN] Closing TCP server socket and waiting for client threads...")
        server.close()
        for t in client_threads:
            t.join()
        print("[STOPPED] TCP server exited cleanly.")


def run_com_server():
    """Giả lập Laser qua cổng COM (RS232)."""
    print(f"[STARTED] Fake Laser COM Server on {COM} @ {BAUDRATE}bps")
    print("[INFO] Ready to receive laser commands (GA, C2, NT, etc.) via RS232")
    print("[INFO] Press 'q' + Enter to shutdown\n")

    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

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
    except Exception as e:
        print(f"[ERROR] Cannot open COM port {COM}: {e}")
        return

    buffer = b""
    peer = f"COM:{COM}"

    try:
        while not shutdown_flag.is_set():
            try:
                data = ser.read(4096)
                if not data:
                    # Timeout: bình thường, tiếp tục vòng lặp
                    continue

                print(f"\n{'=' * 60}")
                print(f"[RECEIVED COM] From {peer}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  Raw HEX: {bytes_to_hex(data)}")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")

                buffer += data

                # Xử lý buffer thành các lệnh
                buffer = process_buffer(buffer, ser.write, peer)

            except Exception as e:
                print(f"[ERROR] COM receive error on {peer}: {e}")
                break
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down COM server.")
        shutdown_flag.set()
    finally:
        print("[SHUTDOWN] Closing COM port...")
        try:
            ser.close()
        except Exception:
            pass
        print("[STOPPED] COM server exited cleanly.")


def main():
    if MODE == 1:
        run_tcp_server()
    else:
        run_com_server()


if __name__ == "__main__":
    main()
