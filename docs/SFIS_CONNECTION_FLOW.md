# SFIS Connection Flow - Luồng Kết Nối và Gửi Dữ Liệu

## 📊 Kiến Trúc Tổng Quan

```
┌─────────────────────────────────────────────────────────────┐
│                         GUI Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TopControlPanel.py                                   │  │
│  │  - SFIS ON/OFF Button                                │  │
│  │  - COM Port Selector (COM1, COM2, COM3...)          │  │
│  │  - Signal: sfisConnectRequested(bool, str)          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Presenter Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MainPresenter                                        │  │
│  │  - Nhận signal từ TopControlPanel                    │  │
│  │  - Gọi SFISPresenter.connect(portName)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SFISPresenter                                        │  │
│  │  - Quản lý SFISWorker (COM port)                    │  │
│  │  - Quản lý SFISModel (tạo/parse message)            │  │
│  │  - Quản lý StartSignalWorker (gửi START)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Worker Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SFISWorker (QThread)                                │  │
│  │  - Sử dụng PySerial                                  │  │
│  │  - Kết nối COM port                                  │  │
│  │  - Gửi/nhận dữ liệu                                  │  │
│  │  - Config: baudrate=9600, timeout=5s                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Hardware Layer                          │
│                      COM Port (RS232)                        │
│                           ↓                                  │
│                      SFIS System                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 Flow 1: Kết Nối SFIS

### Bước 1: User Click "SFIS OFF" Button
```python
# gui/TopControlPanel.py
def _onSfisButtonToggled(self, checked):
    port_name = self.combo_sfis_com.currentText()  # Lấy COM port (vd: "COM2")
    
    if checked:
        # Yêu cầu kết nối
        self.sfisConnectRequested.emit(True, port_name)
```

### Bước 2: MainPresenter Nhận Signal
```python
# presenter/main_presenter.py
def onSfisConnectRequested(self, shouldConnect, portName):
    topPanel = self.main_window.getTopPanel()
    
    if shouldConnect:
        # Kết nối SFIS
        success = self.sfis_presenter.connect(portName)
        topPanel.setSFISConnectionStatus(success, "Connected" if success else "Failed")
```

### Bước 3: SFISPresenter Gọi Worker
```python
# presenter/sfis_presenter.py
def connect(self, portName):
    log.info(f"Đang kết nối SFIS qua {portName}...")
    
    # Gọi worker để kết nối COM port
    success = self.sfis_worker.connect(portName)
    
    if success:
        self.currentPort = portName
        log.info(f"Kết nối SFIS thành công: {portName}")
    
    return success
