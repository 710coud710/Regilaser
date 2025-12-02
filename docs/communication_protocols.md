# Hướng dẫn Giao tiếp và Kết nối Hệ thống

## Tổng quan

Chương trình này là một hệ thống Test Equipment (TE) dùng để điều khiển và giao tiếp với nhiều thiết bị khác nhau trong dây chuyền sản xuất, bao gồm:
- PLC (Programmable Logic Controller)
- SFIS (Shop Floor Information System) 
- Laser Marking System
- CCD Camera System
- Fixture Control System

## 1. Giao tiếp với PLC

### Phương thức kết nối
- **Giao thức**: Serial Communication (RS232/RS485)
- **Cổng COM**: COM3 (có thể cấu hình)
- **Tốc độ Baud**: 9600 bps
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None
- **Flow control**: XON/XOFF

### Cấu hình kết nối
```cpp
FIX_COM->CommName = "COM3";
FIX_COM->BaudRate = 9600;
FIX_COM->ByteSize = _8;
FIX_COM->StopBits = _1;
FIX_COM->Parity = None;
```

### Định dạng giao tiếp PLC

#### PLC → TE (Test Equipment)
| Lệnh | Mô tả | Ý nghĩa |
|------|-------|---------|
| `START1` | Bắt đầu laser marking | PCB đã sẵn sàng để bắt đầu laser marking |
| `CHE_READY` | Sẵn sàng kiểm tra | PCB đã sẵn sàng để bắt đầu quét mã |
| `Ready` hoặc `READY` | Trạng thái sẵn sàng | Hệ thống PLC sẵn sàng nhận lệnh |

#### TE → PLC
| Lệnh | Mô tả | Ý nghĩa |
|------|-------|---------|
| `L_OK` | Laser marking thành công | Quá trình laser marking hoàn thành OK |
| `L_NG` | Laser marking thất bại | Quá trình laser marking có lỗi |
| `CHE_OK` | Kiểm tra thành công | Quét mã thành công |
| `CHE_NG` | Kiểm tra thất bại | Quét mã thất bại |
| `NG\r\n` | Báo lỗi | Thông báo có lỗi xảy ra |

### Mã lỗi PLC
| Mã | Tên lỗi | Mô tả |
|----|---------|-------|
| M660 | ERR_01 | Lỗi trục Z |
| M661 | ERR_02 | Lỗi định vị |
| M662 | ERR_03 | Lỗi cảm biến |
| M663 | ERR_04 | Lỗi xoay |
| M665 | ERR_06 | Lỗi xoay và định vị |
| M666 | ERR_07 | Lỗi tốc độ xoay |
| M667 | ERR_08 | Lỗi laser |
| M668 | ERR_09 | Lỗi quét |
| M669 | ERR_10 | Lỗi xoay và định vị |
| M670 | ERR_11 | EMO & Door |
| M671 | ERR_12 | Lỗi cảm biến quét |
| M672 | ERR_13 | Lỗi sản phẩm |
| M673 | ERR_14 | Lỗi khởi tạo |

### Hàm giao tiếp PLC
```cpp
bool __fastcall TForm1::FIXWriteCommDataWaitFor(char *Cmd, AnsiString ExpStr, int iTimeout_ms)
{
    this->F_RecvBuffer = "";
    AnsiString tempcmd = AnsiString(Cmd);
    FIX_COM->WriteCommData(tempcmd.c_str(),strlen(tempcmd.c_str()));
    
    if(iTimeout_ms == 0 || ExpStr == "") {
        return true;
    }
    
    // Chờ phản hồi trong thời gian timeout
    iTimeout_ms = iTimeout_ms / 100;
    while(iTimeout_ms--) {
        if(this->F_RecvBuffer.Pos(ExpStr)) {
            return true;
        }
        Application->ProcessMessages();
        Delay(100);
    }
    return false;
}
```

## 2. Giao tiếp với SFIS (Shop Floor Information System)

