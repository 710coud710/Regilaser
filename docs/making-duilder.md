Tôi sẽ tìm kiếm thông tin về kết nối với MarkingBuilder và các tín hiệu gửi đến chương trình đó.

[4 tools called]

Dựa trên phân tích code, tôi đã tìm thấy thông tin về kết nối với MarkingBuilder và các tín hiệu gửi đến chương trình đó:

## **Kết nối với MarkingBuilder2 và Tín hiệu gửi đi**

### **1. Hàm Check_Tool() - Khởi chạy MarkingBuilder2**

```cpp
void __fastcall TForm1::Check_Tool()
{
    AnsiString tempfile="C:\\Program Files\\Keyence\\MarkingBuilder2\\MarkingBuilder2.exe";
    if(FileExists(tempfile))
    {
        HWND hwnd=::FindWindow(NULL,"無題-MarkingBuilder2");
        HINSTANCE hInstance;
        if(hwnd==NULL)
        {
            // Khởi chạy MarkingBuilder2 nếu chưa chạy
            hInstance = ShellExecute(NULL,"open",tempfile.c_str(),NULL,NULL,SW_SHOWNORMAL);
            Sleep(1000);
            if((int)hInstance <= 32)
            {
                ShowMessage("MarkingBuilder2.exe is not Open");
                return;
            }
        }
        else
        {
            // Nếu đã chạy thì kill process
            system("taskkill /F /M MarkingBuilder2.exe");
        }
    }
    else
    {
        ShowMessage("MarkingBuilder2.exe is not Exists");
    }
}
```

### **2. Khi nào Check_Tool được gọi?**

**Điều kiện kích hoạt:** Khi người dùng click vào menu **PSN Calibration** (`mni_PSNClick`)

```cpp
void __fastcall TForm1::mni_PSNClick(TObject *Sender)
{
    // 1. Xác nhận với operator
    if(Application->MessageBoxA("請放Golden PCB進入治具內,進行PSN點雷射", "ASK", MB_YESNO) != ID_YES)
    {
        CalibrationFail();
        return;
    }
    
    Sleep(300);
    
    // 2. Bắt đầu calibration
    Calibration();
    
    // 3. Khởi chạy MarkingBuilder2
    Check_Tool();
    
    // 4. Chờ 20 giây để operator thực hiện calibration
    Sleep(20000);
    
    // 5. Xác nhận kết quả calibration
    if(Application->MessageBoxA("請確認PSN點雷射是否正確OK", "ASK", MB_YESNO) != ID_YES)
    {
        CalibrationFail();
        return;
    }
    
    // 6. Ghi thời gian calibration vào registry
    if(this->WriteCalibrationTimeToReg())
    {
        CalibrationPass();
    }
    else
    {
        CalibrationFail();
    }
}
```

### **3. Quy trình Calibration với MarkingBuilder2**

**Bước 1:** Operator click menu "PSN Calibration"
**Bước 2:** Hệ thống hiển thị dialog xác nhận đặt Golden PCB
**Bước 3:** Khởi chạy MarkingBuilder2.exe
**Bước 4:** Chờ 20 giây để operator thực hiện calibration thủ công
**Bước 5:** Xác nhận kết quả và ghi log

### **4. Đường dẫn MarkingBuilder2**

```cpp
AnsiString tempfile="C:\\Program Files\\Keyence\\MarkingBuilder2\\MarkingBuilder2.exe";
```

### **5. Tín hiệu và giao tiếp**

**Không có tín hiệu trực tiếp:** Chương trình không gửi tín hiệu trực tiếp đến MarkingBuilder2. Thay vào đó:

- **Khởi chạy:** Sử dụng `ShellExecute()` để mở MarkingBuilder2
- **Kiểm tra:** Sử dụng `FindWindow()` để tìm cửa sổ "無題-MarkingBuilder2"
- **Đóng:** Sử dụng `system("taskkill /F /M MarkingBuilder2.exe")` để kill process

### **6. Hàm Call_EXE_Tool() - Hàm tổng quát**

```cpp
bool __fastcall TForm1::Call_EXE_Tool(AnsiString exepath, AnsiString WindowTitle)
{
    if(FileExists(exepath))
    {
        HWND hwnd=::FindWindow(NULL,WindowTitle.c_str());
        HINSTANCE hInstance;
        if(hwnd==NULL)
        {
            // Khởi chạy ở chế độ minimize
            hInstance = ShellExecute(NULL,"open",exepath.c_str(),NULL,NULL,SW_MINIMIZE);
            Sleep(1000);
            if((int)hInstance <= 32)
            {
                return false;
            }
        }
        return true;
    }
    else
    {
        ShowMessage(exepath+" is not Exists");
        return false;
    }
}
```

### **7. Ghi thời gian Calibration vào Registry**

```cpp
bool __fastcall TForm1::WriteCalibrationTimeToReg()
{
    AnsiString Lasttempdata = FormatDateTime("YYYY_MM_DD HH:MM",Now());
    TRegistry *Reg=new TRegistry;
    Reg->RootKey=HKEY_LOCAL_MACHINE;
    AnsiString ProjectName=AnsiString(Tab_ProductName);
    AnsiString StationName=AnsiString(Tab_StationName);
    
    if(Reg->OpenKey("Software\\Sample Test\\"+ProjectName+"_"+StationName,true))
    {
        Reg->WriteString("Test Time",Lasttempdata);
        Reg->CloseKey();
        delete Reg;
        return true;
    }
    return false;
}
```

### **Tóm tắt:**

- **Mục đích:** Calibration PSN laser marking với Golden PCB
- **Kích hoạt:** Menu "PSN Calibration" 
- **Phương thức:** Khởi chạy MarkingBuilder2.exe bằng ShellExecute
- **Giao tiếp:** Không có tín hiệu trực tiếp, chỉ khởi chạy/đóng process
- **Thời gian:** Chờ 20 giây để operator thực hiện calibration thủ công
- **Lưu trữ:** Ghi thời gian calibration vào Windows Registry

Đây là một quy trình calibration thủ công, không phải tự động, yêu cầu operator tương tác trực tiếp với MarkingBuilder2 để thực hiện việc calibration laser marking.