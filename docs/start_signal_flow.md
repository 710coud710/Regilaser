# START Signal Flow - Luồng Gửi Tín Hiệu START

## Tổng Quan

Hệ thống gửi tín hiệu START đến SFIS qua COM port sử dụng kiến trúc **fire-and-forget** (gửi đi không chờ phản hồi) với QThread để xử lý bất đồng bộ.

## Kiến Trúc

```
User Click START Button
        ↓
MainPresenter.onStartClicked()
        ↓
SFISPresenter.sendStartSignal()
        ↓
SFISModel.createStartSignal() → Tạo message
        ↓
StartSignalWorker (QThread) → Gửi qua COM
        ↓
Signal: startSignalSent(success, message)
        ↓
MainPresenter.onStartSignalSent() → Cập nhật UI
```

## Các Thành Phần

### 1. StartSignalWorker (`workers/start_signal_worker.py`)

**Chức năng**: Worker chạy trong QThread riêng để gửi tín hiệu START qua COM port.

**Signals**:
- `signal_sent(bool, str)`: Phát ra khi đã gửi xong (success, message)
- `log_message(str, str)`: Log messages (message, level)

**Methods**:
- `send_start_signal(start_message)`: Gửi START signal (fire and forget)
- `is_running()`: Kiểm tra worker có đang xử lý không

**Đặc điểm**:
- Chạy trong thread riêng biệt
- Không block UI thread
- Không chờ phản hồi từ SFIS
- Thread-safe với flag `_is_running`

### 2. SFISModel (`model/sfis_model.py`)

**Method mới**: `createStartSignal(mo, all_parts_no, panel_no)`

**Format START Signal**:
```
MO(20 bytes) + AllPar_NO(12 bytes) + PANEL_NO(20 bytes) + "START"(5 bytes)
Total: 57 bytes
```

**Example**:
```
"MO12345             ALL123      PANEL001            START"
```

**Validation**:
- MO: Không rỗng, max 20 ký tự
- ALL PARTS NO: Không rỗng, max 12 ký tự
- PANEL NO: Không rỗng, max 20 ký tự

### 3. SFISPresenter (`presenter/sfis_presenter.py`)

**Thêm Signal**: `startSignalSent(bool, str)`

**Method mới**: `sendStartSignal(mo, all_parts_no, panel_no)`

**Luồng xử lý**:
1. Kiểm tra kết nối SFIS
2. Validate dữ liệu đầu vào
3. Tạo START message từ SFISModel
4. Invoke worker method trong thread của nó (QMetaObject.invokeMethod)
5. Worker gửi dữ liệu qua COM port
6. Worker phát signal khi hoàn tất
7. Presenter forward signal đến MainPresenter

**Thread Management**:
- `start_thread`: QThread riêng cho StartSignalWorker
- `sfis_thread`: QThread cho SFISWorker (đọc/ghi COM)

### 4. MainPresenter (`presenter/main_presenter.py`)

**Method cập nhật**: `onStartClicked()`

**Luồng xử lý**:
1. Kiểm tra hệ thống có đang chạy không
2. Kiểm tra kết nối SFIS
3. Lấy dữ liệu từ UI (MO, ALL PARTS SN)
4. Validate dữ liệu
5. Gọi `sfis_presenter.sendStartSignal()`
6. Log thông báo đang gửi
7. Đợi callback `onStartSignalSent()`

**Method mới**: `onStartSignalSent(success, message)`

**Xử lý kết quả**:
- Success: Log thành công, có thể tiếp tục các bước tiếp theo
- Failure: Log lỗi, reset trạng thái
- Reset `isRunning` flag

## Luồng Dữ Liệu Chi Tiết

### Bước 1: User Click START
```python
# LeftControlPanel.py
self.btn_start.clicked.connect(self.startClicked.emit)
```

### Bước 2: MainPresenter nhận signal
```python
# MainPresenter.onStartClicked()
mo = topPanel.getMO()              # Ví dụ: "MO12345"
allPartsSn = topPanel.getAllPartsSN()  # Ví dụ: "ALL123"
panel_no = mo  # Hoặc từ input khác

self.sfis_presenter.sendStartSignal(mo, allPartsSn, panel_no)
```

### Bước 3: SFISPresenter tạo message
```python
# SFISPresenter.sendStartSignal()
# Validate
valid_mo, msg = self.sfis_model.validateMo(mo)
valid_parts, msg = self.sfis_model.validateAllPartsNo(all_parts_no)
valid_panel, msg = self.sfis_model.validatePanelNo(panel_no)

# Tạo message
start_message = self.sfis_model.createStartSignal(mo, all_parts_no, panel_no)
# Result: "MO12345             ALL123      MO12345             START"
```

