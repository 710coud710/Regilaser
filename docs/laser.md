[7 tools called]

Luồng kết nối với phần mềm laser Keyence (MarkingBuilder/SamLight) diễn ra ngay sau khi TE nhận được bản tin `PASS` từ SFIS:

1. **Nhận dữ liệu SFIS và kích hoạt chuỗi laser**
   - Khi chuỗi `LaserSN(25) + SecurityCode(25) + Status(20) + PASS` đến, TE lưu lại SN/SecurityCode và gọi `Auto_test()`, từ đó kích hoạt `LaserPSN()` để giao tiếp với máy laser.

```1000:1034:MainForm.cpp
void __fastcall TForm1::SFIS_COMReceiveData(...){
    ...
    sfc_recvBuffer = temp;
    LaserSN = sfc_recvBuffer.SubString(1,25).Trim();
    Securitycode_sfis = sfc_recvBuffer.SubString(26,25).Trim();
    ...
    IsRunStatus=true;
    ...
    Auto_test();
    ...
}
```

```2220:2258:MainForm.cpp
InitFailResumeLog();
Logcsv.clear();
...
AnsiString str_temp = this->sfc_recvBuffer.SubString(26,25).Trim();
...
Securitycode = str_temp;
...
ShowStatus(0);
LaserPSN();
TObject *Sender;
FormStartBtnClick(Sender);
```

2. **Kết nối socket tới bộ điều khiển laser**
   - Khi form hiển thị, TE mở kết nối TCP tới `192.168.1.20:50002` và giữ socket ở chế độ non-blocking để gửi lệnh trực tiếp.

```489:505:MainForm.cpp
this->laser_Socket->Port = 50002;
this->laser_Socket->Address = "192.168.1.20";
this->laser_Socket->Active = true;
```

3. **Chuỗi lệnh gửi cho laser**
   - `LaserPSN()` gửi ba lệnh lần lượt và chờ phản hồi:
     1. `GA,<script>\r\n` – chọn chương trình laser tương ứng với sản phẩm (`laser_info.HMX_LM_Script`).
     2. `C2,<script>,2,<Securitycode>` – nạp chuỗi Security Code vào block 2 của chương trình.
     3. `NT\r\n` – phát lệnh bắt đầu khắc laser.

```2677:2796:MainForm.cpp
void __fastcall TForm1::LaserPSN(){
    AnsiString tempcmd;
    tempcmd.sprintf("GA,%s\r\n",laser_info.HMX_LM_Script);
    if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"GA,0",3000)){...}

    tempcmd = tempcmd.sprintf("C2,%s,2,%s",laser_info.HMX_LM_Script,Securitycode);
    if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"C2,0",8000)){...}
    ...
}
```

```3639:3645:MainForm.cpp
tempcmd="NT\r\n";
if(!this->ClientSocketSendTextWaitFor(tempcmd.c_str(),"NT,0",15000)){
    ShowStatus(2);
    return;
}
```

4. **Cơ chế gửi/đợi phản hồi**
   - Mỗi lệnh đi qua `ClientSocketSendTextWaitFor()`: gửi chuỗi, chờ phản hồi chứa `GA,0`, `C2,0`, `NT,0`. Dữ liệu trả về được gom vào `RecvData` nhờ `laser_SocketRead`.

```4173:4216:MainForm.cpp
bool __fastcall TForm1::ClientSocketSendTextWaitFor(...){
    this->RecvData = "";
    if(!ClientSocketSendText(Cmd)){ strcpy(chrErrorCode,"Connect Laser error"); return false; }
    ...
    while(iTimeout_ms--){
        if(this->RecvData.Pos(ExpStr)){ return true; }
        Application->ProcessMessages();
        Delay(100);
    }
    strcpy(chrErrorCode,GERROR);
    return false;
}
```

```4158:4164:MainForm.cpp
void __fastcall TForm1::laser_SocketRead(...){
    RecvData += Socket->ReceiveText().Trim();
    this->DebugListBox->Lines->Add("<<<<======== Laser Send TE:"+ RecvData);
}
```

**Tóm tắt format lệnh gửi đi:**
- `GA,<script>\r\n` → chờ `GA,0`
- `C2,<script>,2,<Securitycode>` → chờ `C2,0`
- `NT\r\n` → chờ `NT,0`

Nhờ cơ chế này, TE đảm bảo chỉ khi SFC cung cấp SN/SecurityCode hợp lệ thì lệnh laser mới được gửi và nhận xác nhận hoàn tất từ bộ điều khiển laser.