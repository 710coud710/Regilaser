# Functions Reference

## 1. Event Handlers

### 1.1. Form Lifecycle Events

#### FormCreate (Line 141-166)
```cpp
void __fastcall TForm1::FormCreate(TObject *Sender)
```

**Mục đích**: Khởi tạo ban đầu khi form được tạo

**Workflow**:
1. Lấy đường dẫn thư mục chứa exe
2. Build đường dẫn file .tab
3. Kiểm tra file .tab tồn tại
4. Lấy hostname của PC
5. Hiển thị hostname lên StatusBar

**Dependencies**: 
- `ExtractFileDir()`
- `FileExists()`
- `WSAStartup()`, `gethostname()`, `gethostbyname()`

---

#### FormShow (Line 168-362)
```cpp
void __fastcall TForm1::FormShow(TObject *Sender)
```

**Mục đích**: Khởi tạo đầy đủ khi form được hiển thị

**Workflow**:
1. Hide các control không cần thiết
2. Load settings từ file .tab
3. Map network drive (nếu enable)
4. Tạo thư mục log
5. Load và khởi tạo HANS DLL
6. Kết nối các COM port
7. Setup UI display
8. Xác nhận MO Number với operator
9. Kiểm tra SMT type (E5/H7)
10. Click EMP button

**Called Functions**:
- `GetTabSettingAndShow()`
- `MapNetworkDrive()`
- `ForceDirectories()`
- `LoadLibrary()`
- `GetProcAddress()`
- `HS_InitialMachine()`
- `ComboBoxSFISCOMChange()`
- `ComboBoxCMDCOMChange()`
- `QuestionYesNO()`
- `InputBox()`
- `EMP_btn->Click()`

**Critical**: Nếu bất kỳ bước nào fail, application terminate

---

#### FormClose (Line 2884-2902)
```cpp
void __fastcall TForm1::FormClose(TObject *Sender, TCloseAction &Action)
```

**Mục đích**: Cleanup khi đóng form

**Workflow**:
1. Lưu AllPartSN vào .tab file
2. Close HANS machine
3. Free HANS DLL

**Code**:
```cpp
WriteIniValue("General", "AllPartSN", FormAllPart->Text.c_str(), chrTabPath);

if (hInstance != NULL) {
    pFunPro = GetProcAddress(hInstance, "HS_CloseMachine");
    HS_CloseMachine = (int(__stdcall *)())pFunPro;
    HS_CloseMachine();
    FreeLibrary(hInstance);
}
```

---

### 1.2. Button Click Events

#### FormStartBtnClick (Line 854-1334)
```cpp
void __fastcall TForm1::FormStartBtnClick(TObject *Sender)
```

**Mục đích**: Main laser marking process

**Parameters**: Triggered by SFIS after receiving PSN data

**Workflow**:
1. Check if test is running
2. **Phase 1**: Mark Script 1 (PSN 0-7)
   - Load marking file
   - Set text for 2D_0 to 2D_7
   - Set Panel Number
   - Start marking
   - Wait for completion
   - Close marking file
3. **Phase 2**: Send PRO1_DONE, wait START2
4. **Phase 3**: Mark Script 2 (PSN 8-11)
   - Load marking file 2
   - Set MO Number
   - Set text for 2D_8 to 2D_11
   - Start marking
   - Wait for completion
   - Close marking file
5. **Phase 4**: Send PRO2_DONE
6. **Phase 5**: Check SFIS response and show result

**Return**: 
- Success: `ShowStatus(1)` → PASS
- Failure: `ShowStatus(2)` → FAIL

**Error Handling**: Retry mechanisms cho PLC communication (3-4 lần)

---

#### EMP_btnClick (Line 2430-2446)
```cpp
void __fastcall TForm1::EMP_btnClick(TObject *Sender)
```

**Mục đích**: Send UNDO command và operator info to SFIS

**Workflow**:
```cpp
if (FormSFISStatus->Caption == "SFIS ON") {
    AnsiString tempopnumber;
    tempopnumber.sprintf("%-20sEND\r\n", OP_Number);
    
    SFIS_COM->WriteCommData("UNDO\r\n", strlen("UNDO\r\n"));
    Sleep(200);
    SFIS_COM->WriteCommData(tempopnumber.c_str(), strlen(tempopnumber.c_str()));
}
SFIS_memo->SetFocus();
```

**Usage**: Được gọi trong FormShow để khởi tạo SFIS session

---

#### pnl_StopClick (Line 2727-2737)
```cpp
void __fastcall TForm1::pnl_StopClick(TObject *Sender)
```

**Mục đích**: Emergency stop button

**Logic**:
```cpp
if (iSec > 9) {
    ShowMessage("目前测试阶段时间已超过10s，无法立即停止并退出");
} else {
    exit(0);  // Terminate immediately
}
```

