# SFIS Data Receiving - Nhận Dữ Liệu Từ SFIS

## Tổng Quan

Hệ thống nhận **TẤT CẢ** dữ liệu từ SFIS qua COM port mà không giới hạn format hay độ dài. Mọi dữ liệu nhận được sẽ được hiển thị chi tiết trên log để phân tích.

## Đặc Điểm

### 1. Không Giới Hạn Format
- ✅ Không yêu cầu format cố định
- ✅ Không yêu cầu độ dài cố định
- ✅ Đọc tất cả dữ liệu có sẵn
- ✅ Tự động dừng khi không còn dữ liệu mới

### 2. Hiển Thị Chi Tiết
- ✅ Độ dài (bytes)
- ✅ Nội dung (text)
- ✅ Nội dung (HEX)
- ✅ Phân tích từng chunk 20 bytes
- ✅ Thử parse nếu có thể (không bắt buộc)

### 3. Thread-Safe
- ✅ Đọc dữ liệu trong QThread riêng
- ✅ Không block UI
- ✅ Signal tự động chuyển về main thread

## Flow

```
User Click START
    ↓
Gửi START signal (49 bytes)
    ↓
START signal sent successfully
    ↓
Tự động gọi receiveResponsePsn()
    ↓
SFISWorker.read_data_all(timeout=10s)
    ├─ Đọc liên tục từ COM port
    ├─ Không giới hạn độ dài
    ├─ Dừng khi không còn dữ liệu mới (100ms)
    └─ Emit data_received signal
    ↓
SFISPresenter.onDataReceived(data)
    ├─ Log chi tiết: length, text, HEX
    ├─ Phân tích từng chunk 20 bytes
    ├─ Hiển thị trên UI
    └─ Thử parse (không bắt buộc)
```

## Code Reference

### 1. SFISWorker.read_data_all()

```python
@Slot(int)
def read_data_all(self, timeout_ms=10000):
    """
    Đọc TẤT CẢ dữ liệu có sẵn từ SFIS
    Không giới hạn độ dài
    """
    data_bytes = b''
    no_data_count = 0
    max_no_data_count = 10  # 100ms
    
    while time.time() - start_time < timeout_sec:
        if self.serial_port.in_waiting > 0:
            # Đọc tất cả dữ liệu có sẵn
            chunk = self.serial_port.read(self.serial_port.in_waiting)
            data_bytes += chunk
            no_data_count = 0
        else:
            no_data_count += 1
            if len(data_bytes) > 0 and no_data_count >= max_no_data_count:
                # Đã có dữ liệu và không còn dữ liệu mới → dừng
                break
            time.sleep(0.01)
    
    # Convert to text
    data_str = data_bytes.decode('ascii', errors='ignore')
    
    # Emit signal
    self.data_received.emit(data_str)
    return data_str
```

### 2. SFISPresenter.onDataReceived()

```python
def onDataReceived(self, data):
    """
    Hiển thị TẤT CẢ dữ liệu nhận được
    """
    # Log chi tiết
    log.info("=" * 70)
    log.info("DATA RECEIVED FROM SFIS")
    log.info(f"Length: {len(data)} bytes")
    log.info(f"Data (text): '{data}'")
    log.info(f"Data (HEX):  {data.encode('ascii').hex()}")
    
    # Phân tích từng 20 bytes
    for i in range(0, len(data), 20):
        chunk = data[i:i+20]
        log.info(f"  [{i:3d}-{i+len(chunk)-1:3d}] '{chunk}'")
    
    # Hiển thị trên UI
    self.logMessage.emit(f"✓ RECEIVED DATA FROM SFIS", "SUCCESS")
    self.logMessage.emit(f"  Length: {len(data)} bytes", "INFO")
    self.logMessage.emit(f"  Data: {data}", "INFO")
    
    # Thử parse (không bắt buộc)
    try:
        parsedData = self.sfis_model.parseResponsePsn(data)
        if parsedData:
            # Hiển thị parsed data
            ...
    except:
        # Parse failed, không sao
        pass
```

## Log Output Example

### Terminal Log

```
======================================================================
DATA RECEIVED FROM SFIS
======================================================================
Length: 144 bytes
Data (text): '2790004761          PANEL001            PSN001              PSN002              PSN003              PSN004              PSN005              PASS'
Data (HEX):  323739303030343736312020202020202020202020202050414e454c30303120202020202020202020202050534e303031202020202020202020202020202050534e303032202020202020202020202020202050534e303033202020202020202020202020202050534e303034202020202020202020202020202050534e30303520202020202020202020202020204041535320
----------------------------------------------------------------------
DETAILED BREAKDOWN (20-byte chunks):
  [  0- 19] '2790004761          ' (HEX: 32373930303034373631202020202020202020202020)
  [ 20- 39] 'PANEL001            ' (HEX: 50414e454c30303120202020202020202020202020)
  [ 40- 59] 'PSN001              ' (HEX: 50534e30303120202020202020202020202020)
  [ 60- 79] 'PSN002              ' (HEX: 50534e30303220202020202020202020202020)
  [ 80- 99] 'PSN003              ' (HEX: 50534e30303320202020202020202020202020)
  [100-119] 'PSN004              ' (HEX: 50534e30303420202020202020202020202020)
  [120-139] 'PSN005              ' (HEX: 50534e30303520202020202020202020202020)
  [140-143] 'PASS' (HEX: 50415353)
======================================================================
```

