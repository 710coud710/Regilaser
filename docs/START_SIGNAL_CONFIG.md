# START Signal Configuration Guide

## Tổng Quan

START signal được gửi đến SFIS qua COM port với format động dựa trên cấu hình trong `config.yaml`.

## Format START Signal

```
MO(20 bytes) + Panel_Number(20 bytes) + NEEDPSNxx(9 bytes) = 49 bytes
```

### Các Thành Phần

1. **MO (Manufacturing Order)** - 20 bytes
   - Lấy từ `config.yaml` → field `MO`
   - Padding bằng spaces nếu < 20 ký tự
   - Cắt bớt nếu > 20 ký tự

2. **Panel Number** - 20 bytes
   - Luôn để trống (20 spaces)

3. **NEEDPSNxx** - 9 bytes
   - **Động** dựa trên `Panel_Num` trong `config.yaml`
   - Format: `NEEDPSN` + 2 chữ số cuối của `Panel_Num`
   - Ví dụ:
     - `Panel_Num: 5` → `NEEDPSN05`
     - `Panel_Num: 11` → `NEEDPSN11`
     - `Panel_Num: 99` → `NEEDPSN99`

## Config File (`config.yaml`)

```yaml
PANEL_NO: PANEL001
MO: 2790004761
SECURITY_CODE: 52-005353
Panel_Num: 5      # Panel Number để tạo NEEDPSNxx
FrontPSN_Num: P4N3SH
```

### Các Field Quan Trọng

| Field | Type | Mô Tả | Ví Dụ |
|-------|------|-------|-------|
| `MO` | int | Manufacturing Order | `2790004761` |
| `Panel_Num` | int | Panel Number (0-99) | `5` hoặc `11` |
| `SECURITY_CODE` | str | Security Code | `52-005353` |

## Config Manager (`config.py`)

### Đặc Điểm

- **Singleton Pattern**: Chỉ có 1 instance duy nhất
- **Thread-Safe**: Sử dụng `threading.Lock`
- **Hot Reload**: Tự động reload khi file thay đổi (mỗi 1 giây)
- **Validation**: Sử dụng Pydantic để validate dữ liệu

### Sử Dụng

```python
from config import ConfigManager

# Lấy config (singleton)
config_manager = ConfigManager()
config = config_manager.get()

# Truy cập giá trị
mo = config.MO
panel_num = config.Panel_Num
security_code = config.SECURITY_CODE

# Update config
config_manager.update('Panel_Num', 11)
```

## Flow Tạo START Signal

```
User Click START
    ↓
MainPresenter.onStartClicked()
    ↓
SFISPresenter.sendStartSignal()
    ↓
SFISModel.createStartSignal()
    ├─ Lấy MO từ ConfigManager
    ├─ Lấy Panel_Num từ ConfigManager
    ├─ Tạo NEEDPSNxx = f"NEEDPSN{Panel_Num:02d}"
    └─ Return: MO(20) + Panel(20) + NEEDPSNxx(9)
    ↓
SFISWorker.send_start_signal() (trong QThread)
    ↓
Gửi qua COM port (ASCII text)
```

## Ví Dụ

### Case 1: Panel_Num = 5

**Config:**
```yaml
MO: 2790004761
Panel_Num: 5
```

**START Signal:**
```
'2790004761                              NEEDPSN05'
 |--------20 bytes---------|----20 bytes----|--9--|
```

**HEX:**
```
323739303030343736312020202020202020202020202020202020202020202020202020202020204e45454450534e3035
```

### Case 2: Panel_Num = 11

**Config:**
```yaml
MO: 2790004761
Panel_Num: 11
```

**START Signal:**
```
'2790004761                              NEEDPSN11'
 |--------20 bytes---------|----20 bytes----|--9--|
```

**HEX:**
```
323739303030343736312020202020202020202020202020202020202020202020202020202020204e45454450534e3131
```

## Code Reference

### SFISModel.createStartSignal()

```python
def createStartSignal(self, mo=None, all_parts_no=None, panel_no=None):
    # Lấy config từ ConfigManager
    config = self.config_manager.get()
    
    # MO từ config
    if not mo:
        mo = str(config.MO)
    
    # Panel_Num từ config
    panel_num = config.Panel_Num
    
    # Tạo NEEDPSNxx động
    need_keyword = f"NEEDPSN{panel_num:02d}"
    
    # Format: MO(20) + Panel(20) + NEEDPSNxx(9)
    mo_padded = str(mo).ljust(20)[:20]
    panel_padded = "".ljust(20)
    start_signal = f"{mo_padded}{panel_padded}{need_keyword}"
    
    return start_signal  # 49 bytes
```

## Lưu Ý

1. **Panel_Num phải từ 0-99** (để format thành 2 chữ số)
2. **MO phải là số nguyên** (StrictInt trong Pydantic)
3. **Config tự động reload** khi file thay đổi (không cần restart app)
4. **Thread-safe** - có thể đọc config từ nhiều thread
5. **Validation tự động** - Pydantic sẽ báo lỗi nếu format sai

## Troubleshooting

### Lỗi: "Không thể đọc config"
- Kiểm tra file `config.yaml` có tồn tại không
- Kiểm tra format YAML có đúng không

### Lỗi: "NEEDPSN keyword không đúng độ dài"
- Kiểm tra `Panel_Num` có phải số từ 0-99 không
- Kiểm tra format `f"NEEDPSN{panel_num:02d}"` có tạo đúng 9 bytes không

### Lỗi: Validation error
- Kiểm tra `MO` phải là số nguyên (int)
- Kiểm tra `Panel_Num` phải là số nguyên (int)
- Kiểm tra `SECURITY_CODE` phải là string

## Testing

Chạy test để kiểm tra:

```python
from model.sfis_model import SFISModel
from config import ConfigManager

model = SFISModel()
config = ConfigManager().get()

print(f"Panel_Num: {config.Panel_Num}")

signal = model.createStartSignal()
print(f"START Signal: '{signal}'")
print(f"Length: {len(signal)} bytes")
print(f"NEEDPSN: '{signal[40:49]}'")
```

Expected output:
```
Panel_Num: 5
START Signal: '2790004761                              NEEDPSN05'
Length: 49 bytes
NEEDPSN: 'NEEDPSN05'
```