**Safety**: Chỉ cho phép exit nếu test đang ở giai đoạn đầu (< 10s)

---

### 1.3. Communication Event Handlers

#### SFIS_COMReceiveData (Line 570-852)
```cpp
void __fastcall TForm1::SFIS_COMReceiveData(TObject *Sender, 
                                             Pointer Buffer, 
                                             WORD BufferLength)
```

**Mục đích**: Xử lý data nhận từ SFIS server

**Message Types**:

**Type 1**: PSN Data (284-286 bytes)
```
Format: MO(20) + Panel(20) + PSN[12]×20 + Status(4) + [CRLF]
```
- Parse 12 PSNs
- Validate format, front chars, sequence
- Append to log CSV
- Trigger marking: `FormStartBtnClick()`

**Type 2**: Pass/Fail Response (47-49 bytes)
```
Format: MO(20) + Panel(20) + "ENDPASS" or "ENDFAIL"
```
- Set `IsPassDCTResponse` flag

**Type 3**: Operator Info (23-27 bytes)
```
Format: Operator(20) + "END" + Status(4)
```
- Display operator and status

**Type 4**: NO MODEL Error
```
Message: Contains "NO MODEL"
```
- Send E-STOP to PLC
- Display error: SetMO

**Error Handling**: 
- Invalid length → Error message
- Invalid format → Stop test với error code

---

#### CMD_COMReceiveData (Line 2000-2030)
```cpp
void __fastcall TForm1::CMD_COMReceiveData(TObject *Sender, 
                                            Pointer Buffer,
                                            WORD BufferLength)
```

**Mục đích**: Xử lý response từ CCD

**Messages**:
- **CHE_OK**: Vision check OK → Forward to PLC
- **CHE_NG**: Vision check NG → Start thread send CHE_NG continuously

**Code Flow**:
```cpp
AnsiString ccdtemp = (char*)Buffer;
AnsiString toplc;

if (ccdtemp.Pos("CHE_OK")) {
    toplc = "CHE_OK";
} else if (ccdtemp.Pos("CHE_NG") && !IsCheck) {
    toplc = "CHE_NG";
}

if (toplc == "CHE_NG") {
    // Start thread to send repeatedly
    p_send_plc = new send_plc(true);
    p_send_plc->FreeOnTerminate = true;
    p_send_plc->Resume();
} else {
    FIXWriteCommDataWaitFor(toplc);
}
```

---

#### FIX_COMReceiveData (Line 2674-2723)
```cpp
void __fastcall TForm1::FIX_COMReceiveData(TObject *Sender, 
                                            Pointer Buffer,
                                            WORD BufferLength)
```

**Mục đích**: Xử lý data nhận từ PLC

**Messages**:

**START1**: Start test sequence
```cpp
if (!IsRunStatus && strReceive.Pos("START1")) {
    IsRunStatus = true;
    IsPassDCTResponse = false;
    DebugListBox->Clear();
    SFIS_memo->Clear();
    Auto_test();
}
```

**CHECK1**: CCD check request
```cpp
if (strReceive.Pos("CHECK1")) {
    Delay(500);
    CMD_COM->WriteCommData("CHECK1", strlen("CHECK1"));
}
```

**START2**: Ready for second marking
```cpp
if (strReceive.Pos("START2")) {
    GetStart2 = true;
}
```

**Buffer Management**:
```cpp
F_RecvBuffer += chrBuffer;  // Append to buffer for checking
```

---

### 1.4. Timer Events

#### CountTestTimerTimer (Line 1690-1709)
```cpp
void __fastcall TForm1::CountTestTimerTimer(TObject *Sender)
```

**Mục đích**: Cập nhật test time

**Update Frequency**: 1 second

**Logic**:
```cpp
iTempTime = clock() - iStartTime;
iHour = iTempTime / CLK_TCK / 3600;
iMin = (iTempTime - iHour*3600*CLK_TCK) / CLK_TCK / 60;
iSec = (iTempTime - iHour*3600*CLK_TCK - iMin*60*CLK_TCK) / CLK_TCK;

FormTestTime->Caption = AnsiString(iHour) + ":" + 
                        AnsiString(iMin) + ":" + 
                        AnsiString(iSec);

// Timeout check (7000 seconds)
if (iTempTime > 7000000) {
    DebugListBox->Lines->Add("Test Over Time");
    ShowStatus(1);  // Force pass
}
```

---

#### CountFreeTimerTimer (Line 1711-1723)
```cpp
void __fastcall TForm1::CountFreeTimerTimer(TObject *Sender)
```

**Mục đích**: Đếm interval time giữa các test

**Logic**:
```cpp
if (++iIntervalTimes > 5) {
    strTempBuffer.sprintf("Interval:%ds", (iIntervalTimes-5));
} else {
    strTempBuffer.sprintf("Interval:0s");
}
Label10->Caption = strTempBuffer;
```

