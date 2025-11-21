# Hướng dẫn Triển khai SFIS Communication

## Tổng quan

Hệ thống đã được triển khai theo kiến trúc **MVP (Model-View-Presenter)** để giao tiếp với SFIS qua COM port.

## Cấu trúc Module

```
Regilazi/
├── model/
│   ├── __init__.py
│   └── sfis_model.py          # Logic nghiệp vụ SFIS
├── workers/
│   ├── __init__.py
│   └── sfis_worker.py         # Xử lý COM port
├── presenter/
│   ├── __init__.py
│   └── main_presenter.py      # Điều phối View-Model
├── gui/
│   └── ...                    # Các component giao diện
└── main.py                    # Entry point
```

## 1. SFIS Worker (`workers/sfis_worker.py`)

### Chức năng
- Xử lý giao tiếp serial COM port với SFIS
- Chạy trong thread riêng để không block UI
- Hỗ trợ đọc/ghi dữ liệu với timeout

### Cấu hình mặc định
```python
Port: COM2
Baudrate: 9600
Data bits: 8
Stop bits: 1
Parity: None
Timeout: 5s
```

### Các method chính

#### `connect(port_name, baudrate)`
Kết nối đến SFIS qua COM port.

**Tham số:**
- `port_name` (str): Tên COM port (vd: "COM2")
- `baudrate` (int): Tốc độ baud (mặc định: 9600)

**Returns:** `bool` - True nếu kết nối thành công

**Signals:**
- `connectionStatusChanged(bool)` - Thông báo trạng thái kết nối

#### `send_data(data)`
Gửi dữ liệu đến SFIS.

**Tham số:**
- `data` (str): Dữ liệu cần gửi (sẽ được encode sang ASCII)

**Returns:** `bool` - True nếu gửi thành công

#### `read_data(expected_length, timeout_ms)`
Đọc dữ liệu từ SFIS.

**Tham số:**
- `expected_length` (int): Độ dài dữ liệu mong đợi (None = đọc tất cả)
- `timeout_ms` (int): Thời gian timeout (milliseconds)

**Returns:** `str` - Dữ liệu nhận được, hoặc None nếu lỗi

**Signals:**
- `data_received(str)` - Dữ liệu đã nhận được

#### `send_and_wait(data, expected_length, timeout_ms)`
Gửi dữ liệu và chờ phản hồi.

**Returns:** `str` - Dữ liệu phản hồi

## 2. SFIS Model (`model/sfis_model.py`)

### Chức năng
- Xử lý logic nghiệp vụ SFIS
- Parse và validate dữ liệu
- Tạo các message theo định dạng SFIS

### Data Structure: `SFISData`

```python
@dataclass
class SFISData:
    # Request data
    mo: str                    # Manufacturing Order (20 bytes)
    all_parts_no: str          # ALL PARTS NO (12 bytes)
    panel_no: str              # Panel Number (20 bytes)
    
    # Response data (định dạng mới)
    laser_sn: str              # Laser SN (25 bytes)
    security_code: str         # Security Code (25 bytes)
    status: str                # Status (20 bytes)
    
    # Response data (định dạng cũ)
    psn_list: List[str]        # List of PSN (10 items)
```

### Các method chính

#### `parse_response_new_format(response)`
Parse phản hồi SFIS định dạng mới.

**Format:** `LaserSN(25) + SecurityCode(25) + Status(20) + PASS(4)`

**Ví dụ:** `"GR93J80034260001         52-005353                00S0PASS"`

**Returns:** `SFISData` - Dữ liệu đã parse

**Signals:**
- `data_parsed(SFISData)` - Dữ liệu đã parse thành công
- `validation_error(str)` - Lỗi validation

#### `create_request_psn(mo, all_parts_no, panel_no)`
Tạo request yêu cầu PSN (định dạng cũ).

**Format:** `MO(20) + AllPar_NO(12) + PANEL_NO(20) + NEED(4) + PSN10(5)`

**Returns:** `str` - Request string (61 bytes)

#### `create_test_complete(mo, panel_no)`
Tạo message báo hoàn thành test.

**Format:** `MO(20) + PANEL_NO(20) + END(3)`

**Returns:** `str` - Message string (43 bytes)

#### `create_test_error(mo, panel_no, error_code)`
Tạo message báo lỗi test.

**Format:** `MO(20) + PANEL_NO(20) + END(3) + ErrorCode(6)`

**Returns:** `str` - Message string (49 bytes)

## 3. Main Presenter (`presenter/main_presenter.py`)

### Chức năng
- Điều phối giữa View (GUI) và Model (Logic)
- Quản lý luồng công việc
- Xử lý events từ UI
- Cập nhật UI với kết quả

### Quy trình xử lý khi nhấn START

```
1. User nhấn nút START
   ↓
2. Presenter.on_start_clicked()
   ↓
3. Kiểm tra kết nối SFIS
   ↓
4. Validate dữ liệu đầu vào (MO, ALL PARTS SN)
   ↓
5. Gửi request/trigger đến SFIS
   ↓
6. Đợi nhận dữ liệu từ SFIS (timeout 5s)
   ↓
7. Parse dữ liệu (LaserSN, SecurityCode, Status)
   ↓
8. Cập nhật log và hiển thị kết quả
   ↓
9. Tiếp tục quy trình (laser marking, etc.)
```

### Các method chính

#### `initialize()`
Khởi tạo hệ thống và kết nối SFIS.

#### `on_start_clicked()`
Xử lý khi user nhấn nút START.

**Quy trình:**
1. Kiểm tra hệ thống đang chạy
2. Kiểm tra kết nối SFIS
3. Validate dữ liệu đầu vào
4. Bắt đầu giao tiếp SFIS