### Phương thức kết nối
- **Giao thức**: Serial Communication (RS232)
- **Cổng COM**: Có thể cấu hình (thường là COM1 hoặc COM2)
- **Tốc độ Baud**: 9600 bps
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None

### Định dạng giao tiếp SFIS

#### 1. TE → SFC: Yêu cầu PSN
```
MO(20) + AllPar_NO(12) + PANEL_NO(20) + NEED(4) + PSN10(5)
Tổng độ dài: 61 bytes
```
**Ví dụ**: `001200035100-gsgadweewfgg          D19011701427PF3456789           NEEDPSN10`

#### 2. SFC → TE: Trả về thông tin PSN
```
MO(20) + PANEL_NO(20) + PSN1(20) + ... + PSN10(20) + PASS(4)
Tổng độ dài: 244 bytes
```

#### 3. TE → SFC: Báo hoàn thành test
```
MO(20) + PANEL_NO(20) + END(3)
Tổng độ dài: 43 bytes
```

#### 4. SFC → TE: Xác nhận hoàn thành
```
MO(20) + PANEL_NO(20) + END(3) + PASS(4)
Tổng độ dài: 47 bytes
```

#### 5. TE → SFC: Báo lỗi test
```
MO(20) + PANEL_NO(20) + END(3) + ErrorCode(6)
Tổng độ dài: 49 bytes
```

### Định dạng dữ liệu SFIS mới (cập nhật)
```
LaserSN(25) + SecurityCode(25) + Status(20) + PASS(4)
Tổng độ dài: 70 bytes
```

**Ví dụ**: `GR93J80034260001         52-005353                00S0PASS`

### Hàm xử lý SFIS
```cpp
void __fastcall TForm1::SFIS_COMReceiveData(TObject *Sender, Pointer Buffer, WORD BufferLength)
{
    AnsiString temp = (char*) Buffer;
    temp = temp.Trim();
    
    // Kiểm tra định dạng mới: LaserSN(25) + SecurityCode(25) + Status(20) + PASS
    if(!IsRunStatus && (temp.Length() == (25+25+20) && temp.Pos("PASS"))) {
        LaserSN = sfc_recvBuffer.SubString(1,25).Trim();
        // Bắt đầu quá trình laser marking
        Auto_test();
    }
}
```

## 3. Giao tiếp với Laser System

### Phương thức kết nối
- **Giao thức**: TCP/IP Socket
- **Địa chỉ IP**: 192.168.1.20
- **Port**: 50002
- **Loại kết nối**: Client Socket (Non-blocking)

### Cấu hình kết nối
```cpp
this->laser_Socket->Port = 50002;
this->laser_Socket->Address = "192.168.1.20";
this->laser_Socket->Active = true;
```

### Lệnh điều khiển Laser

#### 1. Lệnh GA (Get/Activate Program)
```
GA,<script_number>
```
**Ví dụ**: `GA,1` - Kích hoạt script số 1
**Phản hồi**: `GA,0` - Thành công

#### 2. Lệnh C2 (Set Content)
```
C2,<script>,<block>,<content>
```
**Ví dụ**: `C2,1,2,GR93J80034260001` - Đặt nội dung cho block 2 của script 1
**Phản hồi**: `C2,0` - Thành công

#### 3. Lệnh NT (Start Marking)
```
NT
```
**Phản hồi**: `NT,0` - Bắt đầu laser marking thành công

### Hàm giao tiếp Laser
```cpp
bool __fastcall TForm1::ClientSocketSendTextWaitFor(AnsiString Cmd, AnsiString ExpStr, int iTimeout_ms)
{
    this->RecvData = "";
    if(!ClientSocketSendText(Cmd)) {
        strcpy(chrErrorCode,"Connect Laser error");
        return false;
    }
    
    // Chờ phản hồi
    iTimeout_ms = iTimeout_ms / 100;
    while(iTimeout_ms--) {
        if(this->RecvData.Pos(ExpStr)) {
            return true;
        }
        Application->ProcessMessages();
        Delay(100);
    }
    return false;
}
```