**Note**: Bắt đầu đếm từ -5s (5s đệm)

---

### 1.5. Menu Item Events

#### PassToZero1Click (Line 1841-1848)
```cpp
void __fastcall TForm1::PassToZero1Click(TObject *Sender)
```

**Mục đích**: Reset Pass counter về 0

```cpp
Tab_Pass = 0;
WriteIniValue("PASS/FAIL", "Pass", "0", chrTabPath);
sprintf(temp, "Pass: %d", Tab_Pass);
StatusBar1->Panels->Items[2]->Text = temp;
```

---

#### FailToZero1Click (Line 1850-1857)
```cpp
void __fastcall TForm1::FailToZero1Click(TObject *Sender)
```

**Mục đích**: Reset Fail counter về 0

```cpp
Tab_Fail = 0;
WriteIniValue("PASS/FAIL", "Fail", "0", chrTabPath);
sprintf(temp, "Fail: %d", Tab_Fail);
StatusBar1->Panels->Items[3]->Text = temp;
```

---

#### mni_PSNClick (Line 2254-2279)
```cpp
void __fastcall TForm1::mni_PSNClick(TObject *Sender)
```

**Mục đích**: Calibration PSN trên Golden PCB

**Workflow**:
1. Confirm with operator (Yes/No dialog)
2. Call `Calibration()` - Set UI to calibration state
3. Call `Check_Tool()` - Launch MarkingBuilder2.exe
4. Wait 20 seconds for operator to calibrate
5. Confirm calibration result (Yes/No dialog)
6. If OK: Write calibration time to Registry
7. Show Pass/Fail status

**Registry Key**:
```
HKEY_LOCAL_MACHINE\Software\Sample Test\{ProductName}_{StationName}\Test Time
```

---

## 2. Core Functions

### 2.1. Configuration Functions

#### GetTabSettingAndShow (Line 364-455)
```cpp
void __fastcall TForm1::GetTabSettingAndShow()
```

**Mục đích**: Load tất cả settings từ file .tab

**Settings Loaded**:
```cpp
GetIniValue("General", "CMD_COM", CMD_COM_Text, chrTabPath);
GetIniValue("General", "FIX_COM", FIX_COM_Text, chrTabPath);
GetIniValue("General", "SFIS_Action", Tab_SFIS_Action, chrTabPath);
GetIniValue("General", "OP_Num", OP_Number, chrTabPath);
GetIniValue("General", "AllPartSN", Tab_AllPartSN, chrTabPath);
GetIniValue("General", "Title", Tab_ProgramTitle, chrTabPath);
GetIniValue("General", "ProductName", Tab_ProductName, chrTabPath);
GetIniValue("General", "StationName", Tab_StationName, chrTabPath);
GetIniValue("General", "FrontPSN_Num", Tab_FrontPSN_Num, chrTabPath);
GetIniValue("General", "HANS_LM_Script", Tab_HANS_LM_Script, chrTabPath);
GetIniValue("General", "HANS_LM_Script2", Tab_HANS_LM_Script2, chrTabPath);
GetIniValue("General", "LM_Config", Tab_LM_Config, chrTabPath);
GetIniValue("General", "MONum", Tab_MONum, chrTabPath);
GetIniValue("General", "PSNProgramNo", Tab_ProgramNo, chrTabPath);
GetIniValue("General", "PanelProgramNo", Tab_PanelProgramNo, chrTabPath);
GetIniValue("General", "PSN1_ProgramNo", Tab_PSN1_ProgramNo, chrTabPath);
GetIniValue("General", "PSN2_ProgramNo", Tab_PSN2_ProgramNo, chrTabPath);
GetIniValue("General", "PSN3_ProgramNo", Tab_PSN3_ProgramNo, chrTabPath);
GetIniValue("General", "PSN4_ProgramNo", Tab_PSN4_ProgramNo, chrTabPath);

GetIniValueInt("General", "IsDialogBeforeTest", Tab_IsDialogBeforeTest, chrTabPath);
GetIniValueInt("General", "LaserPanelLableEnable", Tab_LaserPanelLable, chrTabPath);
GetIniValueInt("General", "LM_Config_Enable", Tab_LM_Config_Enable, chrTabPath);

GetIniValueInt("PASS/FAIL", "Pass", Tab_Pass, chrTabPath);
GetIniValueInt("PASS/FAIL", "Fail", Tab_Fail, chrTabPath);

GetIniValueInt("SAVELOG", "IsLogOnLocal", Tab_IsLogOnLocal, chrTabPath);
GetIniValue("SAVELOG", "LocalLogPath", Tab_LocalLogPath, chrTabPath);
GetIniValueInt("SAVELOG", "IsLogOnServer", Tab_IsLogOnServer, chrTabPath);
GetIniValue("SAVELOG", "ServerDrive", Tab_ServerDrive, chrTabPath);
GetIniValue("SAVELOG", "ServerAddress", Tab_ServerAddress, chrTabPath);
GetIniValue("SAVELOG", "ServerLogpath", Tab_ServerLogPath, chrTabPath);
```

