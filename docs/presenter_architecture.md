# Kiến trúc Presenter - Modular Design

## Tổng quan

Hệ thống Presenter đã được tách thành nhiều module nhỏ, mỗi module chịu trách nhiệm xử lý một phần cụ thể của hệ thống.

## Cấu trúc Module

```
presenter/
├── __init__.py                 # Export tất cả presenters
├── base_presenter.py           # Base class cho tất cả presenters
├── main_presenter.py           # Presenter chính - điều phối
├── sfis_presenter.py           # Xử lý SFIS communication
├── plc_presenter.py            # Xử lý PLC communication
├── laser_presenter.py          # Xử lý Laser Marking
└── ccd_presenter.py            # Xử lý CCD Camera
```

## 1. BasePresenter (`base_presenter.py`)

### Mục đích
- Base class cho tất cả các presenter
- Cung cấp các method chung: logging, status update

### Signals
- `logMessage(str, str)` - (message, level)
- `status_changed(str)` - Status text

### Methods
```python
log_info(message)       # Log INFO
log_success(message)    # Log SUCCESS
log_warning(message)    # Log WARNING
log_error(message)      # Log ERROR
log_debug(message)      # Log DEBUG
update_status(text)     # Cập nhật status bar
cleanup()               # Dọn dẹp tài nguyên
```

## 2. SFISPresenter (`sfis_presenter.py`)

### Mục đích
- Xử lý toàn bộ logic giao tiếp SFIS
- Quản lý SFIS Worker và Model
- Chạy trong QThread riêng

### Signals
- `logMessage(str, str)` - Log messages
- `connection_status_changed(bool)` - Trạng thái kết nối
- `data_ready(SFISData)` - Dữ liệu đã sẵn sàng

### Methods chính

#### `connect(port_name)`
Kết nối đến SFIS qua COM port.

**Returns:** `bool` - True nếu thành công

#### `disconnect()`
Ngắt kết nối SFIS.

**Returns:** `bool` - True nếu thành công

#### `request_data(mo, all_parts_sn)`
Yêu cầu dữ liệu từ SFIS.

**Returns:** `str` - Response data hoặc None

#### `parse_response(response)`
Parse response từ SFIS.

**Returns:** `SFISData` - Dữ liệu đã parse

#### `send_test_complete(mo, panel_no)`
Gửi thông báo hoàn thành test.

**Returns:** `bool` - True nếu thành công

#### `send_test_error(mo, panel_no, error_code)`
Gửi thông báo lỗi test.

**Returns:** `bool` - True nếu thành công

### Ví dụ sử dụng
```python
sfis = SFISPresenter()
sfis.connect("COM2")
response = sfis.request_data()
data = sfis.parse_response(response)
sfis.send_test_complete(data.mo, data.panel_no)
```

## 3. PLCPresenter (`plc_presenter.py`)

### Mục đích
- Xử lý giao tiếp với PLC
- Gửi/nhận tín hiệu điều khiển

### Methods chính

#### `connect(port_name)`
Kết nối đến PLC (mặc định COM3).

#### `send_command(command)`
Gửi lệnh đến PLC.

#### `wait_for_signal(expected_signal, timeout_ms)`
Chờ tín hiệu từ PLC.

#### Các lệnh cụ thể
```python
send_laser_ok()     # Gửi L_OK
send_laser_ng()     # Gửi L_NG
send_check_ok()     # Gửi CHE_OK
send_check_ng()     # Gửi CHE_NG
```

### Ví dụ sử dụng
```python
plc = PLCPresenter()
plc.connect("COM3")
signal = plc.wait_for_signal("START1", 5000)
plc.send_laser_ok()
```

## 4. LaserPresenter (`laser_presenter.py`)

### Mục đích
- Xử lý giao tiếp với Laser Marking System
- Điều khiển laser marking qua TCP/IP

### Methods chính

#### `connect(ip_address, port)`
Kết nối đến Laser System (mặc định 192.168.1.20:50002).

#### `activate_script(script_number)`
Kích hoạt script laser (GA command).

#### `set_content(script, block, content)`
Đặt nội dung cho block (C2 command).

#### `start_marking()`
Bắt đầu laser marking (NT command).

#### `mark_psn(script, security_code)`
Thực hiện laser marking PSN (quy trình đầy đủ).

### Ví dụ sử dụng
```python
laser = LaserPresenter()
laser.connect("192.168.1.20", 50002)
laser.mark_psn("1", "52-005353")
```

## 5. CCDPresenter (`ccd_presenter.py`)

### Mục đích
- Xử lý giao tiếp với CCD Camera
- Giải mã và verify barcode/QR code

### Methods chính

#### `connect(port_name)`
Kết nối đến CCD Camera.

#### `decode(timeout_ms)`
Yêu cầu CCD giải mã.

**Returns:** `(bool, str)` - (success, decoded_string)

