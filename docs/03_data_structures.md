# Cấu Trúc Dữ Liệu và Giao Thức

## 1. Data Structures

### 1.1. SFCData Structure

```cpp
struct SFCData {
    AnsiString MO_Number;      // Manufacturing Order Number
    AnsiString Panel_Number;   // Panel Label/Serial Number
} sfcdata;
```

**Mô tả**:
- `MO_Number`: Mã đơn hàng sản xuất (10 bytes, padded to 20)
- `Panel_Number`: Mã panel PCB (9 bytes, padded to 20)

**Sử dụng**:
```cpp
// Khởi tạo từ file .tab
sfcdata.MO_Number = AnsiString(Tab_MONum).Trim();

// Nhận từ SFIS
strncpy(chrSFISMO, chrReceBuffer, 10);
strncpy(chrPanelNO, chrReceBuffer+20, 9);
sfcdata.Panel_Number = AnsiString(chrPanelNO);
```

### 1.2. Logframe Structure

```cpp
struct Logframe {
    AnsiString Title;  // Tên cột trong CSV
    AnsiString Data;   // Giá trị dữ liệu
};

vector<Logframe> Logcsv;  // Global log buffer
```

**Mô tả**: Lưu trữ dữ liệu log theo cặp key-value để export ra CSV

**Sử dụng**:
```cpp
// Append data
void __fastcall TForm1::AppendLogcsv(AnsiString title, AnsiString data)
{
    Logframe logtemp;
    logtemp.Title = title;
    logtemp.Data = data;
    Logcsv.push_back(logtemp);
}

// Usage
AppendLogcsv("Panel_Lable", sfcdata.Panel_Number);
AppendLogcsv("MO_Number", sfcdata.MO_Number);
AppendLogcsv("PSN_1", strSFISPSN[0]);
AppendLogcsv("Test_Times", FormTestTime->Caption.Trim());
AppendLogcsv("Test_Result", "PASS");
```

**CSV Output Example**:
```
Panel_Lable,MO_Number,PSN_1,PSN_2,...,Test_Times,Test_Result
PANEL001,MO12345678,P0714M02ABCD0001,P0714M02ABCD0002,...,0:0:45,PASS
```

### 1.3. Global Variables

```cpp
// Status Flags
bool IsRunStatus = false;        // Test đang chạy
bool IsSFISON = false;           // SFIS COM connected
bool IsPassDCTResponse = false;  // Nhận được PASS response từ SFIS
bool IsCheck = false;            // CCD check status
bool GetStart2 = false;          // Đã nhận START2 từ PLC
bool WriteMO = false;            // Cần ghi MO mới

// Timing
long iStartTime;                 // Thời điểm bắt đầu test
int iIntervalTimes;              // Interval timer counter
int iSec;                        // Seconds counter
AnsiString iTestTime;            // Test time string

// PSN Data
AnsiString strSFISPSN[12];       // 12 PSN nhận từ SFIS
int psn_i;                       // Số lượng PSN cần request
AnsiString PSN_title;            // PSN prefix (P07, P11)

// Communication Buffers
AnsiString m_RecvBuffer;         // CMD_COM receive buffer
AnsiString F_RecvBuffer;         // FIX_COM receive buffer
AnsiString strCmdCommRec;        // CMD command receive buffer

// Error Tracking
char chrErrorCode[100];          // Current error code
char chrSFISErrorCode[10];       // SFIS error code

// Configuration (loaded from .tab file)
char Tab_SFIS_Action[30];        // SFIS action type
char Tab_ProgramTitle[100];      // Program title
char Tab_ProductName[20];        // Product name
char Tab_StationName[20];        // Station name
char Tab_MONum[100];             // MO Number
char Tab_FrontPSN_Num[8];        // PSN front characters
char Tab_HANS_LM_Script[20];     // Script 1 filename
char Tab_HANS_LM_Script2[20];    // Script 2 filename
char Tab_LM_Config[20];          // LM Config string
char Tab_AllPartSN[20];          // All part SN
char CMD_COM_Text[20];           // CMD COM port
char FIX_COM_Text[20];           // FIX COM port
char OP_Number[20];              // Operator number

// Program Numbers
char Tab_ProgramNo[100];         // PSN Program No
char Tab_PanelProgramNo[100];    // Panel Program No
char Tab_PSN1_ProgramNo[10];     // PSN1 specific program
char Tab_PSN2_ProgramNo[10];     // PSN2 specific program
char Tab_PSN3_ProgramNo[10];     // PSN3 specific program
char Tab_PSN4_ProgramNo[10];     // PSN4 specific program

// Counters
int Tab_Pass;                    // Pass counter
int Tab_Fail;                    // Fail counter

// Logging Configuration
int Tab_IsLogOnLocal;            // Enable local logging
char Tab_LocalLogPath[100];      // Local log path
int Tab_IsLogOnServer;           // Enable server logging
char Tab_ServerDrive[100];       // Server drive letter (Z:)
char Tab_ServerAddress[100];     // Server UNC path
char Tab_ServerLogPath[100];     // Server log path

// Paths
char chrTabPath[200];            // .tab file path
char chrCurrentPath[200];        // Current exe path
AnsiString strPCName;            // PC hostname (12 chars)

// HANS DLL
HINSTANCE hInstance;             // DLL handle
int i_function_Return;           // Function return value
FARPROC pFunPro;                 // Function pointer

// HANS Function Pointers
int (__stdcall *HS_InitialMachine)(char* pszPath);
int (__stdcall *HS_CloseMachine)();
int (__stdcall *HS_LoadMarkFile)(char* pszFileName);
int (__stdcall *HS_ChangeTextByName)(char* lpszTextName, char* lpszText);
int (__stdcall *HS_Mark)(int nType, bool bWaitTouch, bool bWaitEnd, 
                         int nOverTime, bool bMarkAll);
int (__stdcall *HS_IsMarkEnd)(int *pFlag);
int (__stdcall *HS_CloseMarkFile)(char* lpszFile, bool bSave);

// Thread
send_plc *p_send_plc;            // PLC sender thread
```

