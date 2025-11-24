# START Signal Format

## 📋 Format Mới

### Cấu trúc:
```
MO(20 bytes) + Panel_Number(20 bytes) + NEEDPSN08(9 bytes) = 49 bytes total
```

### Chi tiết:
- **MO**: 20 bytes
  - Lấy từ `config.yaml`
  - Padding bằng space nếu ngắn hơn 20
  - Cắt nếu dài hơn 20

- **Panel_Number**: 20 bytes
  - Để trống (20 spaces)

- **NEEDPSN08**: 9 bytes
  - Keyword cố định
  - Yêu cầu SFIS trả về 8 PSN

## 📝 Ví dụ

### Config (config.yaml):
```yaml
PANEL_NO: PANEL001
MO: 2790004761
SECURITY_CODE: 52-005353
```

### Message được tạo:
```
MO: "2790004761          " (20 bytes - padded with 10 spaces)
Panel: "                    " (20 bytes - all spaces)
Keyword: "NEEDPSN08" (9 bytes)

Full message (49 bytes):
"2790004761                              NEEDPSN08"
 ^---------^                    ^--------^
 MO (20)                        Keyword (9)
            ^------------------^
            Panel (20 spaces)
```

### HEX representation:
```
32 37 39 30 30 30 34 37 36 31 20 20 20 20 20 20 20 20 20 20  // MO + padding
20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20  // Panel (all spaces)
4E 45 45 44 50 53 4E 30 38                                    // NEEDPSN08
```

## 🔧 Implementation

### Model (sfis_model.py):
```python
def createStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
    # Nếu không truyền MO, lấy từ config
    if not mo:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            mo = config.get('MO', '')
    
    # MO: 20 bytes
    mo_padded = str(mo).ljust(20)[:20]
    
    # Panel Number: 20 bytes (để trống)
    panel_padded = "".ljust(20)
    
    # NEEDPSN08: 9 bytes (cố định)
    need_keyword = "NEEDPSN08"
    
    # Tạo START signal: 20 + 20 + 9 = 49 bytes
    start_signal = f"{mo_padded}{panel_padded}{need_keyword}"
    
    return start_signal
```

### Usage:
```python
# Nhấn START button
# -> Tự động lấy MO từ config.yaml
# -> Tạo message 49 bytes
# -> Gửi qua COM port
# -> KHÔNG chờ response (fire and forget)
```

## 📊 Log Output

Khi nhấn START, log sẽ hiển thị:

```
[2025-11-21 16:30:00] [INFO] ======================================================================
[2025-11-21 16:30:00] [INFO] CHECK TÍN HIỆU TRƯỚC KHI GỬI:
[2025-11-21 16:30:00] [INFO]   Format: MO(20) + Panel(20) + NEEDPSN08(9) = 49 bytes
[2025-11-21 16:30:00] [INFO]   MO: '2790004761' (padded to 20)
[2025-11-21 16:30:00] [INFO]   Panel: '' (empty, 20 spaces)
[2025-11-21 16:30:00] [INFO]   Keyword: 'NEEDPSN08' (9 bytes)
[2025-11-21 16:30:00] [INFO]   Message Length: 49 bytes (expected: 49)
[2025-11-21 16:30:00] [INFO]   Message Content: '2790004761                              NEEDPSN08'
[2025-11-21 16:30:00] [INFO]   Message HEX: 32373930303034373631202020202020202020202020...
[2025-11-21 16:30:00] [INFO] ======================================================================
```

## 🔄 Flow

```
User Click START
    ↓
MainPresenter.onStartClicked()
    ↓
SFISPresenter.sendStartSignal()
    ↓
SFISModel.createStartSignal()
    ├─ Read MO from config.yaml
    ├─ Pad MO to 20 bytes
    ├─ Add 20 spaces for Panel
    └─ Add "NEEDPSN08"
    ↓
StartSignalWorker.send_start_signal()
    ├─ Log message details (ASCII + HEX)
    └─ Send via COM port
    ↓
Done (fire and forget - no response needed)
```

## ⚙️ Configuration

### config.yaml:
```yaml
PANEL_NO: PANEL001          # Không dùng trong START signal
MO: 2790004761              # ✓ Dùng cho START signal
SECURITY_CODE: 52-005353    # Không dùng trong START signal
```

### Thay đổi MO:
1. Edit `config.yaml`
2. Lưu file
3. Nhấn START → Tự động dùng MO mới

## 📌 Notes

- **KHÔNG validate**: Gửi luôn không kiểm tra
- **KHÔNG chờ response**: Fire and forget
- **MO tự động**: Lấy từ config.yaml
- **Panel trống**: Luôn là 20 spaces
- **NEEDPSN08 cố định**: Không thay đổi
- **Total: 49 bytes**: Đúng format yêu cầu