**Display**: Log tất cả settings vào DebugListBox

---

#### GetIniValue (Line 1982-1988)
```cpp
void __fastcall TForm1::GetIniValue(AnsiString Section, 
                                     AnsiString Key, 
                                     char* Value, 
                                     AnsiString Filepath)
```

**Mục đích**: Read string value từ INI file

**Implementation**:
```cpp
char returnStr[200] = {0};
int strlength = GetPrivateProfileString(Section.c_str(),
                                        Key.c_str(),
                                        NULL,
                                        returnStr,
                                        sizeof(returnStr),
                                        Filepath.c_str());
returnStr[strlength] = '\0';
strcpy(Value, returnStr);
```

---

#### GetIniValueInt (Line 1990-1993)
```cpp
void __fastcall TForm1::GetIniValueInt(AnsiString Section, 
                                        AnsiString Key, 
                                        int& Value, 
                                        AnsiString Filepath)
```

**Mục đích**: Read integer value từ INI file

**Implementation**:
```cpp
Value = GetPrivateProfileInt(Section.c_str(),
                              Key.c_str(),
                              -1,
                              Filepath.c_str());
```

**Default**: -1 nếu key không tồn tại

---

#### WriteIniValue (Line 1995-1998)
```cpp
void __fastcall TForm1::WriteIniValue(AnsiString Section, 
                                       AnsiString Key, 
                                       char* WriteString, 
                                       AnsiString Filepath)
```

**Mục đích**: Write value vào INI file

**Implementation**:
```cpp
WritePrivateProfileString(Section.c_str(),
                          Key.c_str(),
                          WriteString,
                          Filepath.c_str());
```

---

### 2.2. Communication Functions

#### CMDWriteCommDataWaitFor (Line 1337-1361)
```cpp
bool __fastcall TForm1::CMDWriteCommDataWaitFor(char *Cmd, 
                                                 AnsiString ExpStr, 
                                                 int iTimeout_ms = 200)
```

**Mục đích**: Send command to CCD và wait for expected response

**Parameters**:
- `Cmd`: Command to send
- `ExpStr`: Expected response string
- `iTimeout_ms`: Timeout in milliseconds (default 200ms)

**Return**: 
- `true`: Received expected response
- `false`: Timeout or wrong response

**Implementation**:
```cpp
m_RecvBuffer = "";
AnsiString tempcmd = AnsiString(Cmd) + "\r\n";
CMD_COM->WriteCommData(tempcmd.c_str(), strlen(tempcmd.c_str()));

if (iTimeout_ms == 0 || ExpStr == "") return true;

iTimeout_ms = iTimeout_ms / 100;
while (iTimeout_ms--) {
    if (m_RecvBuffer.Pos(ExpStr)) {
        return true;
    }
    Application->ProcessMessages();
    Delay(100);
}

strcpy(chrErrorCode, GRCR00);  // Can't get right COM response
return false;
```

**Usage Example**:
```cpp
if (!CMDWriteCommDataWaitFor("GA,001\r\n", "GA,0", 1000)) {
    ShowStatus(2);  // FAIL
    return;
}
```

---

#### FIXWriteCommDataWaitFor (Line 1364-1398)
```cpp
bool __fastcall TForm1::FIXWriteCommDataWaitFor(AnsiString Cmd, 
                                                 AnsiString ExpStr = "", 
                                                 int iTimeout_ms = 0)
```

**Mục đích**: Send command to PLC và wait for response

**Parameters**:
- `Cmd`: Command to send (will be padded to 12 bytes)
- `ExpStr`: Expected response (optional)
- `iTimeout_ms`: Timeout in milliseconds (default 0 = no wait)

**Return**:
- `true`: Success or received expected response
- `false`: Timeout or "not dut" response

**Special Handling**:
```cpp
// Pad command to 12 bytes
Cmd.sprintf("%-12s", Cmd);

// Check for "not dut" error
if (F_RecvBuffer.Pos("not dut")) {
    return false;
}
```

**Wait Logic**:
```cpp
int iTime = iTimeout_ms / 500;
while (iTime--) {
    if (F_RecvBuffer.Pos(ExpStr)) return true;
    if (F_RecvBuffer.Pos("not dut")) return false;
    Delay(500);
}
```

---

### 2.3. Test Flow Functions

#### Auto_test (Line 2032-2101)
```cpp
void _fastcall TForm1::Auto_test()
```

**Mục đích**: Bắt đầu test sequence, request PSN từ SFIS

