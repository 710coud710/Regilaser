# Tổng Quan Chương Trình HANS Laser Marking

## 1. Giới Thiệu

**Tên chương trình**: BCM Common Use - HANS Laser Marking System  
**Version**: V1.1 (May 21, 2013)  
**Mục đích**: Hệ thống điều khiển máy laser marking tích hợp với SFIS (Shop Floor Information System)

## 2. Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────┐
│                     BCMBCB.exe                          │
│                   (Main Application)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼────────┐
│   MainForm     │   │  QuestionDlg    │
│  (Form chính)  │   │  (Dialog Yes/No)│
└───────┬────────┘   └─────────────────┘
        │
        ├─── send_plc (Thread gửi PLC)
        │
        ├─── SFIS_COM (Serial Communication)
        ├─── CMD_COM (CCD Communication)
        └─── FIX_COM (PLC Communication)
```

## 3. Các Thành Phần Chính

### 3.1. Module Chính

| Module | File | Chức năng |
|--------|------|-----------|
| Main Entry | BCMBCB.cpp | Entry point, khởi tạo ứng dụng, kiểm tra single instance |
| Main Form | MainForm.cpp/.h | Giao diện chính, xử lý logic laser marking |
| PLC Thread | send_plc.cpp/.h | Thread gửi lệnh CHE_NG đến PLC |
| Question Dialog | Unit_QuestionDlg.cpp/.h | Dialog xác nhận Yes/No |

### 3.2. Thư Viện DLL Được Sử Dụng

| DLL | Chức năng |
|-----|-----------|
| HansAdvInterface.dll | Điều khiển máy laser HANS |
| KeyboardHook.dll | Hook bàn phím để nhận dữ liệu |
| SPComm | Giao tiếp Serial Port |

### 3.3. Giao Tiếp Serial

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   SFIS_COM   │◄──────►│  SFIS Server │        │   CMD_COM    │
│ (SFIS Comm)  │        │   (9600bps)  │        │  (CCD Comm)  │
└──────────────┘        └──────────────┘        └──────┬───────┘
                                                        │
┌──────────────┐        ┌──────────────┐               │
│   FIX_COM    │◄──────►│     PLC      │◄──────────────┘
│  (PLC Comm)  │        │   (9600bps)  │
└──────────────┘        └──────────────┘
```

## 4. Cấu Trúc Dữ Liệu Chính

### 4.1. SFCData Structure
```cpp
struct SFCData {
    AnsiString MO_Number;      // Manufacturing Order Number (10 bytes)
    AnsiString Panel_Number;    // Panel Label (9 bytes)
}
```

### 4.2. Logframe Structure
```cpp
struct Logframe {
    AnsiString Title;  // Tiêu đề cột
    AnsiString Data;   // Dữ liệu
}
vector<Logframe> Logcsv;  // Lưu log CSV
```

### 4.3. Error Codes
Hệ thống định nghĩa các mã lỗi:
- **SRPE00-SRPE03**: SFIS Receive PSN Error
- **PSNC03, PSNC08, PSNC10**: PSN Compare Error
- **SRPEMO**: SFIS Receive MO/PO Error
- **LMPSN1-4**: Laser Marking PSN Fail
- **SBCE00-03**: Set Block Content Error
- **SNRE00-03**: SN Rule Error

## 5. File Cấu Hình

### 5.1. Sprite_LM.tab (INI Format)

```ini
[General]
CMD_COM=COM3
FIX_COM=COM4
SFIS_Action=Loading
OP_Num=OP12345
AllPartSN=PART123
Title=Program Title
ProductName=Product
StationName=LM Station
MONum=MO12345678
PSNProgramNo=001
FrontPSN_Num=P0714M02
HANS_LM_Script=script1.hs
HANS_LM_Script2=script2.hs
LM_Config_Enable=1
LM_Config=CONFIG

[PASS/FAIL]
Pass=0
Fail=0

[SAVELOG]
IsLogOnLocal=1
LocalLogPath=D:\Logs\Local
IsLogOnServer=1
ServerDrive=Z:
ServerAddress=\\192.168.1.100\share
ServerLogpath=Z:\Logs\Server
```

## 6. Workflow Tổng Quát