## 2. Communication Protocols

### 2.1. SFIS Protocol (SFIS_COM)

#### 2.1.1. TE → SFIS: Request PSN

**Format**: `MO(20) + [AllPartSN(12)] + Panel(20) + "NEEDPSN" + Count + "\r\n"`

**Với AllPartSN**:
```
Position: 0         20        32              52
Format:   [MO_Number][AllPartSN][Panel_Number][NEEDPSN12\r\n]
Length:      20         12           20            11
Example:  "MO12345678      PART123     PANEL001            NEEDPSN12\r\n"
```

**Không AllPartSN**:
```
Position: 0         20              40
Format:   [MO_Number][Panel_Number][NEEDPSN12\r\n]
Length:      20           20            11
Example:  "MO12345678      PANEL001            NEEDPSN12\r\n"
```

**Code**:
```cpp
if (CK_AllPartSN->Checked) {
    tempsfc.sprintf("%-20s%-12s%-20sNEEDPSN%d\r\n",
                    sfcdata.MO_Number, 
                    FormAllPart->Text.Trim(),
                    sfcdata.Panel_Number.c_str(), 
                    psn_i);
} else {
    tempsfc.sprintf("%-20s%-20sNEEDPSN%d\r\n",
                    sfcdata.MO_Number, 
                    sfcdata.Panel_Number.c_str(), 
                    psn_i);
}
SFIS_COM->WriteCommData(tempsfc.c_str(), strlen(tempsfc.c_str()));
```

#### 2.1.2. SFIS → TE: Send PSN Data

**Format**: `MO(20) + Panel(20) + PSN1(20) + ... + PSN12(20) + Status(4) + ["\r\n"]`

```
Position: 0    20   40   60   80   100  120  140  160  180  200  220  240  260  280  284
Field:    [MO ][PN ][P1 ][P2 ][P3 ][P4 ][P5 ][P6 ][P7 ][P8 ][P9 ][P10][P11][P12][ST][NL]
Length:    20   20   20   20   20   20   20   20   20   20   20   20   20   20   4   2
Total: 284 or 286 bytes
```

**PSN Format**: 16 characters actual data, padded to 20
```
Example PSN: "P0714M02ABCD0001    "
             |<- 16 chars ->|<-4->|
```

**Status**: 
- "PASS" (4 bytes)
- "FAIL" (4 bytes)