**Workflow**:
1. Hide single panel controls
2. Initialize log system
3. Clear panel number
4. Set psn_i = 12 (request 12 PSNs)
5. Build SFIS request message
6. Send to SFIS

**Message Format**:
```cpp
if (CK_AllPartSN->Checked) {
    // With AllPartSN: MO(20) + AllPartSN(12) + Panel(20) + "NEEDPSN12\r\n"
    tempsfc.sprintf("%-20s%-12s%-20sNEEDPSN%d\r\n",
                    MO_Number, 
                    FormAllPart->Text.Trim(),
                    Panel_Number, 
                    psn_i);
} else {
    // Without AllPartSN: MO(20) + Panel(20) + "NEEDPSN12\r\n"
    tempsfc.sprintf("%-20s%-20sNEEDPSN%d\r\n",
                    MO_Number, 
                    Panel_Number, 
                    psn_i);
}
```

**Triggered By**: START1 signal từ PLC

---

#### OnPass (Line 1725-1755)
```cpp
void __fastcall TForm1::OnPass()
```

**Mục đích**: Internal pass handling

**Workflow**:
```cpp
DebugListBox->Lines->Add("-------->Test Pass");

if (IsSFISON) {
    OnSFISPass();  // Report to SFIS
}
```

---

#### OnSFISPass (Line 1757-1791)
```cpp
void __fastcall TForm1::OnSFISPass()
```

**Mục đích**: Report PASS result to SFIS

**Workflow**:
```cpp
IsRunStatus = false;

// Build message: MO(20) + Panel(20) + "END\r\n"
AnsiString tosfcdata;
tosfcdata.sprintf("%-20s%-20sEND\r\n", 
                  sfcdata.MO_Number, 
                  sfcdata.Panel_Number);

// Send with retry (3 times)
for (int i=1; i<4; i++) {
    SFIS_COM->WriteCommData(tosfcdata.c_str(), strlen(tosfcdata.c_str()));
    SFIS_memo->Lines->Add("TE To SFC[" + AnsiString(i) + "]:" + tosfcdata);
    delay_run(100);
    
    if (IsPassDCTResponse) return;  // Got ENDPASS response
}
```

**Expected Response**: "ENDPASS" from SFIS

---

#### OnFail (Line 1793-1821)
```cpp
void __fastcall TForm1::OnFail()
```

**Mục đích**: Handle fail case

**Workflow**:
```cpp
DebugListBox->Lines->Add("-------->Test Fail");

if (IsSFISON) {
    OnSFISFail();  // Report to SFIS
}

// Save fail logs
SaveAllLog("FAIL");
```

---

#### OnSFISFail (Line 1823-1839)
```cpp
void __fastcall TForm1::OnSFISFail()
```

**Mục đích**: Report FAIL result to SFIS

**Note**: Function body is commented out in current version

**Original Intent** (based on comments):
```cpp
// Build message: MO + Panel + PC Name + Error Code
sprintf(chrTempBuffer, "%-25s%-12s%-6s",
        strFormSN,
        strPCName.c_str(),
        chrSFISErrorCode);
SFIS_COM->WriteCommData(chrTempBuffer);
```

---

### 2.4. Status and Display Functions

#### ShowStatus (Line 1552-1688)
```cpp
void __fastcall TForm1::ShowStatus(int StatusMode)
```

**Mục đích**: Update UI status và xử lý kết quả test

**Parameters**:
- `StatusMode`: 
  - `0` = Marking (Yellow)
  - `1` = Pass (Green)
  - `2` = Fail (Red)
  - `3` = Stand By (Cyan)

**Case 0: Marking**
```cpp
iStartTime = clock();
memset(chrErrorCode, '\0', sizeof(chrErrorCode));
FormErrorCode->Caption = "";
CountFreeTimer->Enabled = false;
iIntervalTimes = 0;
CountTestTimer->Enabled = true;
P_F_Status->Color = clYellow;
P_F_Status->Caption = "Marking";
TestItem->Caption = "Start test";
```

**Case 1: Pass**
```cpp
CountTestTimer->Enabled = false;
CountFreeTimer->Enabled = true;

AppendLogcsv("Test_Times", FormTestTime->Caption.Trim());

if (IsSFISON) {
    FormSN->Enabled = true;
    FormStartBtn->Enabled = false;
}

Tab_Pass++;
WriteIniValue("PASS/FAIL", "Pass", chrTempBuffer, chrTabPath);
StatusBar1->Panels->Items[2]->Text = "Pass: " + Tab_Pass;

SaveAllLog("PASS");
AppendLogcsv("Test_Result", "PASS");
SaveResumeLog("PASS");

P_F_Status->Color = clLime;
P_F_Status->Caption = "Pass";
TestItem->Caption = "Test Pass";
```