```
START
  │
  ├─► Khởi tạo ứng dụng (BCMBCB.cpp)
  │     │
  │     └─► Kiểm tra single instance (Mutex)
  │
  ├─► Load MainForm
  │     │
  │     ├─► FormCreate: Load settings từ .tab
  │     │
  │     └─► FormShow: Khởi tạo HANS Library
  │           │
  │           ├─► Connect Serial Ports (SFIS, CMD, FIX)
  │           ├─► Load HansAdvInterface.dll
  │           ├─► Initial HANS Machine
  │           └─► Ready State
  │
  ├─► Wait for START1 from PLC
  │     │
  │     └─► Trigger Auto_test()
  │           │
  │           └─► Send NEEDPSN to SFIS
  │
  ├─► Receive PSN from SFIS (12 PSNs)
  │     │
  │     ├─► Validate PSN format
  │     ├─► Compare PSN1 vs PSN12
  │     └─► FormStartBtnClick()
  │
  ├─► Laser Marking Process
  │     │
  │     ├─► Script 1: Mark PSN 0-7
  │     │     │
  │     │     ├─► Load marking file
  │     │     ├─► Set text (2D_0 ~ 2D_7)
  │     │     ├─► HS_Mark()
  │     │     ├─► Wait for completion
  │     │     └─► Close mark file
  │     │
  │     ├─► Send PRO1_DONE → Wait START2
  │     │
  │     └─► Script 2: Mark PSN 8-11
  │           │
  │           ├─► Load marking file
  │           ├─► Set text (2D_8 ~ 2D_11)
  │           ├─► HS_Mark()
  │           ├─► Wait for completion
  │           └─► Close mark file
  │
  ├─► Send PRO2_DONE to PLC
  │
  ├─► Send PASS/FAIL to SFIS
  │
  ├─► Save Logs
  │     │
  │     ├─► Save to local
  │     └─► Save to server
  │
  └─► Return to Ready State
```

## 7. Các Tính Năng Đặc Biệt

### 7.1. Single Instance Protection
- Sử dụng Windows Mutex để đảm bảo chỉ chạy 1 instance
- Tên Mutex: "BCMCommonUse"

### 7.2. Golden PCB Calibration
- Calibration PSN trên Golden PCB
- Lưu thời gian calibration vào Registry
- Kiểm tra interval time để nhắc calibration định kỳ

### 7.3. Network Drive Mapping
- Tự động map network drive để lưu log
- Username: "oper", Password: "wireless"

### 7.4. Multi-threading
- Thread `send_plc`: Gửi CHE_NG đến PLC liên tục trong 30s nếu CCD check fail

### 7.5. Base-32 Conversion
- Convert 4 ký tự cuối PSN từ base-32 sang decimal
- Dùng để so sánh PSN1 và PSN12

## 8. State Machine

```
┌─────────────┐
│  Stand By   │◄────────────────────────┐
└──────┬──────┘                         │
       │ START1                          │
       │                                 │
┌──────▼──────┐                         │
│   Marking   │                         │
└──────┬──────┘                         │
       │ Success                        │
       │                                 │
┌──────▼──────┐     ┌──────────┐       │
│    Pass     │     │   Fail   │───────┘
└──────┬──────┘     └──────────┘
       │
       └────────────────────────────────┘
```

## 9. Error Handling

### 9.1. Validation Layers
1. **PSN Format Check**: 16 ký tự
2. **PSN Front Check**: So sánh với Tab_FrontPSN_Num
3. **PSN Sequence Check**: PSN12 - PSN1 >= 11
4. **MO/PO Check**: Kiểm tra MO và Panel Number

### 9.2. Error Recovery
- Retry mechanism cho serial communication (3 lần)
- Timeout handling
- E-STOP signal để dừng PLC khi lỗi

## 10. Logging System

### 10.1. Log Levels
- **Debug Log**: DebugListBox (chi tiết từng bước)
- **SFIS Log**: SFIS_memo (communication với SFIS)
- **Result Log**: Lưu file .txt theo format Pass/Fail
- **Resume Log**: Lưu file .csv tổng hợp

### 10.2. Log File Structure
```
D:\Logs\
  ├─ PASS\
  │   └─ 20250114\
  │       ├─ Result_PSN123_120000.txt
  │       └─ Resume_Local_Log.csv
  └─ FAIL\
      └─ 20250114\
          ├─ Result_PSN456_120100.txt
          └─ Resume_Local_Log.csv
```

## 11. Kết Luận

Chương trình là một hệ thống tích hợp phức tạp với:
- **Multi-threading**: Xử lý song song nhiều tác vụ
- **Serial Communication**: 3 cổng COM đồng thời
- **DLL Integration**: Gọi thư viện bên ngoài
- **Error Handling**: Nhiều lớp validation
- **Logging**: Đầy đủ và chi tiết
- **Network Integration**: SFIS và network drive

Hệ thống được thiết kế để hoạt động trong môi trường sản xuất, với độ tin cậy cao và khả năng trace log đầy đủ.