**Parsing Code**:
```cpp
// Parse MO (10 chars actual, in 20-byte field)
strncpy(chrSFISMO, chrReceBuffer, 10);
chrSFISMO[10] = '\0';

// Parse Panel NO (9 chars actual, in 20-byte field starting at offset 20)
strncpy(chrPanelNO, chrReceBuffer+20, 9);
chrPanelNO[9] = '\0';

// Parse 12 PSNs (16 chars each, in 20-byte fields)
for (int i=0; i<12; i++) {
    strncpy(chrSFISPSN[i], chrReceBuffer+40+(i*20), 16);
    chrSFISPSN[i][16] = '\0';
    strSFISPSN[i].sprintf("%s", chrSFISPSN[i]);
}

// Parse Status (4 bytes at offset 280)
strncpy(chrSFISStatus, chrReceBuffer+280, 4);
chrSFISStatus[4] = '\0';
```

#### 2.1.3. TE → SFIS: Report Result

**Format**: `MO(20) + Panel(20) + "END\r\n"`

```
Position: 0         20              40
Format:   [MO_Number][Panel_Number]["END\r\n"]
Length:      20           20           5
Total: 45 bytes

Example: "MO12345678      PANEL001            END\r\n"
```

**Code**:
```cpp
AnsiString tosfcdata;
tosfcdata.sprintf("%-20s%-20sEND\r\n", 
                  sfcdata.MO_Number, 
                  sfcdata.Panel_Number);

for (int i=1; i<4; i++) {
    SFIS_COM->WriteCommData(tosfcdata.c_str(), strlen(tosfcdata.c_str()));
    SFIS_memo->Lines->Add("TE To SFC[" + AnsiString(i) + "]:" + tosfcdata);
    delay_run(100);
    if (IsPassDCTResponse) return;
}
```

#### 2.1.4. SFIS → TE: Acknowledge Result

**Format**: `MO(20) + Panel(20) + "END" + Status + ["\r\n"]`

```
Format:   [MO_Number][Panel_Number]["ENDPASS\r\n"]
          or
          [MO_Number][Panel_Number]["ENDFAIL\r\n"]

Length:   20 + 20 + 7 + 2 = 49 bytes (ENDPASS)
          20 + 20 + 7 + 2 = 49 bytes (ENDFAIL)
```

**Parsing Code**:
```cpp
// In SFIS_COMReceiveData, case 2:
AnsiString passdata = AnsiString(chrReceBuffer);
if (passdata.Pos("ENDPASS") > 0) {
    IsPassDCTResponse = true;
} else {
    IsPassDCTResponse = false;
}
```

#### 2.1.5. TE → SFIS: Request Operator Info

**Format**: `OP_Number(20) + "END\r\n"`

```
Position: 0               20
Format:   [OP_Number     ]["END\r\n"]
Length:        20             5
Total: 25 bytes

Example: "OP12345             END\r\n"
```

**Code** (EMP_btnClick):
```cpp
AnsiString tempopnumber;
tempopnumber.sprintf("%-20sEND\r\n", OP_Number);

SFIS_COM->WriteCommData("UNDO\r\n", strlen("UNDO\r\n"));
Sleep(200);
SFIS_COM->WriteCommData(tempopnumber.c_str(), strlen(tempopnumber.c_str()));
```

#### 2.1.6. SFIS → TE: Operator Info Response

**Format**: `Operator(12) + "END" + Status(4) + ["\r\n"]`

```
Position: 0          12   15   19  21
Format:   [Operator   ]["END"]["PASS"]["\r\n"]
Length:       12         3     4      2
Total: 23 or 25 bytes

Example: "OP12345     ENDPASS\r\n"
```

**Parsing Code**:
```cpp
// In SFIS_COMReceiveData, case 3:
strncpy(chrSFISOper, chrReceBuffer, 12);
chrSFISOper[12] = '\0';

strncpy(chrSFISStatus, chrReceBuffer+23, 4);
chrSFISStatus[4] = '\0';

SFIS_memo->Lines->Add("Oper No:" + AnsiString(chrSFISOper));
SFIS_memo->Lines->Add("Status:" + AnsiString(chrSFISStatus));
```

### 2.2. PLC Protocol (FIX_COM)

#### 2.2.1. PLC → TE: START1 (Start Test)

**Format**: `"START1"` (variable length, no padding)

```
Message: "START1"
Length: 6 bytes
```

**Handling**:
```cpp
// In FIX_COMReceiveData
if (!IsRunStatus && strReceive.Pos("START1")) {
    IsRunStatus = true;
    IsPassDCTResponse = false;
    DebugListBox->Clear();
    SFIS_memo->Clear();
    Auto_test();  // Trigger test sequence
}
```

