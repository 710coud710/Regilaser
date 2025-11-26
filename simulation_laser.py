# fake_laser_server.py
import socket
import threading
import time
import sys

HOST = "10.153.227.38"
PORT = 50002

shutdown_flag = threading.Event()

def handle_client(conn, addr):
    print(f"[CONNECTED] {addr} connected")
    try:
        while not shutdown_flag.is_set():
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode().strip()
            print(f"[RECEIVED] {command} from {addr}")

            # Giả lập xử lý lệnh
            if command.startswith("GA,"):
                time.sleep(1)  # giả lập xử lý
                response = "GA,0\r\n"
            elif command.startswith("C2,"):
                time.sleep(2)
                response = "C2,0\r\n"
            elif command == "NT":
                time.sleep(3)
                response = "NT,0\r\n"
            else:
                response = "ERROR,UNKNOWN_COMMAND\r\n"

            conn.sendall(response.encode())
            print(f"[RESPONSE] {response.strip()} to {addr}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected")

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
    print(f"[STARTED] Fake Laser Server listening on {HOST}:{PORT}")

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