### Quy trình Laser Marking
```cpp
void __fastcall TForm1::LaserPSN()
{
    // 1. Kích hoạt script
    AnsiString tempcmd;
    tempcmd.sprintf("GA,%s\r\n", laser_info.HMX_LM_Script);
    if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"GA,0",3000)) {
        ShowStatus(2);
        return;
    }
    
    // 2. Đặt nội dung security code
    tempcmd.sprintf("C2,%s,2,%s", laser_info.HMX_LM_Script, Securitycode);
    if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"C2,0",8000)) {
        ShowStatus(2);
        return;
    }
    
    // 3. Bắt đầu laser marking
    tempcmd = "NT\r\n";
    if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"NT,0",15000)) {
        ShowStatus(2);
        return;
    }
}
```

## 4. Giao tiếp với CCD Camera

### Phương thức kết nối
- **Giao thức**: Serial Communication
- **Cổng COM**: Có thể cấu hình

### Lệnh CCD
#### TE → CCD
| Lệnh | Mô tả |
|------|-------|
| `m_decode` | Yêu cầu giải mã |

#### CCD → TE
| Phản hồi | Mô tả |
|----------|-------|
| `decode_ok` | Giải mã thành công |
| `decode_ng` | Giải mã thất bại |

## 5. Keyboard Hook System

### Phương thức kết nối
- **Giao thức**: DLL (Dynamic Link Library)
- **File DLL**: KeyboardHook.dll

### Hàm điều khiển Hook
```cpp
bool __fastcall TForm1::SetHookDll(bool bStatus, AnsiString & error)
{
    if(hHookDll==NULL) {
        hHookDll=LoadLibrary("KeyboardHook.dll");
        if(hHookDll==NULL) {
            error="Load KeyboradHook.dll Error!";
            return false;
        }
    }
    
    if(bStatus) {
        // Bắt đầu hook
        starthook pStartHook=(starthook)GetProcAddress(hHookDll,"StartHook");
        pStartHook(this->Caption.c_str());
    } else {
        // Dừng hook
        stophook pStopHook=(stophook)GetProcAddress(hHookDll,"StopHook");
        pStopHook();
    }
    return true;
}
```

## 6. Quy trình hoạt động tổng thể

### Luồng công việc chính:
1. **Khởi tạo**: Kết nối tất cả các hệ thống (PLC, SFIS, Laser)
2. **Chờ tín hiệu**: PLC gửi `START1` hoặc `Ready`
3. **Nhận dữ liệu**: SFIS gửi thông tin PSN và Security Code
4. **Laser Marking**: Thực hiện laser marking với dữ liệu nhận được
5. **Báo kết quả**: Gửi kết quả về SFIS và PLC
6. **Lặp lại**: Quay lại bước 2

### Sơ đồ luồng:
```
PLC ----[START1]----> TE
                      |
                      v
TE ----[Request]----> SFIS
                      |
                      v
SFIS --[PSN Data]---> TE
                      |
                      v
TE ----[Commands]---> Laser
                      |
                      v
TE ----[Result]-----> SFIS & PLC
```

## 7. Xử lý lỗi và Timeout

### Timeout Settings:
- **PLC Communication**: 2000-8000ms
- **SFIS Communication**: 500-5000ms  
- **Laser Communication**: 3000-15000ms
- **Socket Connection**: 100ms intervals

### Error Codes:
- `GRCR00`: Can't get right COM response
- `GERROR`: Can't get right Socket response
- `SRPE00`: SFIS Receive PSN Error
- `LMPSN1-4`: Laser Marking PSN Fail

## 8. Cấu hình và Tùy chỉnh

### File cấu hình chính:
- `ALL_LM.tab`: Cấu hình chính của hệ thống
- `LM_INFO.csv`: Thông tin cấu hình laser cho từng sản phẩm

### Các tham số có thể cấu hình:
- COM Port cho từng thiết bị
- IP Address và Port cho Laser
- Timeout values
- Product-specific settings
- Logging paths