**Case 2: Fail**
```cpp
FormErrorCode->Caption = chrErrorCode;
CountFreeTimer->Enabled = true;
CountTestTimer->Enabled = false;

AppendLogcsv("Test_Times", FormTestTime->Caption.Trim());

Tab_Fail++;
WriteIniValue("PASS/FAIL", "Fail", chrTempBuffer, chrTabPath);
StatusBar1->Panels->Items[3]->Text = "Fail: " + Tab_Fail;

IsRunStatus = false;
EMP_btn->Enabled = true;

SaveAllLog("FAIL");
AppendLogcsv("Test_Result", "FAIL");
SaveResumeLog("FAIL");

P_F_Status->Color = clRed;
P_F_Status->Caption = "Fail";
TestItem->Caption = "Test Fail";
```

**Case 3: Stand By**
```cpp
FormErrorCode->Caption = "";
CountFreeTimer->Enabled = true;
CountTestTimer->Enabled = false;
FormSN->Text = "";

P_F_Status->Color = clAqua;
P_F_Status->Caption = "StandBy";
TestItem->Caption = "Stand By";

IsRunStatus = false;
EMP_btn->Enabled = true;
iSec = 0;
```

---

### 2.5. Logging Functions

#### AppendLogcsv (Line 1439-1445)
```cpp
void __fastcall TForm1::AppendLogcsv(AnsiString title, AnsiString data)
```

**Mục đích**: Thêm một cặp key-value vào log buffer

**Implementation**:
```cpp
Logframe logtemp;
logtemp.Title = title;
logtemp.Data = data;
Logcsv.push_back(logtemp);
```

**Usage**:
```cpp
AppendLogcsv("Panel_Lable", sfcdata.Panel_Number);
AppendLogcsv("MO_Number", sfcdata.MO_Number);
AppendLogcsv("PSN_1", strSFISPSN[0]);
AppendLogcsv("Test_Times", "0:0:45");
AppendLogcsv("Test_Result", "PASS");
```

---

#### InitFailResumeLog (Line 1447-1498)
```cpp
void __fastcall TForm1::InitFailResumeLog()
```

**Mục đích**: Khởi tạo file Resume_Log.csv với header nếu chưa tồn tại

**Workflow**:
1. Build folder paths cho FAIL logs
2. Create directories
3. Build resume log file paths
4. Check if files exist
5. If not exist, create with header row

**Header Row**:
```
Panel_Lable,MO_Number,PSN_1,PSN_2,PSN_3,PSN_4,Test_Times,Test_Result
```

**Implementation**:
```cpp
AnsiString faillocalresumefile = Tab_LocalLogPath + "\\FAIL\\" + 
                                 FormatDateTime("YYYYMMDD", Now()) +
                                 "\\Resume_Local_Log.csv";

if (!FileExists(faillocalresumefile)) {
    AppendLogcsv("Panel_Lable", "");
    AppendLogcsv("MO_Number", "");
    AppendLogcsv("PSN_1", "");
    // ... more columns
    
    AnsiString strfailtitle;
    for (int i=0; i<Logcsv.size(); i++) {
        strfailtitle += Logcsv.at(i).Title + ",";
    }
    
    FILE *pfailfile = fopen(faillocalresumefile.c_str(), "a+");
    fprintf(pfailfile, "%s\n", strfailtitle.c_str());
    fclose(pfailfile);
    
    Logcsv.clear();
}
```

---

#### SaveAllLog (Line 1401-1437)
```cpp
void __fastcall TForm1::SaveAllLog(AnsiString Result)
```

**Mục đích**: Save full debug log to text file

**Parameters**:
- `Result`: "PASS" or "FAIL"

**File Path Structure**:
```
LocalPath\PASS\20250114\Result_PSN0001_120530.txt
ServerPath\FAIL\20250114\Result_PSN0010_130245.txt
```

**Implementation**:
```cpp
TDateTime dtTempData = Now();
AnsiString localresultfile = Tab_LocalLogPath + "\\" + Result;
AnsiString serverresultfile = Tab_ServerLogPath + "\\" + Result;

// Create directories
ForceDirectories(localresultfile);
ForceDirectories(serverresultfile);

// Save to local
if (Tab_IsLogOnLocal) {
    AnsiString path = localresultfile + "\\" + 
                      FormatDateTime("YYYYMMDD", dtTempData);
    ForceDirectories(path);
    
    AnsiString filename = path + "\\Result_" + 
                          strSFISPSN[0] + "_" +
                          FormatDateTime("HHNNSS", dtTempData) + ".txt";
    
    DebugListBox->Lines->SaveToFile(filename);
}

// Save to server (similar)
if (Tab_IsLogOnServer) {
    // ... similar logic
}
```

---

#### SaveResumeLog (Line 1500-1550)
```cpp
void __fastcall TForm1::SaveResumeLog(AnsiString resumeresult)
```

**Mục đích**: Save summary data to CSV file