```

### Bước 4: SFISWorker Kết Nối COM Port
```python
# workers/sfis_worker.py
def connect(self, port_name=None, baudrate=None):
    if port_name:
        self.port_name = port_name  # Lưu port name từ UI
    
    # Mở kết nối COM port bằng PySerial
    self.serial_port = serial.Serial(
        port=self.port_name,        # "COM2" từ TopControlPanel
        baudrate=9600,              # Cố định
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=5.0,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    
    self.is_connected = True
    self.connectionStatusChanged.emit(True)
    return True
```

## 📤 Flow 2: Gửi START Signal

### Bước 1: User Click "START" Button
```python
# gui/LeftControlPanel.py
self.btn_start.clicked.connect(self.startClicked.emit)
```

### Bước 2: MainPresenter Xử Lý
```python
# presenter/main_presenter.py
def onStartClicked(self):
    # Kiểm tra kết nối
    if not self.sfis_presenter.isConnected:
        log.error("SFIS not connected")
        return
    
    # Gửi START signal (MO từ config.yaml)
    success = self.sfis_presenter.sendStartSignal()
```

### Bước 3: SFISPresenter Tạo Message
```python
# presenter/sfis_presenter.py
def sendStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
    # Tạo START signal từ Model
    start_message = self.sfis_model.createStartSignal(mo, all_parts_no, panel_no)
    
    # Log chi tiết
    log.info(f"Message: '{start_message}'")
    log.info(f"Length: {len(start_message)} bytes")
    
    # Invoke worker để gửi
    QMetaObject.invokeMethod(
        self.start_worker,
        "send_start_signal",
        Qt.QueuedConnection,
        Q_ARG(str, start_message)
    )
```

### Bước 4: SFISModel Tạo Message
```python
# model/sfis_model.py
def createStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
    # Đọc MO từ config.yaml
    if not mo:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            mo = config.get('MO', '')  # "2790004761"
    
    # Tạo message: MO(20) + Panel(20) + NEEDPSN08(9) = 49 bytes
    mo_padded = str(mo).ljust(20)[:20]
    panel_padded = "".ljust(20)
    need_keyword = "NEEDPSN08"
    
    start_signal = f"{mo_padded}{panel_padded}{need_keyword}"
    return start_signal
```

### Bước 5: StartSignalWorker Gửi Qua COM
```python
# workers/start_signal_worker.py
def send_start_signal(self, start_message):
    log.info(f"Sending: '{start_message}'")
    log.info(f"HEX: {start_message.encode('ascii').hex()}")
    
    # Gửi qua SFISWorker (đã kết nối COM port)
    success = self.sfis_worker.send_data(start_message)
    
    if success:
        log.info("✓ START signal sent successfully")
        self.signal_sent.emit(True, "Success")
```

### Bước 6: SFISWorker Gửi Qua PySerial
```python
# workers/sfis_worker.py
def send_data(self, data):
    # Chuyển string sang bytes
    data_bytes = data.encode('ascii')
    
    # Gửi qua COM port bằng PySerial
    self.serial_port.write(data_bytes)
    self.serial_port.flush()
    
    return True
```

## ⚙️ Cấu Hình COM Port

### Từ GUI (TopControlPanel.py):
```python
# Danh sách COM port
self.combo_sfis_com.addItems(["COM2", "COM1", "COM3", "COM4", "COM5"])

# User chọn port → emit signal
self.combo_sfis_com.currentTextChanged.connect(self.sfisChanged.emit)
```

### Trong SFISWorker:
```python
# Cấu hình mặc định
self.port_name = "COM2"      # Sẽ được override từ UI
self.baudrate = 9600         # Cố định
self.timeout = 5.0           # Cố định

# PySerial config
serial.Serial(
    port=self.port_name,        # Từ TopControlPanel
    baudrate=9600,              # Cố định
    bytesize=serial.EIGHTBITS,  # 8 bits
    parity=serial.PARITY_NONE,  # No parity
    stopbits=serial.STOPBITS_ONE, # 1 stop bit
    timeout=5.0,                # 5 seconds
    xonxoff=False,              # No software flow control
    rtscts=False,               # No hardware flow control
    dsrdtr=False                # No DSR/DTR
)
```

## 📋 Tóm Tắt

### Kết Nối:
1. User chọn COM port trong `TopControlPanel` (vd: COM2)
2. User click "SFIS OFF" → Button toggle
3. `TopControlPanel` emit `sfisConnectRequested(True, "COM2")`
4. `MainPresenter` nhận signal → gọi `sfis_presenter.connect("COM2")`
5. `SFISPresenter` gọi `sfis_worker.connect("COM2")`
6. `SFISWorker` dùng **PySerial** mở COM port
7. Kết nối thành công → Button hiển thị "SFIS ON" (màu xanh)

### Gửi START Signal:
1. User click "START" button
2. `MainPresenter` gọi `sfis_presenter.sendStartSignal()`
3. `SFISPresenter` gọi `sfis_model.createStartSignal()`
4. `SFISModel` đọc MO từ `config.yaml` → tạo message 49 bytes
5. `StartSignalWorker` nhận message → gọi `sfis_worker.send_data()`
6. `SFISWorker` dùng **PySerial** gửi qua COM port
7. Log hiển thị chi tiết message (ASCII + HEX)

## 🔧 File Liên Quan

- **GUI**: `gui/TopControlPanel.py` - Chọn COM port
- **Presenter**: `presenter/sfis_presenter.py` - Điều phối
- **Worker**: `workers/sfis_worker.py` - **PySerial COM port**
- **Worker**: `workers/start_signal_worker.py` - Gửi START signal
- **Model**: `model/sfis_model.py` - Tạo message format
- **Config**: `config.yaml` - MO number

## ✅ Kiểm Tra

### Log khi kết nối:
```
[INFO] Đang kết nối SFIS qua COM2...
[INFO] Serial port opened successfully: COM2
[INFO] Kết nối SFIS thành công: COM2
```

### Log khi gửi START:
```
[INFO] CHECK TÍN HIỆU TRƯỚC KHI GỬI:
[INFO]   MO: '2790004761' (padded to 20)
[INFO]   Panel: '' (empty, 20 spaces)
[INFO]   Message Length: 49 bytes (expected: 49)
[INFO]   Message: '2790004761                              NEEDPSN08'
[INFO] WORKER: Preparing to send START signal
[INFO] ✓ START signal sent successfully via COM port
```