#### `verify_code(expected_code)`
Giải mã và verify với code mong đợi.

**Returns:** `bool` - True nếu khớp

### Ví dụ sử dụng
```python
ccd = CCDPresenter()
ccd.connect("COM4")
success = ccd.verify_code("52-005353")
```

## 6. MainPresenter (`main_presenter.py`)

### Mục đích
- Điều phối tất cả các presenter con
- Quản lý luồng công việc chính
- Kết nối với View (GUI)

### Khởi tạo
```python
class MainPresenter(QObject):
    def __init__(self, main_window):
        # Khởi tạo các presenter con
        self.sfis_presenter = SFISPresenter()
        self.plc_presenter = PLCPresenter()
        self.laser_presenter = LaserPresenter()
        self.ccd_presenter = CCDPresenter()
```

### Quy trình test chính

```python
def start_test_process(self, mo, all_parts_sn):
    """
    Quy trình test đầy đủ:
    1. Nhận dữ liệu từ SFIS
    2. Laser marking
    3. Verify bằng CCD
    4. Gửi kết quả về SFIS và PLC
    """
```

### Signal Flow

```
View (GUI)
    ↓ (user action)
MainPresenter
    ↓ (delegate)
SubPresenter (SFIS/PLC/Laser/CCD)
    ↓ (worker/model)
Hardware
    ↓ (response)
SubPresenter
    ↓ (signal)
MainPresenter
    ↓ (forward)
View (update UI)
```

## Lợi ích của kiến trúc modular

### 1. **Separation of Concerns**
- Mỗi presenter chỉ xử lý một phần cụ thể
- Dễ hiểu, dễ maintain

### 2. **Reusability**
- Có thể tái sử dụng presenter độc lập
- Ví dụ: SFISPresenter có thể dùng trong project khác

### 3. **Testability**
- Test từng presenter riêng biệt
- Mock dependencies dễ dàng

### 4. **Scalability**
- Thêm presenter mới không ảnh hưởng code cũ
- Ví dụ: Thêm `FixturePresenter`, `DatabasePresenter`

### 5. **Parallel Development**
- Nhiều dev có thể làm việc trên các presenter khác nhau
- Ít conflict code

## Cách thêm Presenter mới

### Bước 1: Tạo file presenter mới
```python
# presenter/new_device_presenter.py
from presenter.base_presenter import BasePresenter

class NewDevicePresenter(BasePresenter):
    def __init__(self):
        super().__init__()
        # Khởi tạo worker, model
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def cleanup(self):
        pass
```

### Bước 2: Thêm vào MainPresenter
```python
# presenter/main_presenter.py
from presenter.new_device_presenter import NewDevicePresenter

class MainPresenter(QObject):
    def __init__(self, main_window):
        # ...
        self.new_device_presenter = NewDevicePresenter()
        
    def _connect_signals(self):
        # Kết nối signals
        self.new_device_presenter.logMessage.connect(self._forward_log)
```

### Bước 3: Export trong __init__.py
```python
# presenter/__init__.py
from presenter.new_device_presenter import NewDevicePresenter

__all__ = [
    # ...
    'NewDevicePresenter',
]
```

## Best Practices

### 1. Luôn kế thừa BasePresenter
```python
class MyPresenter(BasePresenter):
    def __init__(self):
        super().__init__()
```

### 2. Sử dụng log methods từ base
```python
self.log_info("Connecting...")
self.log_success("Connected")
self.log_error("Connection failed")
```

### 3. Emit signals để communicate
```python
# Trong presenter con
self.data_ready.emit(data)

# MainPresenter subscribe
sub_presenter.data_ready.connect(self.on_data_ready)
```

### 4. Cleanup đúng cách
```python
def cleanup(self):
    if self.is_connected:
        self.disconnect()
    if self.thread:
        self.thread.quit()
        self.thread.wait()
```

### 5. Error handling
```python
try:
    result = self.do_something()
    if result:
        self.log_success("Success")
    else:
        self.log_error("Failed")
except Exception as e:
    self.log_error(f"Error: {str(e)}")
```

## Tóm tắt

| Presenter | Chức năng | Thread | Hardware |
|-----------|-----------|--------|----------|
| BasePresenter | Base class | - | - |
| MainPresenter | Điều phối | Main | - |
| SFISPresenter | SFIS comm | QThread | COM2 |
| PLCPresenter | PLC comm | TODO | COM3 |
| LaserPresenter | Laser marking | TODO | TCP/IP |
| CCDPresenter | CCD camera | TODO | COM port |

## Roadmap

- [ ] Implement PLCPresenter với worker/model
- [ ] Implement LaserPresenter với TCP/IP worker
- [ ] Implement CCDPresenter với worker/model
- [ ] Thêm unit tests cho từng presenter
- [ ] Thêm integration tests cho quy trình đầy đủ
- [ ] Thêm logging vào file
- [ ] Thêm error recovery mechanisms