#### 2.2.2. TE → PLC: PRO1_DONE (Script 1 Complete)

**Format**: `"PRO1_DONE   "` (padded to 12 bytes)

```
Message: "PRO1_DONE   "
Length: 12 bytes (fixed)
```

**Code**:
```cpp
AnsiString Cmd01 = "PRO1_DONE";
for (int i=0; i<4; i++) {
    if (FIXWriteCommDataWaitFor("PRO1_DONE", "PRO1_DONE", 3000) || GetStart2) {
        GetStart2 = false;
        break;
    }
    if (i == 3) {
        ShowStatus(2);  // FAIL
        return;
    }
}
```

**FIXWriteCommDataWaitFor Implementation**:
```cpp
bool __fastcall TForm1::FIXWriteCommDataWaitFor(AnsiString Cmd, 
                                                 AnsiString ExpStr, 
                                                 int iTimeout_ms)
{
    F_RecvBuffer = "";
    Cmd.sprintf("%-12s", Cmd);  // Pad to 12 bytes
    FIX_COM->WriteCommData(Cmd.c_str(), strlen(Cmd.c_str()));
    
    if (iTimeout_ms == 0 || ExpStr == "") return true;
    
    int iTime = iTimeout_ms / 500;
    while (iTime--) {
        if (F_RecvBuffer.Pos(ExpStr)) return true;
        if (F_RecvBuffer.Pos("not dut")) return false;
        Delay(500);
    }
    return false;
}
```

#### 2.2.3. PLC → TE: START2 (Ready for Script 2)

**Format**: `"START2"` (variable length)

```
Message: "START2"
Length: 6 bytes
```

**Handling**:
```cpp
// In FIX_COMReceiveData
if (strReceive.Pos("START2")) {
    GetStart2 = true;
}

// In FormStartBtnClick - waiting for START2
for (int j=0; j<9; j++) {
    if (F_RecvBuffer.Trim().Pos("START2")) {
        break;
    }
    if (j == 8) {
        DebugListBox->Lines->Add("******Wait <START2> to TE Fail******");
        // Auto continue anyway
    }
    Delay(1000);
}
```

#### 2.2.4. TE → PLC: PRO2_DONE (Script 2 Complete)

**Format**: `"PRO2_DONE   "` (padded to 12 bytes)

```
Message: "PRO2_DONE   "
Length: 12 bytes (fixed)
```

**Code**:
```cpp
for (int i=0; i<3; i++) {
    if (FIXWriteCommDataWaitFor("PRO2_DONE", "PRO2_DONE", 3000)) {
        break;
    }
    if (i == 2) {
        ShowStatus(2);  // FAIL
        return;
    }
}
```

#### 2.2.5. PLC → TE: CHECK1 (Request CCD Check)

**Format**: `"CHECK1"` (variable length)

```
Message: "CHECK1"
Length: 6 bytes
```

**Handling**:
```cpp
// In FIX_COMReceiveData
if (strReceive.Pos("CHECK1")) {
    AnsiString temp = "CHECK1";
    Delay(500);
    CMD_COM->WriteCommData(temp.c_str(), strlen(temp.c_str()));
    SFIS_memo->Lines->Add("LM Send CCD:" + temp);
}
```

#### 2.2.6. TE → PLC: CHE_OK / CHE_NG (Check Result)

**Format**: `"CHE_OK      "` or `"CHE_NG      "` (padded to 12 bytes)

```
Message: "CHE_OK      " or "CHE_NG      "
Length: 12 bytes (fixed)
```

**Handling**:
```cpp
// In CMD_COMReceiveData (receive from CCD)
AnsiString ccdtemp = (char*)Buffer;
AnsiString toplc;

if (ccdtemp.Pos("CHE_OK")) {
    toplc = "CHE_OK";
} else if (ccdtemp.Pos("CHE_NG") && !IsCheck) {
    toplc = "CHE_NG";
}

if (toplc == "CHE_NG") {
    // Start thread to send CHE_NG repeatedly
    p_send_plc = new send_plc(true);
    p_send_plc->FreeOnTerminate = true;
    p_send_plc->Resume();
} else {
    FIXWriteCommDataWaitFor(toplc);
}
```