#### `start_sfis_communication(mo, all_parts_sn)`
Bắt đầu giao tiếp với SFIS.

**Tham số:**
- `mo` (str): Manufacturing Order
- `all_parts_sn` (str): ALL PARTS Serial Number

#### `on_sfis_data_received(data)`
Xử lý khi nhận được dữ liệu từ SFIS.

#### `on_data_parsed(sfis_data)`
Xử lý khi dữ liệu đã được parse thành công.

#### `send_test_complete()`
Gửi thông báo hoàn thành test đến SFIS.

#### `send_test_error(error_code)`
Gửi thông báo lỗi test đến SFIS.

## 4. Cách sử dụng

### Khởi động ứng dụng

```python
# main.py
app = QApplication(sys.argv)
window = MainWindow()
presenter = MainPresenter(window)
presenter.initialize()
window.show()
app.exec()
```

### Thay đổi COM port SFIS

1. Chọn COM port từ dropdown trong TopControlPanel
2. Presenter tự động ngắt kết nối cũ và kết nối lại

### Quy trình test

1. Nhập MO vào TopControlPanel (nếu cần)
2. Nhập ALL PARTS SN (nếu checkbox được chọn)
3. Nhấn nút **START** trong LeftControlPanel
4. Hệ thống tự động:
   - Kết nối SFIS (nếu chưa kết nối)
   - Gửi request/đợi dữ liệu
   - Parse và hiển thị kết quả
   - Log toàn bộ quá trình

### Xem log

Log được hiển thị trong `LogDisplay` với các level:
- **INFO**: Thông tin chung
- **SUCCESS**: Thành công
- **WARNING**: Cảnh báo
- **ERROR**: Lỗi
- **DEBUG**: Debug info

## 5. Signals và Events

### View → Presenter

| Signal | Source | Handler |
|--------|--------|---------|
| `start_clicked` | LeftControlPanel | `on_start_clicked()` |
| `sfis_changed` | TopControlPanel | `on_sfis_port_changed()` |

### Worker → Presenter

| Signal | Source | Handler |
|--------|--------|---------|
| `data_received` | SFISWorker | `on_sfis_data_received()` |
| `error_occurred` | SFISWorker | `on_sfis_error()` |
| `connectionStatusChanged` | SFISWorker | `on_sfis_connection_changed()` |

### Model → Presenter

| Signal | Source | Handler |
|--------|--------|---------|
| `data_parsed` | SFISModel | `on_data_parsed()` |
| `validation_error` | SFISModel | `on_validation_error()` |

### Presenter → View

| Signal | Target | Purpose |
|--------|--------|---------|
| `logMessage` | LogDisplay | Hiển thị log |
| `status_changed` | StatusBar | Cập nhật status |
| `test_result` | ResultDisplay | Hiển thị kết quả |

## 6. Xử lý lỗi

### Lỗi kết nối
```python
# Worker emit signal
error_occurred.emit("Lỗi kết nối SFIS: [COM2] could not be opened")

# Presenter xử lý
def on_sfis_error(self, error_msg):
    self.logMessage.emit(f"SFIS Error: {error_msg}", "ERROR")
```

### Lỗi timeout
```python
# Worker trả về None khi timeout
response = self.sfis_worker.read_data(expected_length=70, timeout_ms=5000)
if not response:
    self.logMessage.emit("Timeout đọc dữ liệu SFIS", "ERROR")
```

### Lỗi validation
```python
# Model emit signal
validation_error.emit("Response quá ngắn: 50 < 70")

# Presenter xử lý
def on_validation_error(self, error_msg):
    self.logMessage.emit(f"Validation Error: {error_msg}", "ERROR")
```

## 7. Testing

### Test kết nối SFIS
```python
# Trong presenter
presenter.connect_sfis("COM2")
# Kiểm tra log: "Kết nối SFIS thành công: COM2"
```

### Test gửi/nhận dữ liệu
```python
# Gửi dữ liệu test
presenter.sfis_worker.send_data("TEST_DATA")

# Đọc dữ liệu
response = presenter.sfis_worker.read_data(timeout_ms=5000)
print(response)
```

### Test parse dữ liệu
```python
# Parse định dạng mới
test_data = "GR93J80034260001         52-005353                00S0PASS"
parsed = presenter.sfis_model.parse_response_new_format(test_data)
print(f"Laser SN: {parsed.laser_sn}")
print(f"Security Code: {parsed.security_code}")
```

## 8. Mở rộng

### Thêm định dạng SFIS mới
1. Thêm constants vào `SFISModel`
2. Tạo method parse mới: `parse_response_xxx()`
3. Cập nhật `on_sfis_data_received()` để xử lý

### Thêm thiết bị mới (PLC, Laser, CCD)
1. Tạo Worker mới: `plc_worker.py`, `laser_worker.py`
2. Tạo Model mới: `plc_model.py`, `laser_model.py`
3. Tích hợp vào `MainPresenter`
4. Kết nối signals

### Thêm chức năng log vào file
```python
# Trong LogDisplay
def save_to_file(self, filepath):
    with open(filepath, 'w') as f:
        f.write(self.log_view.toPlainText())
```

## 9. Troubleshooting

### COM port không mở được
- Kiểm tra port có đang được sử dụng bởi app khác
- Kiểm tra quyền truy cập
- Thử port khác

### Không nhận được dữ liệu
- Kiểm tra baudrate đúng (9600)
- Kiểm tra cable kết nối
- Tăng timeout
- Kiểm tra SFIS có gửi dữ liệu không

### Parse lỗi
- Kiểm tra độ dài response
- Kiểm tra format có đúng không
- Log raw data để debug

## 10. Dependencies

```
PySide6>=6.4.0
pySerial>=3.5
```

Cài đặt:
```bash
pip install -r requirements.txt
```

