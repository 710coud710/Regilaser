
---s

# 📁 **Biểu đồ cấu trúc toàn hệ thống**

```
📦 Ứng dụng Regilazi
│
├── 🟦 1. Program Files (Cài bởi Inno Setup – READ ONLY)
│     📂 C:\Program Files\Regilazi\
│     │
│     ├── Regilazi.exe
│     ├── *.dll
│     ├── assets\
│     │     ├── icons\
│     │     ├── images\
│     │     └── static-data\
│     ├── config.default.yaml     (file cấu hình mẫu, không ghi đè)
│     └── runtime\                (nếu cần thư viện thêm)
│
├── 🟩 2. AppData/Roaming (Tự động tạo bởi code – ALLOW WRITE)
│     📂 C:\Users\<User>\AppData\Roaming\Regilazi\
│     │
│     ├── config.yaml             (cấu hình người dùng)
│     ├── logs\
│     │     ├── app.log
│     │     └── error.log
│     ├── cache\
│     │     └── temp.json
│     └── user-state.json         (trạng thái app, window size, port, last-used…)
│
└── 🟧 3. User Data (Người dùng chọn ở bước setup – READ/WRITE)
      📂 D:\RegilaziData\
      │
      ├── output\
      │     ├── laser_results_2025\
      │     └── exports\
      ├── images_scanned\
      └── backups\
```

---

# 🎯 **Giải thích trực quan theo biểu đồ**

## 🟦 **1. Program Files – “vùng hệ thống”**

* App và file tĩnh (exe, dll)
* Tài nguyên ảnh/logo
* Config mẫu (để copy sang AppData nếu thiếu)
* **Không bao giờ ghi vào đây trong runtime**

→ Vì Windows xem đây là **phần mềm**, không phải dữ liệu người dùng.

---

## 🟩 **2. AppData – “vùng cấu hình cá nhân”**

* Cấu hình người dùng
* Logs, cache
* File thay đổi liên tục
* Lưu theo từng người đăng nhập Windows

→ Đây là nơi ứng dụng có quyền **ghi thoải mái** mà không cần quyền admin.

---

## 🟧 **3. User Data – “vùng dữ liệu thực tế của công việc”**

* File kết quả laser
* File output
* Hình ảnh
* Export
* Backup

→ Tách biệt khỏi app để khi update app không ảnh hưởng.

---

# 📊 **Biểu đồ dòng chảy hoạt động (Flow Data)**

```
            ┌──────────────────────┐
            │ Program Files        │
            │ (App + Static Files) │
            └──────────┬───────────┘
                       │ READ ONLY
                       ▼
     ┌──────────────────────────────────────┐
     │ App khởi động                        │
     └──────────────────────────────────────┘
                       │
                       ▼
        Kiểm tra AppData/config.yaml
                       │
      ┌─────── yes ────┴────────── no ────────┐
      ▼                                        ▼
Dùng config.yaml                  Copy config.default.yaml
trong AppData                     từ Program Files → AppData
      ▼                                        ▼
  Đọc settings                           Lưu file config mới
                       ▼
               Hoạt động chính
                       │
                       ▼
    Ghi output → Folder User Data (ổ do user chọn)
```

---