import socket

FAKE_D = {
    100: 1234,
    101: 5678
}

def fake_plc():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 5007))
    s.listen(1)
    print("Fake PLC SLMP running...")

    conn, addr = s.accept()
    print("Client connected:", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            break

        # giả trả về dữ liệu
        conn.send(b"\xd0\x00\x00\x00")  # dummy response

fake_plc()
