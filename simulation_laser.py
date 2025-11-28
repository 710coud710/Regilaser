# fake_laser_server.py
import socket
import threading
import time
import sys

# Lắng nghe trên tất cả interfaces để chương trình có thể kết nối
HOST = "0.0.0.0"  # Hoặc "172.20.10.5" nếu muốn chỉ lắng nghe trên IP cụ thể
PORT = 50002

shutdown_flag = threading.Event()

def bytes_to_hex(data: bytes, max_bytes: int = 100) -> str:
    """Chuyển bytes sang HEX string để log"""
    if len(data) <= max_bytes:
        return " ".join(f"{b:02X}" for b in data)
    else:
        hex_str = " ".join(f"{b:02X}" for b in data[:max_bytes])
        return f"{hex_str} ... ({len(data)} bytes total)"

def handle_client(conn, addr):
    print(f"[CONNECTED] Client connected from {addr}")
    buffer = b""
    try:
        while not shutdown_flag.is_set():
            # Đọc dữ liệu với timeout
            conn.settimeout(1.0)
            try:
                data = conn.recv(4096)
                if not data:
                    print(f"[DISCONNECTED] Client {addr} closed connection")
                    break
                
                # Log toàn bộ dữ liệu nhận được
                print(f"\n{'='*60}")
                print(f"[RECEIVED] From {addr}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  Raw HEX: {bytes_to_hex(data)}")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")
                
                buffer += data
                
                # Xử lý từng dòng lệnh (phân tách bởi \r\n hoặc \n)
                while b"\r\n" in buffer or (b"\n" in buffer and b"\r\n" not in buffer):
                    if b"\r\n" in buffer:
                        line, buffer = buffer.split(b"\r\n", 1)
                    else:
                        line, buffer = buffer.split(b"\n", 1)
                    
                    if not line:
                        continue
                    
                    try:
                        command = line.decode("ascii", errors="replace").strip()
                        print(f"\n[COMMAND] Processing: '{command}'")
                        
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
                            print(f"[WARNING] Unknown command: '{command}'")
                            response = "ERROR,UNKNOWN_COMMAND"
                        
                        if response:
                            # Phản hồi với \r\n như chương trình mong đợi
                            response_line = f"{response}\r\n"
                            conn.sendall(response_line.encode("ascii"))
                            print(f"[RESPONSE] Sent: '{response_line.strip()}'")
                            print(f"  HEX: {bytes_to_hex(response_line.encode('ascii'))}")
                    
                    except Exception as e:
                        print(f"[ERROR] Error processing command: {e}")
                        error_response = f"ERROR,{str(e)}\r\n"
                        conn.sendall(error_response.encode("ascii"))
                
            except socket.timeout:
                # Timeout là bình thường, tiếp tục vòng lặp
                continue
            except Exception as e:
                print(f"[ERROR] Error receiving data: {e}")
                break
                
    except Exception as e:
        print(f"[ERROR] Client handler error: {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] Client {addr} disconnected")

def input_listener():
    print("Nhấn 'q' rồi Enter để tắt server.")
    while not shutdown_flag.is_set():
        try:
            if sys.version_info >= (3, 0):
                # input() is blocking, but that's fine for this usage
                line = input()
            else:
                line = raw_input()
        except EOFError:
            break
        if line.strip().lower() == "q":
            shutdown_flag.set()
            print("[SHUTDOWN] Đã nhận lệnh tắt server.")
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    # Lấy địa chỉ IP thực tế của server
    if HOST == "0.0.0.0":
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "N/A"
        print(f"[STARTED] Fake Laser Server listening on {HOST}:{PORT}")
        print(f"[INFO] Server will accept connections on all interfaces")
        if local_ip != "N/A":
            print(f"[INFO] Local IP: {local_ip}:{PORT}")
    else:
        print(f"[STARTED] Fake Laser Server listening on {HOST}:{PORT}")
    print(f"[INFO] Ready to receive laser commands (GA, C2, NT, etc.)")
    print(f"[INFO] Press 'q' + Enter to shutdown\n")

    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()

    client_threads = []

    try:
        while not shutdown_flag.is_set():
            # Wait at most 1 second for connections, allows checking shutdown_flag
            server.settimeout(1)
            try:
                conn, addr = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
                client_threads.append(client_thread)
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down server.")
        shutdown_flag.set()
    finally:
        print("[SHUTDOWN] Closing server socket and waiting for client threads...")
        server.close()
        for t in client_threads:
            t.join()
        print("[STOPPED] Server exited cleanly.")

if __name__ == "__main__":
    main()
