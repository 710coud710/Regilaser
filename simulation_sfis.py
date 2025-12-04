"""
Giả lập SFIS Server để test giao tiếp SFIS:
- Lắng nghe trên cổng COM (RS232)
- Nhận START signal dạng: MO(20) + PANEL(20) + NEEDPSN{panel_num}
- Trả về response PSN dạng cũ, ví dụ:
  2792000196          PX5BF03CL           PT53QG0754670080    ... PASS
"""

import sys
import time
import threading
import re

import serial


# Cấu hình COM cho SFIS (phù hợp với cấu hình trong SFISWorker / config.yaml)
COM = "COM7"          # Đổi lại nếu bạn dùng cổng khác
BAUDRATE = 9600
TIMEOUT_S = 1.0

# Tham số định dạng — phải đồng bộ với SFISModel
MO_LENGTH = 20
PANEL_NO_LENGTH = 20
PSN_LENGTH = 20
PASS_KEYWORD = "PASS"


shutdown_flag = threading.Event()


def bytes_to_hex(data: bytes, max_bytes: int = 100) -> str:
    """Chuyển bytes sang HEX string để log"""
    if len(data) <= max_bytes:
        return " ".join(f"{b:02X}" for b in data)
    else:
        hex_str = " ".join(f"{b:02X}" for b in data[:max_bytes])
        return f"{hex_str} ... ({len(data)} bytes total)"


def _extract_panel_num(text: str) -> int:
    """Lấy số panel từ chuỗi NEEDPSNx (ví dụ NEEDPSN5 -> 5)."""
    m = re.search(r"NEEDPSN(\d+)", text.upper())
    if not m:
        return 1
    try:
        return max(1, int(m.group(1)))
    except ValueError:
        return 1


def build_psn_response(start_line: str) -> str:
    """
    Tạo response PSN từ START signal:
    - start_line: chuỗi ASCII đã strip() nhưng vẫn đủ 49+ ký tự
    - Số PSN trả về dựa vào NEEDPSNx (x = số panel)
    """
    mo_raw = start_line[:MO_LENGTH]
    mo = mo_raw.strip() or "2792000196"

    # Lấy số panel từ NEEDPSNx (NEEDPSN5 -> 5 PSN)
    panel_num = _extract_panel_num(start_line)

    # PANEL trong request thường để trống -> ta sinh panel_no giả lập giống mẫu
    panel_no = "PX5BF03CL"

    mo_padded = mo.ljust(MO_LENGTH)[:MO_LENGTH]
    panel_padded = panel_no.ljust(PANEL_NO_LENGTH)[:PANEL_NO_LENGTH]

    # Tạo list PSN giống mẫu: PT53QG0754670080, 81, 82...
    base_prefix = "PT53QG07546700"
    psn_list = []
    start_idx = 80  # bắt đầu từ ...80 như ví dụ
    for i in range(panel_num):
        suffix = start_idx + i
        psn_code = f"{base_prefix}{suffix:02d}"
        psn_list.append(psn_code.ljust(PSN_LENGTH)[:PSN_LENGTH])

    body = "".join(psn_list)
    response = f"{mo_padded}{panel_padded}{body}{PASS_KEYWORD}"
    return response


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
            text = line.decode("ascii", errors="replace").strip()
            print(f"\n[COMMAND from {peer_name}] '{text}'")

            response = None

            # Lệnh UNDO: chỉ log, không phản hồi
            if text.upper().startswith("UNDO"):
                print("[SFIS SIM] UNDO received (reset state)")

            # START signal: MO(20) + PANEL(20) + NEEDPSN{panel_num}
            elif "NEEDPSN" in text:
                print("[SFIS SIM] START signal (NEEDPSN...) detected")
                psn_response = build_psn_response(text)
                response = psn_response
            elif text.strip().endswith("END"):
                # Giả lập SFIS nhận test complete và trả về ENDPASS
                mo_raw = text[:MO_LENGTH]
                mo = mo_raw.strip()
                resp = f"{mo.ljust(MO_LENGTH)[:MO_LENGTH]}ENDPASS"
                resp_line = f"{resp}\r\n".encode("ascii", errors="ignore")
                send_func(resp_line)
                print(f"[SFIS SIM] END response -> '{resp}'")
            else:
                # Lệnh khác: log + trả về lỗi chung
                print(f"[SFIS SIM] Unknown command: '{text}'")
                response = "ERROR,UNKNOWN_CMD"

            if response is not None:
                resp_line = f"{response}\r\n".encode("ascii", errors="ignore")
                send_func(resp_line)
                print(f"[RESPONSE to {peer_name}] '{response}'")
                print(f"  HEX: {bytes_to_hex(resp_line)}")

        except Exception as e:
            print(f"[ERROR] Error processing command from {peer_name}: {e}")
            error_response = f"ERROR,{str(e)}\r\n".encode("ascii", errors="ignore")
            send_func(error_response)

    return buffer


def input_listener():
    print("Nhấn 'q' rồi Enter để tắt SFIS simulator.")
    while not shutdown_flag.is_set():
        try:
            line = input()
        except EOFError:
            break
        if line.strip().lower() == "q":
            shutdown_flag.set()
            print("[SHUTDOWN] Đã nhận lệnh tắt SFIS simulator.")
            break


def run_com_server():
    """Giả lập SFIS qua cổng COM (RS232)."""
    print(f"[STARTED] Fake SFIS COM Server on {COM} @ {BAUDRATE}bps")
    print("[INFO] Ready to receive SFIS START signal (NEEDPSN...) via RS232")
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
                    # Timeout bình thường, tiếp tục vòng lặp
                    continue

                print(f"\n{'=' * 60}")
                print(f"[RECEIVED COM] From {peer}:")
                print(f"  Length: {len(data)} bytes")
                print(f"  ASCII: {repr(data.decode('ascii', errors='replace'))}")

                buffer += data

                # Xử lý buffer thành các lệnh
                buffer = process_buffer(buffer, ser.write, peer)

            except Exception as e:
                print(f"[ERROR] COM receive error on {peer}: {e}")
                break
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] KeyboardInterrupt - shutting down SFIS COM server.")
        shutdown_flag.set()
    finally:
        print("[SHUTDOWN] Closing COM port...")
        try:
            ser.close()
        except Exception:
            pass
        print("[STOPPED] SFIS COM server exited cleanly.")


def main():
    run_com_server()


if __name__ == "__main__":
    main()


