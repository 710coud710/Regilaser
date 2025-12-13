from pymcprotocol import Type3E


class DominatePLC:
    def __init__(self, ip="10.153.227.100", port=5007, timeout=2):
        self.ip = ip
        self.port = port
        self.timeout = timeout

        self.plc = Type3E()
        self.plc.soc_timeout = self.timeout
        self.connected = False

    def connect(self):
        if not self.connected:
            self.plc.connect(self.ip, self.port)
            self.connected = True

    def disconnect(self):
        if self.connected:
            self.plc.close()
            self.connected = False

    def readPLCRegister(self, device, count=1):
        """
        Đọc thanh ghi WORD (D, W, R...)
        """
        if not self.connected:
            raise RuntimeError("PLC is not connected")

        try:
            values = self.plc.batchread_wordunit(device, count)
            return values
        except Exception as e:
            raise RuntimeError(f"PLC read error: {e}")

if __name__ == "__main__":
    plc = DominatePLC()
    plc.connect()
    values = plc.readPLCRegister("D100", 1)
    print(values)

    plc.disconnect()