**Parameters**:
- `resumeresult`: "PASS" or "FAIL"

**CSV Structure**:
```csv
Panel_Lable,MO_Number,PSN_1,...,PSN_12,Test_Times,Test_Result
PANEL001,MO12345678,PSN0001,...,PSN000C,0:0:45,PASS
```

**Implementation**:
```cpp
AnsiString strtitle, strdata;
for (int i=0; i<Logcsv.size(); i++) {
    strtitle += Logcsv.at(i).Title + ",";
    strdata += Logcsv.at(i).Data + ",";
}

AnsiString localresumefile = Tab_LocalLogPath + "\\" + 
                              resumeresult + "\\" +
                              FormatDateTime("YYYYMMDD", Now()) +
                              "\\Resume_Local_Log.csv";

FILE *pfile;
if (!FileExists(localresumefile)) {
    // Create file with header
    pfile = fopen(localresumefile.c_str(), "a+");
    fprintf(pfile, "%s\n", strtitle.c_str());
    fclose(pfile);
}

Sleep(200);

// Append data
pfile = fopen(localresumefile.c_str(), "a+");
fprintf(pfile, "%s\n", strdata.c_str());
fclose(pfile);

Logcsv.clear();
```

---

### 2.6. Utility Functions

#### Delay (Line 1955-1962)
```cpp
void __fastcall TForm1::Delay(unsigned int i_ms)
```

**Mục đích**: Delay with message processing

**Parameters**:
- `i_ms`: Milliseconds to delay

**Implementation**:
```cpp
unsigned int istart = ::GetTickCount();
while (::GetTickCount() - istart < i_ms) {
    Application->ProcessMessages();  // Keep UI responsive
}
```

**Advantage**: Không block UI thread

---

#### delay_run (Line 1965-1980)
```cpp
void __fastcall TForm1::delay_run(long int dt)
```

**Mục đích**: Delay using time structure (alternative method)

**Parameters**:
- `dt`: Delay time in hundredths of seconds

**Implementation**:
```cpp
struct time t;
long int last, now;

gettime(&t);
last = (t.ti_hour*60*60*100) + (t.ti_min*60*100) + 
       (t.ti_sec*100) + t.ti_hund;

do {
    gettime(&t);
    now = (t.ti_hour*60*60*100) + (t.ti_min*60*100) + 
          (t.ti_sec*100) + t.ti_hund;
    Application->ProcessMessages();
    
    if (now < last) {  // Handle midnight rollover
        now += (24*60*60*100);
    }
} while (now < (last+dt));
```

---

#### MapNetworkDrive (Line 1880-1932)
```cpp
bool __fastcall TForm1::MapNetworkDrive(char* pcLocalDrive, 
                                         char* pcRemote, 
                                         AnsiString& error, 
                                         const char* pcUser, 
                                         const char* pcPsw)
```

**Mục đích**: Map network drive

**Parameters**:
- `pcLocalDrive`: Local drive letter (e.g., "Z:")
- `pcRemote`: UNC path (e.g., "\\\\192.168.1.100\\share")
- `error`: Error message output
- `pcUser`: Username (default "oper")
- `pcPsw`: Password (default "wireless")

**Return**: 
- `true`: Success or already assigned
- `false`: Failed with error message

**Implementation**:
```cpp
TNetResource NetDrive;
NetDrive.dwScope = RESOURCE_GLOBALNET;
NetDrive.dwType = RESOURCETYPE_DISK;
NetDrive.dwUsage = RESOURCEUSAGE_CONNECTABLE;
NetDrive.lpLocalName = pcLocalDrive;
NetDrive.lpRemoteName = pcRemote;
NetDrive.lpProvider = "";

DWORD dwRet = WNetAddConnection2(&NetDrive, 
                                  pcPsw, 
                                  pcUser,
                                  CONNECT_UPDATE_PROFILE | CONNECT_INTERACTIVE);

if (dwRet == NO_ERROR || dwRet == ERROR_ALREADY_ASSIGNED) {
    return true;
} else {
    // Build detailed error message based on dwRet
    error.sprintf("Map server(%s) to local(%s) fail.", pcRemote, pcLocalDrive);
    
    switch (dwRet) {
        case ERROR_ACCESS_DENIED:
            error += "Error: access denied";
            break;
        case ERROR_BAD_DEV_TYPE:
            error += "Error: local drive can't match network resource";
            break;
        // ... more error cases
    }
    
    return false;
}
```

---

### 2.7. PSN Processing Functions

#### Convert32To10 (Line 2740-2779)
```cpp
int __fastcall TForm1::Convert32To10(AnsiString str)
```

**Mục đích**: Convert single base-32 character to decimal

**Mapping**:
```
'0'-'9' → 0-9
'A'-'H' → 10-17
'J'-'N' → 18-22
'P'-'X' → 23-31
```

