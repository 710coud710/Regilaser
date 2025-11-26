# Luồng Xử Lý Dữ Liệu SFIS → Laser

## 1. TE gửi yêu cầu đến SFIS
- TE chuẩn bị chuỗi request theo định dạng cũ: `MO(20) + PANEL(20) + NEEDPSN + số lượng panel`
  - VD: `2795001670          PX5BF03TI           NEEDPSN5`
- Gửi qua cổng serial `SFIS_COM` thông qua `SFIS_COM->WriteCommData`.

## 2. SFIS trả dữ liệu PSN
- SFIS hồi đáp chuỗi `MO(20) + PANEL(20) + PSN1..PSNn (mỗi 20) + PASS(4)`
  - VD: `2795001670          PX5BF03TI           PT53QG0754670375 ... PASS`
- `SFIS_COMReceiveData` đọc buffer, lưu toàn bộ vào `sfc_recvBuffer` và hiển thị lên `SFIS_memo`.

## 3. Phân tách & kiểm tra chuỗi PSN
- `Auto_test()` (logic cũ) đọc từng trường cố định:
  - `MO_Number = SubString(1,20)`
  - `Panel_Number = SubString(21,20)`
  - `strSFISPSN[i] = SubString(41 + i*20, 20)`
- Kiểm tra tính hợp lệ:
  - `FrontPSN_Num` phải khớp prefix quy định.
  - Hiệu giữa PSN đầu/cuối ≥ số panel-1 (`PSNSub4_32To10`).

## 4. Ghi log và chuẩn bị security code
- Ghi MO/Panel/PSN vào CSV bằng `AppendLogcsv`.
- Lấy `Securitycode` từ `sfc_recvBuffer` (định dạng mới 25 ký tự sau LaserSN).
- Hiển thị trên UI và chuyển trạng thái `ShowStatus(0)` (Marking).

## 5. Giao tiếp với bộ điều khiển laser
- Socket TCP: `laser_Socket` kết nối tới `192.168.1.20:50002`.
- `LaserPSN()` gửi tuần tự các lệnh, dùng `ClientSocketSendTextWaitFor` chờ phản hồi:
  1. `GA,<script>\r\n` – chọn chương trình (ví dụ `GA,15`)
  2. `C2,<script>,2,<Securitycode>` – nạp chuỗi cần khắc
  3. `NT\r\n` – bắt đầu khắc

## 6. Nhận phản hồi từ laser
- `laser_SocketRead` gom chuỗi trả về (`GA,0`, `C2,0`, `NT,0`) và log vào `DebugListBox`.
- Nếu bất kỳ lệnh nào không nhận được phản hồi mong muốn trong timeout -> `ShowStatus(2)` (Fail).

## 7. Hoàn tất và báo về SFIS
- Khi khắc xong, `FormStartBtnClick` hoặc `OnSFISPass` gửi bản tin `MO(20)+Panel(20)+END`.
- SFIS trả `ENDPASS` và TE cập nhật log `Pass/Fail`, reset trạng thái UI.

## Tóm tắt phương thức
| Giai đoạn | Phương thức |
|-----------|-------------|
| TE ↔ SFIS | Serial COM (`SFIS_COM`) |
| SFIS parsing | SubString cố định 20 ký tự |
| TE ↔ Laser | TCP Socket (`laser_Socket`) với lệnh ASCII (`GA`, `C2`, `NT`) |
| Log/Status | `DebugListBox`, `SFIS_memo`, CSV, registry |