### UI Log

```
======================================================================
✓ RECEIVED DATA FROM SFIS
  Length: 144 bytes
  Data: 2790004761          PANEL001            PSN001              PSN002              PSN003              PSN004              PSN005              PASS
======================================================================
DETAILED BREAKDOWN:
  [  0- 19] 2790004761          
  [ 20- 39] PANEL001            
  [ 40- 59] PSN001              
  [ 60- 79] PSN002              
  [ 80- 99] PSN003              
  [100-119] PSN004              
  [120-139] PSN005              
  [140-143] PASS
======================================================================
PARSED DATA:
  MO: 2790004761
  Panel: PANEL001
  PSN1: PSN001
  PSN2: PSN002
  PSN3: PSN003
  PSN4: PSN004
  PSN5: PSN005
```

## Cấu Hình

### Timeout

Mặc định: **10 giây**

Thay đổi trong `receiveResponsePsn()`:

```python
Q_ARG(int, 10000)  # 10 seconds = 10000ms
```

### Stop Condition

Dừng đọc khi không còn dữ liệu mới trong **100ms**

Thay đổi trong `read_data_all()`:

```python
max_no_data_count = 10  # 10 x 10ms = 100ms
```

## Ưu Điểm

### 1. Linh Hoạt
- Không cần biết trước format
- Không cần biết trước độ dài
- Tự động điều chỉnh theo dữ liệu thực tế

### 2. Debug Dễ Dàng
- Hiển thị đầy đủ dữ liệu nhận được
- Phân tích chi tiết từng phần
- Cả text và HEX format

### 3. Tự Động Parse
- Thử parse nếu có thể
- Không fail nếu parse không thành công
- Vẫn hiển thị raw data

## Use Cases

### Case 1: Dữ Liệu Đúng Format

```
Input: 144 bytes PSN response
Output: 
  - Raw data displayed
  - Parsed successfully
  - Show MO, Panel, PSN list
```

### Case 2: Dữ Liệu Sai Format

```
Input: Unknown format
Output:
  - Raw data displayed
  - Parse failed (warning)
  - Still show all data for analysis
```

### Case 3: Dữ Liệu Ngắn

```
Input: 50 bytes (less than expected)
Output:
  - Raw data displayed
  - Parse failed
  - Can see actual data received
```

### Case 4: Dữ Liệu Dài

```
Input: 300 bytes (more than expected)
Output:
  - All 300 bytes displayed
  - Parse may fail
  - Can analyze extra data
```

## Troubleshooting

### 1. Không nhận được dữ liệu

**Triệu chứng:**
```
Timeout: No data received
```

**Giải pháp:**
- Kiểm tra COM port có mở không
- Kiểm tra SFIS có gửi response không
- Tăng timeout nếu cần

### 2. Dữ liệu bị cắt

**Triệu chứng:**
```
Received 100 bytes, but expected more
```

**Giải pháp:**
- Tăng `max_no_data_count` (hiện tại: 10)
- Kiểm tra baudrate có đúng không
- Kiểm tra flow control

### 3. Parse failed

**Triệu chứng:**
```
(Could not parse as PSN format)
```

**Giải pháp:**
- Kiểm tra raw data trong log
- So sánh với format mong đợi
- Có thể format khác với dự kiến (OK, vẫn có raw data)

## Testing

### Test Manual

1. Kết nối SFIS
2. Click START
3. Kiểm tra log:
   - Có hiển thị "DATA RECEIVED FROM SFIS" không?
   - Length có đúng không?
   - Data có đầy đủ không?
   - Breakdown có chi tiết không?

### Test với Mock Data

```python
# Simulate data received
mock_data = "TEST" * 50  # 200 bytes

# Should display:
# - Length: 200 bytes
# - Data (text): TESTTESTTEST...
# - Data (HEX): 54455354...
# - Breakdown: [0-19], [20-39], ...
```

## Notes

- Dữ liệu luôn được decode với `errors='ignore'` để tránh crash
- HEX format giúp debug khi có ký tự đặc biệt
- Breakdown 20 bytes giúp dễ so sánh với format mong đợi
- Parse là optional, không ảnh hưởng đến việc hiển thị raw data