**send_plc Thread** (Line 32-51):
```cpp
void __fastcall send_plc::Execute()
{
    for (int i=0; i<30; i++) {
        if (!IsRunStatus) {
            Form1->Delay(5000);
            Form1->FIXWriteCommDataWaitFor("CHE_NG");
            Form1->FormErrorCode->Caption = "视觉检测结果FAIL,请将当前的PCB取走";
            return;
        }
        Form1->Delay(1000);
        Form1->DebugListBox->Lines->Add("TE Send <CHE_NG> To PLC,Delay " + 
                                        AnsiString(i+1) + "s");
        if (i == 29) {
            Form1->FIXWriteCommDataWaitFor("CHE_NG");
        }
    }
}
```

#### 2.2.7. TE → PLC: E-STOP (Emergency Stop)

**Format**: `"E-STOP      "` (padded to 12 bytes)

```
Message: "E-STOP      "
Length: 12 bytes (fixed)
```

**Usage**:
```cpp
// When error occurs
FIXWriteCommDataWaitFor("E-STOP");
```

### 2.3. CCD Protocol (CMD_COM)

CCD communication is forwarded from PLC CHECK1 signal.

#### 2.3.1. TE → CCD: CHECK1

```
Message: "CHECK1\r\n"
Length: 8 bytes
```

#### 2.3.2. CCD → TE: CHE_OK / CHE_NG

```
Message: "CHE_OK" or "CHE_NG"
Length: Variable
```

### 2.4. HANS DLL Protocol

#### 2.4.1. HS_InitialMachine

```cpp
int HS_InitialMachine(char* pszPath);

// Usage
pFunPro = GetProcAddress(hInstance, "HS_InitialMachine");
HS_InitialMachine = (int(__stdcall *)(char*))pFunPro;
i_function_Return = HS_InitialMachine(NULL);

// Return: 0 = Success, Other = Error
```

#### 2.4.2. HS_LoadMarkFile

```cpp
int HS_LoadMarkFile(char* pszFileName);

// Usage
AnsiString HANS_Script_str = currentPath + "\\" + Tab_HANS_LM_Script;
pFunPro = GetProcAddress(hInstance, "HS_LoadMarkFile");
HS_LoadMarkFile = (int(__stdcall *)(char*))pFunPro;
i_function_Return = HS_LoadMarkFile(HANS_Script_str.c_str());

// Return: 0 = Success, Other = Error
```

#### 2.4.3. HS_ChangeTextByName

```cpp
int HS_ChangeTextByName(char* lpszTextName, char* lpszText);

// Usage - Set PSN text
TextName = "2D_0";
Text = "P0714M02ABCD0001";
HS_ChangeTextByName(TextName.c_str(), Text.c_str());

// Usage - Set Config text
ConfigTextName = "2D_0_title";
ConfigText = "CONFIG";
HS_ChangeTextByName(ConfigTextName.c_str(), ConfigText.c_str());

// Return: 0 = Success, Other = Error
```

#### 2.4.4. HS_Mark

```cpp
int HS_Mark(int nType, bool bWaitTouch, bool bWaitEnd, 
            int nOverTime, bool bMarkAll);

// Usage
HS_Mark(0, false, false, 500, true);

// Parameters:
//   nType: 0 = Normal marking
//   bWaitTouch: false = Don't wait for touch sensor
//   bWaitEnd: false = Don't wait for completion (use HS_IsMarkEnd instead)
//   nOverTime: 500 ms timeout
//   bMarkAll: true = Mark all objects in file

// Return: 0 = Success, Other = Error
```

#### 2.4.5. HS_IsMarkEnd

```cpp
int HS_IsMarkEnd(int *pFlag);

// Usage
int flag = -999;
for (int i=0; i<60; i++) {
    Sleep(500);
    HS_IsMarkEnd(&flag);
    if (flag == 1) {
        // Marking complete
        break;
    } else if (flag == 0) {
        // Still marking...
        continue;
    } else if (flag == 2) {
        // Exception stop
        ERROR;
    }
}

// Flag values:
//   0 = Marking in progress
//   1 = Marking complete
//   2 = Exception stop
//   Other = Machine exception

// Return: 0 = Success, Other = Error
```

#### 2.4.6. HS_CloseMarkFile

```cpp
int HS_CloseMarkFile(char* lpszFile, bool bSave);

// Usage
HS_CloseMarkFile(Tab_HANS_LM_Script, false);

// Parameters:
//   lpszFile: Filename to close
//   bSave: false = Don't save changes

// Return: 0 = Success, Other = Error
```