**Return**: 
- `0-31`: Valid character
- `88`: Invalid character

**Implementation**:
```cpp
if (str=="0")   return 0;
if (str=="1")   return 1;
// ...
if (str=="A")   return 10;
if (str=="B")   return 11;
// ...
if (str=="X")   return 31;
return 88;  // Error
```

---

#### PSNSub4_32To10 (Line 2843-2881)
```cpp
unsigned long int __fastcall TForm1::PSNSub4_32To10(AnsiString PSN)
```

**Mục đích**: Convert last 4 characters of PSN from base-32 to decimal

**Algorithm**:
```
Result = d3×32³ + d2×32² + d1×32¹ + d0×32⁰
```

**Implementation**:
```cpp
unsigned long int result;
int iResult0, iResult1, iResult2, iResult3;

// Get last 4 characters (positions 13-16)
iResult3 = Convert32To10(PSN.SubString(13, 1));  // MSB
iResult2 = Convert32To10(PSN.SubString(14, 1));
iResult1 = Convert32To10(PSN.SubString(15, 1));
iResult0 = Convert32To10(PSN.SubString(16, 1));  // LSB

// Check for invalid characters
if (iResult0==88 || iResult1==88 || iResult2==88 || iResult3==88) {
    strcpy(chrErrorCode, SNRE00);  // SN Rule Error
    return 0;
}

// Calculate decimal value
result = iResult3 * 32 * 32 * 32 +
         iResult2 * 32 * 32 +
         iResult1 * 32 +
         iResult0;

return result;
```

**Example**:
```
PSN: "P0714M02ABCD000C"
Last 4: "000C"
  '0' → 0
  '0' → 0
  '0' → 0
  'C' → 12

Result = 0×32768 + 0×1024 + 0×32 + 12×1
       = 12
```

---

### 2.8. UI Helper Functions

#### QuestionYesNO (Line 2782-2805)
```cpp
bool __fastcall TForm1::QuestionYesNO(AnsiString strCaption,
                                       AnsiString strQuestion,
                                       bool bDefaultNo = true)
```

**Mục đích**: Show Yes/No dialog to user

**Parameters**:
- `strCaption`: Dialog caption/title
- `strQuestion`: Question text
- `bDefaultNo`: If true, NO button is default

**Return**:
- `true`: User clicked Yes
- `false`: User clicked No

**Implementation**:
```cpp
TQuestionDlg *pQuestionDlg = new TQuestionDlg(NULL);
pQuestionDlg->OKBtn->ModalResult = mrYes;
pQuestionDlg->NOBtn->ModalResult = mrNo;
pQuestionDlg->Caption->Caption = strCaption;
pQuestionDlg->Question->Text = strQuestion;
pQuestionDlg->NOBtn->Default = bDefaultNo;
pQuestionDlg->ShowModal();

bool result = (pQuestionDlg->ModalResult == mrYes);

if (WriteMO && result) {
    FormSN->Text = pQuestionDlg->Question->Text;
}

delete pQuestionDlg;
return result;
```

**Usage**:
```cpp
if (!QuestionYesNO("确认", "确认当前工单是否为：" + MO_Number, false)) {
    // User said NO, need to input new MO
    WriteMO = true;
}
```

---

## 3. Thread Class

### send_plc::Execute (Line 32-51)
```cpp
void __fastcall send_plc::Execute()
```

**Mục đích**: Send CHE_NG to PLC repeatedly for 30 seconds

**Usage**: Triggered when CCD returns CHE_NG (vision check fail)

**Logic**:
```cpp
for (int i=0; i<30; i++) {
    if (!IsRunStatus) {
        // Test stopped, send final CHE_NG and exit
        Form1->Delay(5000);
        Form1->FIXWriteCommDataWaitFor("CHE_NG");
        Form1->FormErrorCode->Caption = "视觉检测结果FAIL,请将当前的PCB取走";
        return;
    }
    
    Form1->Delay(1000);
    Form1->DebugListBox->Lines->Add("TE Send <CHE_NG> To PLC,Delay " + 
                                    AnsiString(i+1) + "s");
    
    if (i == 29) {
        // Last attempt
        Form1->FIXWriteCommDataWaitFor("CHE_NG");
    }
}
```

**Purpose**: Continuously notify PLC that vision check failed, giving operator time to remove bad PCB

---

## Summary

Document này cung cấp reference đầy đủ cho tất cả functions trong chương trình, bao gồm:
- **Event Handlers**: Form lifecycle, buttons, communications, timers, menus
- **Core Functions**: Configuration, communication, test flow, status display
- **Logging Functions**: CSV và text file logging
- **Utility Functions**: Delay, network mapping, PSN conversion
- **Thread**: Background PLC communication

Mỗi function được document với:
- Signature
- Mục đích
- Parameters và return values
- Implementation details
- Usage examples
- Related functions