### Bước 4: Invoke worker trong thread
```python
# SFISPresenter.sendStartSignal()
QMetaObject.invokeMethod(
    self.start_worker,
    "send_start_signal",
    Qt.QueuedConnection,
    Q_ARG(str, start_message)
)
```

### Bước 5: Worker gửi qua COM
```python
# StartSignalWorker.send_start_signal()
success = self.sfis_worker.send_data(start_message)
self.signal_sent.emit(success, "START signal sent successfully")
```

### Bước 6: Callback cập nhật UI
```python
# MainPresenter.onStartSignalSent()
if success:
    self.logMessage.emit("✓ START signal đã được gửi đến SFIS", "SUCCESS")
else:
    self.logMessage.emit(f"✗ Gửi START signal thất bại", "ERROR")

self.isRunning = False
```

## Thread Safety

### QThread Architecture
```
Main Thread (UI)
    ├─ MainPresenter
    ├─ GUI Components
    └─ Signal connections

SFIS Thread
    └─ SFISWorker
        └─ Serial port operations

Start Signal Thread
    └─ StartSignalWorker
        └─ Send START signal
```

### Thread Communication
- **QueuedConnection**: Signals giữa threads tự động queue-based
- **Thread-safe**: Không có shared mutable state
- **Non-blocking**: UI thread không bao giờ bị block

## Error Handling

### Validation Errors
```python
if not mo or not allPartsSn:
    self.logMessage.emit("Vui lòng nhập đầy đủ MO và ALL PARTS SN", "ERROR")
    return
```

### Connection Errors
```python
if not self.sfis_presenter.isConnected:
    self.logMessage.emit("Chưa kết nối SFIS. Vui lòng bật SFIS trước.", "ERROR")
    return
```

### Send Errors
```python
# StartSignalWorker
except Exception as e:
    error_msg = f"Exception khi gửi START signal: {str(e)}"
    self.log_message.emit(error_msg, "ERROR")
    self.signal_sent.emit(False, error_msg)
```

## Ưu Điểm

1. **Non-blocking**: UI không bị đơ khi gửi dữ liệu
2. **Fire-and-forget**: Không cần chờ phản hồi từ SFIS
3. **Thread-safe**: Sử dụng Qt signals/slots mechanism
4. **Scalable**: Dễ dàng mở rộng thêm workers khác
5. **Maintainable**: Tách biệt rõ ràng giữa UI, Business Logic, và I/O

## Cấu Hình

### COM Port Settings
```python
# SFISWorker
self.port_name = "COM2"
self.baudrate = 9600
self.timeout = 5.0
```

### START Signal Format
```python
# SFISModel
MO_LENGTH = 20
ALL_PARTS_NO_LENGTH = 12
PANEL_NO_LENGTH = 20
START_KEYWORD = "START"  # 5 bytes
```

## Testing

### Test Case 1: Gửi START signal thành công
```
Input:
  - MO: "MO12345"
  - ALL PARTS SN: "ALL123"
  - Panel NO: "PANEL001"

Expected:
  - Message: "MO12345             ALL123      PANEL001            START"
  - Log: "✓ START signal đã được gửi đến SFIS"
  - Signal: startSignalSent(True, "START signal sent successfully")
```

### Test Case 2: Chưa kết nối SFIS
```
Input:
  - SFIS not connected

Expected:
  - Log: "Chưa kết nối SFIS. Vui lòng bật SFIS trước."
  - No signal sent
```

### Test Case 3: Dữ liệu không hợp lệ
```
Input:
  - MO: "" (empty)

Expected:
  - Log: "Validation error: MO không được để trống"
  - No signal sent
```

## Future Enhancements

1. **Retry Mechanism**: Tự động retry khi gửi thất bại
2. **Queue System**: Queue nhiều START signals
3. **Timeout Handling**: Xử lý timeout cho mỗi lần gửi
4. **Statistics**: Đếm số lần gửi thành công/thất bại
5. **Logging**: Ghi log chi tiết vào file

## Tham Khảo

- `docs/communication_protocols.md`: Chi tiết protocol SFIS
- `docs/presenter_architecture.md`: Kiến trúc Presenter pattern
- `workers/sfis_worker.py`: Implementation COM port worker