#### 2.4.7. HS_CloseMachine

```cpp
int HS_CloseMachine();

// Usage (in FormClose)
pFunPro = GetProcAddress(hInstance, "HS_CloseMachine");
HS_CloseMachine = (int(__stdcall *)())pFunPro;
HS_CloseMachine();

// Return: 0 = Success, Other = Error
```

## 3. PSN Format and Validation

### 3.1. PSN Structure

```
Position: 1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
Format:   [P] [0] [7] [1] [4] [M] [0] [2] [A] [B] [C] [D] [0] [0] [0] [1]
          |<------- Front 8 ------>| |<---- Serial 8 ---->|
          |<------ Fixed 10 ------>|     |<-- Base32(4) ->|

Example: "P0714M02ABCD0001"
         P07: Product code (3 chars)
         14M02: Fixed identifier (5 chars)
         ABCD: Lot/Batch code (4 chars)
         0001: Serial number in Base-32 (4 chars)
```

### 3.2. Base-32 Encoding

**Character Set**: `0123456789ABCDEFGHJKLMNPQRSTUVWX` (32 chars, no I, O)

**Mapping**:
```
0→0   1→1   2→2   3→3   4→4   5→5   6→6   7→7   8→8   9→9
A→10  B→11  C→12  D→13  E→14  F→15  G→16  H→17
J→18  K→19  L→20  M→21  N→22
P→23  Q→24  R→25  S→26  T→27  U→28  V→29  W→30  X→31
```

**Conversion Code**:
```cpp
int __fastcall TForm1::Convert32To10(AnsiString str)
{
    if (str=="0")   return 0;
    if (str=="1")   return 1;
    // ... 
    if (str=="A")   return 10;
    if (str=="B")   return 11;
    // ...
    if (str=="X")   return 31;
    return 88;  // Invalid
}

unsigned long int __fastcall TForm1::PSNSub4_32To10(AnsiString PSN)
{
    unsigned long int result;
    int iResult0, iResult1, iResult2, iResult3;
    
    // Get last 4 characters (positions 13-16)
    iResult3 = Convert32To10(PSN.SubString(13, 1));  // Most significant
    iResult2 = Convert32To10(PSN.SubString(14, 1));
    iResult1 = Convert32To10(PSN.SubString(15, 1));
    iResult0 = Convert32To10(PSN.SubString(16, 1));  // Least significant
    
    if (iResult0==88 || iResult1==88 || iResult2==88 || iResult3==88) {
        // Invalid character
        return 0;
    }
    
    // Calculate: result = d3*32³ + d2*32² + d1*32¹ + d0*32⁰
    result = iResult3 * 32 * 32 * 32 +
             iResult2 * 32 * 32 +
             iResult1 * 32 +
             iResult0;
    
    return result;
}
```

**Example**:
```
PSN: "P0714M02ABCD0001"
Last 4: "0001"
  Position 13: '0' → 0
  Position 14: '0' → 0
  Position 15: '0' → 0
  Position 16: '1' → 1

Decimal = 0×32³ + 0×32² + 0×32¹ + 1×32⁰
        = 0 + 0 + 0 + 1
        = 1

PSN: "P0714M02ABCD000C"
Last 4: "000C"
  '0' → 0, '0' → 0, '0' → 0, 'C' → 12

Decimal = 0×32³ + 0×32² + 0×32¹ + 12×32⁰
        = 0 + 0 + 0 + 12
        = 12
```

### 3.3. PSN Validation Rules

#### Rule 1: Length Check
```cpp
if (!(strSFISPSN[0].Trim().Length() == 16
   && strSFISPSN[1].Trim().Length() == 16
   // ... all 12 PSNs
   && strSFISPSN[11].Trim().Length() == 16))
{
    ERROR: SRPE00 (SFIS Receive PSN Error)
}
```

#### Rule 2: Front Characters Check (PSNC03)
```cpp
// Check if PSN contains PSN_title (should NOT contain)
for (int i=0; i<12; i++) {
    if (strSFISPSN[i].Pos(PSN_title)) {
        ERROR: PSNC03 (PSN Front Error)
    }
}
```

