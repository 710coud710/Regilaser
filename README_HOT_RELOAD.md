# 🔥 Hot Reload Development Guide

## Giới thiệu

Hot Reload cho phép bạn chỉnh sửa code và xem thay đổi ngay lập tức mà không cần khởi động lại ứng dụng thủ công.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

### Windows:
```bash
run_dev.bat
```

### Linux/Mac:
```bash
chmod +x run_dev.sh
./run_dev.sh
```

### Hoặc trực tiếp:
```bash
python main_dev.py
```

## Cách hoạt động

1. **Watchdog** theo dõi thay đổi trong các thư mục:
   - `gui/` - Tất cả file giao diện
   - `model/` - Logic và state management
   - `presenter/` - Business logic layer

2. Khi phát hiện thay đổi:
   - Chờ 500ms (debounce) để tránh reload nhiều lần
   - Lưu trạng thái window hiện tại (vị trí, kích thước)
   - Reload tất cả modules đã thay đổi
   - Tạo lại window với code mới
   - Khôi phục vị trí window cũ

3. **Console output** sẽ hiển thị:
   ```
   🔄 Phát hiện thay đổi: left_control_panel.py
   ♻️  Đang reload...
     ↻ Reloaded: gui.left_control_panel
     ↻ Reloaded: gui.main_window
   ✅ Reload thành công!
   ```

## Workflow phát triển

1. **Khởi động ứng dụng**:
   ```bash
   python main_dev.py
   ```

2. **Chỉnh sửa code** trong:
   - `gui/*.py` - Thay đổi giao diện
   - `model/*.py` - Thay đổi logic
   - `presenter/*.py` - Thay đổi điều phối

3. **Lưu file** (Ctrl+S):
   - Ứng dụng tự động reload
   - Thay đổi xuất hiện ngay lập tức

4. **Debug**:
   - Xem console để biết file nào được reload
   - Lỗi sẽ hiển thị trong console
   - Window cũ sẽ giữ nguyên nếu có lỗi

## Tips

### ✅ DO:
- Lưu file nhỏ, thường xuyên
- Chỉnh sửa một file tại một thời điểm
- Kiểm tra console để đảm bảo reload thành công

### ❌ DON'T:
- Thay đổi nhiều file cùng lúc (có thể gây xung đột)
- Chỉnh sửa khi đang reload (chờ thông báo "✅ Reload thành công!")
- Đóng console window (sẽ mất log)

## Production Mode

Khi deploy production, sử dụng file `main.py` thông thường:

```bash
python main.py
```

File `main.py` không có hot reload, chạy nhanh và ổn định hơn.

## Troubleshooting

### Hot reload không hoạt động?
- Kiểm tra watchdog đã được cài: `pip install watchdog`
- Xem console có lỗi gì không
- Đảm bảo đang sửa file trong `gui/`, `model/`, hoặc `presenter/`

### Lỗi khi reload?
- Xem traceback trong console
- Fix lỗi syntax trong code
- Window cũ vẫn hoạt động cho đến khi fix xong

### Reload chậm?
- Debounce time = 500ms (có thể điều chỉnh trong `hot_reload.py`)
- File lớn sẽ mất thời gian reload

## Architecture

```
main_dev.py
    ↓
hot_reload.py (HotReloader)
    ↓
watchdog (FileSystemEventHandler)
    ↓
Monitors: gui/, model/, presenter/
    ↓
On change → Reload modules → Recreate window
```

## Comparison

| Feature | main.py | main_dev.py |
|---------|---------|-------------|
| Hot Reload | ❌ | ✅ |
| Speed | Fast | Slower |
| Memory | Low | Higher |
| Use Case | Production | Development |
| Dependencies | PySide6 | PySide6 + watchdog |

---

Happy Coding! 🚀