#### Rule 3: First 8 Chars Match (PSNC08)
```cpp
AnsiString str_FrontPSN_Num = AnsiString(Tab_FrontPSN_Num).SubString(1,8);
if (strSFISPSN[0].SubString(1,8) != str_FrontPSN_Num 
    && strSFISPSN[11].SubString(1,8) != str_FrontPSN_Num)
{
    ERROR: PSNC08 (PSN Front Error)
}
```

#### Rule 4: PSN1 vs PSN12 First 10 Match (PSNC10)
```cpp
if (strSFISPSN[0].SubString(3,10) != strSFISPSN[11].SubString(3,10)) {
    ERROR: PSNC10 (PSN1 Compare PSN12 is 10byte Error)
}
```

#### Rule 5: Sequence Check (ComPSN)
```cpp
unsigned long int_PSN0 = PSNSub4_32To10(strSFISPSN[0]);
unsigned long int_PSN11 = PSNSub4_32To10(strSFISPSN[11]);

if ((int_PSN11 - int_PSN0) < 11) {
    ERROR: ComPSN (PSN1 Compare PSN12 is 8 Error)
}
```

**Explanation**: 
- Panel có 12 PSN
- PSN1 đến PSN12 phải liên tiếp (difference >= 11)
- Ví dụ: PSN1=0001, PSN12 phải >= 000C (12)

## 4. Error Codes Reference

### 4.1. SFIS Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| SRPE00 | SFIS Receive PSN Error | PSN length không đúng 16 ký tự |
| SRPE01 | SFIS Receive PSN1 Error | PSN1 format error |
| SRPE02 | SFIS Receive PSN2 Error | PSN2 format error |
| SRPE03 | SFIS Receive PSN3 Error | PSN3 format error |
| SRP063 | SFIS Receive PSN(063) Error | PSN không bắt đầu với 063 |
| SRPEMO | SFIS Receive MO or PO Error | MO hoặc Panel Number không khớp |
| SRSE00 | SFIS Receive Status Error | SFIS không trả về PASS |

### 4.2. PSN Compare Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| PSNC03 | PSN Front Error | PSN chứa PSN_title (invalid) |
| PSNC08 | PSN Front Error | 8 ký tự đầu không khớp Tab_FrontPSN_Num |
| PSNC10 | PSN1 Compare PSN8 is 10byte Error | 10 ký tự đầu PSN1 và PSN12 không khớp |
| ComPSN | PSN1 Compare PSN8 is 8 Error | Difference PSN12-PSN1 < 11 |

### 4.3. Laser Marking Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| LMPSN1 | Laser Marking PSN1 Fail | Laser marking PSN1 failed |
| LMPSN2 | Laser Marking PSN2 Fail | Laser marking PSN2 failed |
| LMPSN3 | Laser Marking PSN3 Fail | Laser marking PSN3 failed |
| LMPSN4 | Laser Marking PSN4 Fail | Laser marking PSN4 failed |

### 4.4. Program Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| SPNE00 | Select Program NO. Error | Chọn program number lỗi |
| SBCE00 | Set Block 0 Content Error | Set block 0 content fail |
| SBCE01 | Set Block 1 Content Error | Set block 1 content fail |
| SBCE02 | Set Block 2 Content Error | Set block 2 content fail |
| SBCE03 | Set Block 3 Content Error | Set block 3 content fail |
| MCRE00 | Mask Complete Response Error | Mask complete response error |

### 4.5. Communication Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| GRCR00 | Can't get right COM response | Không nhận được response đúng từ COM |
| GETE00 | Get Error Type Error | Lỗi khi lấy error type |

### 4.6. SN Rule Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| SNRE00 | SN Rule 0 is Error | Ký tự cuối cùng PSN invalid |
| SNRE01 | SN Rule 1 is Error | Ký tự thứ 15 PSN invalid |
| SNRE02 | SN Rule 2 is Error | Ký tự thứ 14 PSN invalid |
| SNRE03 | SN Rule 3 is Error | Ký tự thứ 13 PSN invalid |

### 4.7. Other Errors

| Code | Full Name | Description |
|------|-----------|-------------|
| SetMO | Really MO Not is SET | MO chưa được set |
| CPSN00 | Calibration PCB_PSN Fail | Calibration PSN thất bại |

---

**Summary**: Document này mô tả chi tiết tất cả cấu trúc dữ liệu, protocol communication, PSN format, validation rules và error codes được sử dụng trong hệ thống.

