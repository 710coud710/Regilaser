# Configuration Guide

## 1. File Cấu Hình Sprite_LM.tab

### 1.1. Tổng Quan

File `Sprite_LM.tab` là file cấu hình chính của chương trình, sử dụng format INI (Windows Private Profile).

**Location**: Cùng thư mục với file exe  
**Format**: INI file with sections and key-value pairs  
**Encoding**: ANSI

### 1.2. Cấu Trúc File

```ini
[General]
# Communication Ports
CMD_COM=COM3
FIX_COM=COM4
SFIS_Action=Loading

# Operator Information
OP_Num=OP12345
AllPartSN=PART123456

# Program Information
Title=HANS Laser Marking System Version V1.1
ProductName=ProductABC
StationName=LM_Station_01

# Dialog Settings
IsDialogBeforeTest=1

# PSN Configuration
PSNProgramNo=001
PanelProgramNo=002
FrontPSN_Num=P0714M02
MONum=MO12345678

# Laser Scripts
HANS_LM_Script=Sprite_8PSN.hs
HANS_LM_Script2=Sprite_4PSN.hs

# Laser Configuration
LaserPanelLableEnable=1
LM_Config_Enable=1
LM_Config=CONFIG_TEXT

# Individual PSN Programs (for single panel mode)
PSN1_ProgramNo=001
PSN2_ProgramNo=002
PSN3_ProgramNo=003
PSN4_ProgramNo=004

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

## 2. Chi Tiết Các Tham Số

### 2.1. Section [General]

#### Communication Ports

##### CMD_COM
```ini
CMD_COM=COM3
```
- **Mô tả**: COM port kết nối với CCD (vision system)
- **Type**: String
- **Format**: COMx (x = 1-255)
- **Mặc định**: COM3
- **Baudrate**: 9600 bps
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None

**Lưu ý**: Port này nhận lệnh CHECK1 từ PLC và forward đến CCD, sau đó nhận CHE_OK/CHE_NG từ CCD

---

##### FIX_COM
```ini
FIX_COM=COM4
```
- **Mô tả**: COM port kết nối với PLC
- **Type**: String
- **Format**: COMx
- **Mặc định**: COM4
- **Baudrate**: 9600 bps
- **Protocol**: Custom commands (START1, PRO1_DONE, START2, PRO2_DONE, CHECK1, CHE_OK, CHE_NG, E-STOP)

**Messages từ PLC**:
- `START1`: Bắt đầu test
- `CHECK1`: Yêu cầu CCD check
- `START2`: Sẵn sàng cho script 2

**Messages đến PLC**:
- `PRO1_DONE`: Script 1 hoàn thành
- `PRO2_DONE`: Script 2 hoàn thành
- `CHE_OK`: Vision check OK
- `CHE_NG`: Vision check NG
- `E-STOP`: Emergency stop

---

##### SFIS_Action
```ini
SFIS_Action=Loading
```
- **Mô tả**: Action type cho SFIS
- **Type**: String
- **Giá trị**: Loading, Testing, Packing, etc.
- **Hiển thị**: GroupBox1 caption

---

#### Operator Information

##### OP_Num
```ini
OP_Num=OP12345
```
- **Mô tả**: Operator number
- **Type**: String
- **Max length**: 20 characters
- **Format**: OPxxxxx
- **Hiển thị**: StatusBar Panel[6]
- **Sử dụng**: Gửi đến SFIS khi click EMP button

**Validation**:
```cpp
if (strlen(OP_Number) < 20) {
    // OK
} else {
    ShowMessage("OP Number too long");
    Application->Terminate();
}
```

---

##### AllPartSN
```ini
AllPartSN=PART123456
```
- **Mô tả**: Part serial number cho all part tracing
- **Type**: String
- **Max length**: 12 characters
- **Sử dụng**: Optional, gửi trong NEEDPSN request nếu CK_AllPartSN checked
- **Format SFIS**: `MO(20) + AllPartSN(12) + Panel(20) + NEEDPSN12`

---

#### Program Information

##### Title
```ini
Title=HANS Laser Marking System Version V1.1
```
- **Mô tả**: Tiêu đề chương trình
- **Type**: String
- **Max length**: 100 characters
- **Hiển thị**: 
  - Form caption
  - StatusBar Panel[4] (only version number)

**Extract Version**:
```cpp
StatusBar1->Panels->Items[4]->Text = "Version " + 
    AnsiString(Tab_ProgramTitle).SubString(
        AnsiString(Tab_ProgramTitle).Pos("Version")+8, 3
    );
```

---

##### ProductName
```ini
ProductName=ProductABC
```
- **Mô tả**: Tên sản phẩm
- **Type**: String
- **Max length**: 20 characters
- **Hiển thị**: FormProductName panel
- **Sử dụng**: 
  - Display on UI
  - Registry key for calibration: `Software\Sample Test\{ProductName}_{StationName}`

---

##### StationName
```ini
StationName=LM_Station_01
```
- **Mô tả**: Tên station/trạm
- **Type**: String
- **Max length**: 20 characters
- **Hiển thị**: FormStationName panel (Yellow background, size 26)
- **Sử dụng**: Display và Registry key

---

#### Dialog Settings

##### IsDialogBeforeTest
```ini
IsDialogBeforeTest=1
```
- **Mô tả**: Hiển thị dialog trước khi test
- **Type**: Integer (0 or 1)
- **Values**:
  - `0`: Không hiển thị dialog
  - `1`: Hiển thị dialog xác nhận
- **Mặc định**: 1

---

#### PSN Configuration

##### PSNProgramNo
```ini
PSNProgramNo=001
```
- **Mô tả**: Program number cho PSN marking
- **Type**: String
- **Max length**: 100 characters
- **Format**: 3 digits (001-999)
- **Sử dụng**: General PSN program number

---

##### PanelProgramNo
```ini
PanelProgramNo=002
```
- **Mô tả**: Program number cho panel label marking
- **Type**: String
- **Max length**: 100 characters
- **Format**: 3 digits
- **Sử dụng**: LaserPanelLableEnable=1 mode

---

##### FrontPSN_Num
```ini
FrontPSN_Num=P0714M02
```
- **Mô tả**: 8 ký tự đầu của PSN (prefix cố định)
- **Type**: String
- **Length**: 8 characters
- **Format**: `Pxx14M02` (xx = product code)
- **Sử dụng**: Validation PSN từ SFIS

**Validation Logic**:
```cpp
AnsiString str_FrontPSN_Num = AnsiString(Tab_FrontPSN_Num).SubString(1,8);

// Check PSN1 or PSN12 matches
if (strSFISPSN[0].SubString(1,8) != str_FrontPSN_Num 
    && strSFISPSN[11].SubString(1,8) != str_FrontPSN_Num) {
    ERROR: PSNC08
}
```

**Examples**:
- `P0714M02`: Product code 07
- `P1114M02`: Product code 11

---

##### MONum
```ini
MONum=MO12345678
```
- **Mô tả**: Manufacturing Order Number
- **Type**: String
- **Length**: 10 characters actual (padded to 20 in protocol)
- **Format**: `MOxxxxxxxx`
- **Sử dụng**: 
  - Gửi trong NEEDPSN request
  - Validate với SFIS response
  - Display trên UI

**Confirmation**: User phải confirm MO khi khởi động chương trình

---

#### Laser Scripts

##### HANS_LM_Script
```ini
HANS_LM_Script=Sprite_8PSN.hs
```
- **Mô tả**: Laser marking script file cho PSN 0-7 (Script 1)
- **Type**: String (filename)
- **Max length**: 20 characters
- **Location**: Cùng thư mục với exe
- **Format**: `.hs` file (HANS Laser script)

**Content Example**:
```
// HANS Script for 8 PSN marking
// Text objects: 2D_0, 2D_1, ..., 2D_7
// Optional: 2D_0_title, 2D_1_title, ...
// Variable: PN (Panel Number)
```

**Usage**:
```cpp
AnsiString HANS_Script_str = ExtractFileDir(ParamStr(0)) + "\\" + 
                              AnsiString(Tab_HANS_LM_Script);
HS_LoadMarkFile(HANS_Script_str.c_str());
```

---

##### HANS_LM_Script2
```ini
HANS_LM_Script2=Sprite_4PSN.hs
```
- **Mô tả**: Laser marking script file cho PSN 8-11 (Script 2)
- **Type**: String (filename)
- **Max length**: 20 characters
- **Format**: `.hs` file

**Content Example**:
```
// HANS Script for 4 PSN marking
// Text objects: 2D_8, 2D_9, 2D_10, 2D_11
// Optional: 2D_8_title, 2D_9_title, ...
// Variable: MO (MO Number)
```

---

#### Laser Configuration

##### LaserPanelLableEnable
```ini
LaserPanelLableEnable=1
```
- **Mô tả**: Enable laser marking panel label
- **Type**: Integer (0 or 1)
- **Values**:
  - `0`: Disable panel label marking
  - `1`: Enable panel label marking
- **Mặc định**: 1

---

##### LM_Config_Enable
```ini
LM_Config_Enable=1
```
- **Mô tả**: Enable config text marking
- **Type**: Integer (0 or 1)
- **Values**:
  - `0`: Không mark config text
  - `1`: Mark config text bên cạnh PSN

**Implementation**:
```cpp
if (Tab_LM_Config_Enable) {
    ConfigTextName = "2D_" + AnsiString(i) + "_title";
    ConfigText = AnsiString(Tab_LM_Config).Trim();
    HS_ChangeTextByName(ConfigTextName.c_str(), ConfigText.c_str());
}
```

---

##### LM_Config
```ini
LM_Config=CONFIG_TEXT
```
- **Mô tả**: Config text content to mark
- **Type**: String
- **Max length**: 20 characters
- **Sử dụng**: Mark bên cạnh mỗi PSN nếu LM_Config_Enable=1

**Visual Layout**:
```
[2D_0_title]    [2D_0]
CONFIG_TEXT     P0714M02ABCD0001

[2D_1_title]    [2D_1]
CONFIG_TEXT     P0714M02ABCD0002
```

---

#### Individual PSN Programs

##### PSN1_ProgramNo, PSN2_ProgramNo, PSN3_ProgramNo, PSN4_ProgramNo
```ini
PSN1_ProgramNo=001
PSN2_ProgramNo=002
PSN3_ProgramNo=003
PSN4_ProgramNo=004
```
- **Mô tả**: Program numbers cho single panel mode
- **Type**: String (each)
- **Format**: 3 digits
- **Sử dụng**: Mode laser từng PSN riêng lẻ (hiện tại không sử dụng trong main flow)

---

### 2.2. Section [PASS/FAIL]

##### Pass
```ini
Pass=0
```
- **Mô tả**: Số lượng test PASS
- **Type**: Integer
- **Range**: 0-999999
- **Update**: Auto increment khi test pass
- **Display**: StatusBar Panel[2]
- **Reset**: Menu → Pass To Zero

---

##### Fail
```ini
Fail=0
```
- **Mô tả**: Số lượng test FAIL
- **Type**: Integer
- **Range**: 0-999999
- **Update**: Auto increment khi test fail
- **Display**: StatusBar Panel[3]
- **Reset**: Menu → Fail To Zero

---

### 2.3. Section [SAVELOG]

##### IsLogOnLocal
```ini
IsLogOnLocal=1
```
- **Mô tả**: Enable lưu log lên local drive
- **Type**: Integer (0 or 1)
- **Values**:
  - `0`: Disable local logging
  - `1`: Enable local logging

---

##### LocalLogPath
```ini
LocalLogPath=D:\Logs\Local
```
- **Mô tả**: Đường dẫn lưu log local
- **Type**: String
- **Max length**: 100 characters
- **Format**: Absolute path
- **Auto create**: Yes

**Folder Structure**:
```
D:\Logs\Local\
├─ PASS\
│  └─ 20250114\
│     ├─ Result_PSN0001_120530.txt
│     └─ Resume_Local_Log.csv
└─ FAIL\
   └─ 20250114\
      ├─ Result_PSN0010_130245.txt
      └─ Resume_Local_Log.csv
```

---

##### IsLogOnServer
```ini
IsLogOnServer=1
```
- **Mô tả**: Enable lưu log lên network server
- **Type**: Integer (0 or 1)
- **Values**:
  - `0`: Disable server logging
  - `1`: Enable server logging (auto map network drive)

---

##### ServerDrive
```ini
ServerDrive=Z:
```
- **Mô tả**: Drive letter để map network server
- **Type**: String
- **Format**: `X:` (single letter + colon)
- **Common**: Z:, Y:, etc.

---

##### ServerAddress
```ini
ServerAddress=\\192.168.1.100\share
```
- **Mô tả**: UNC path của network server
- **Type**: String
- **Max length**: 100 characters
- **Format**: `\\server\share` or `\\IP\share`
- **Credentials**: 
  - Username: `oper`
  - Password: `wireless`
  - (Hardcoded in MapNetworkDrive function)

**Examples**:
```ini
ServerAddress=\\192.168.1.100\share
ServerAddress=\\ServerName\LogFolder
ServerAddress=\\10.10.10.50\LaserLogs
```

---

##### ServerLogpath
```ini
ServerLogpath=Z:\Logs\Server
```
- **Mô tả**: Đường dẫn lưu log trên mapped drive
- **Type**: String
- **Max length**: 100 characters
- **Format**: Uses ServerDrive letter
- **Structure**: Same as LocalLogPath

**Example**:
```
Z:\Logs\Server\
├─ PASS\
│  └─ 20250114\
│     ├─ Result_PSN0001_120530.txt
│     └─ Resume_Server_Log.csv
└─ FAIL\
   └─ 20250114\
      ├─ Result_PSN0010_130245.txt
      └─ Resume_Server_Log.csv
```

---

## 3. HANS Laser Script Files

### 3.1. Script File Format (.hs)

HANS Laser script files contain:
- **Text Objects**: Named text elements to mark
- **Graphics**: Lines, shapes, logos
- **Parameters**: Position, size, font, etc.
- **Settings**: Laser power, speed, frequency

### 3.2. Text Object Naming Convention

#### Script 1 (Sprite_8PSN.hs)

**Required Objects**:
```
2D_0    : PSN slot 0 (SFIS PSN[0])
2D_1    : PSN slot 1 (SFIS PSN[1])
2D_2    : PSN slot 2 (SFIS PSN[2])
2D_3    : PSN slot 3 (SFIS PSN[3])
2D_4    : PSN slot 4 (SFIS PSN[4])
2D_5    : PSN slot 5 (SFIS PSN[5])
2D_6    : PSN slot 6 (SFIS PSN[6])
2D_7    : PSN slot 7 (SFIS PSN[7])
PN      : Panel Number
```

**Optional Objects** (if LM_Config_Enable=1):
```
2D_0_title : Config text for PSN 0
2D_1_title : Config text for PSN 1
2D_2_title : Config text for PSN 2
2D_3_title : Config text for PSN 3
2D_4_title : Config text for PSN 4
2D_5_title : Config text for PSN 5
2D_6_title : Config text for PSN 6
2D_7_title : Config text for PSN 7
```

---

#### Script 2 (Sprite_4PSN.hs)

**Required Objects**:
```
2D_8    : PSN slot 8 (SFIS PSN[8])
2D_9    : PSN slot 9 (SFIS PSN[9])
2D_10   : PSN slot 10 (SFIS PSN[10])
2D_11   : PSN slot 11 (SFIS PSN[11])
MO      : MO Number
```

**Optional Objects**:
```
2D_8_title  : Config text for PSN 8
2D_9_title  : Config text for PSN 9
2D_10_title : Config text for PSN 10
2D_11_title : Config text for PSN 11
```

---

### 3.3. Creating HANS Script Files

#### Step 1: Launch MarkingBuilder2

```
Location: C:\Program Files\Keyence\MarkingBuilder2\MarkingBuilder2.exe
```

#### Step 2: Create Text Objects

1. Click "Add Text" tool
2. Set object name (e.g., "2D_0")
3. Set font, size, position
4. Set default text: "TEST"
5. Repeat for all PSN slots

#### Step 3: Add Config Text (Optional)

1. Create text object "2D_0_title"
2. Position next to "2D_0"
3. Set default text: "CONFIG"

#### Step 4: Set Laser Parameters

- **Laser Power**: 30-50% (depends on material)
- **Marking Speed**: 500-1000 mm/s
- **Frequency**: 20-60 kHz
- **Line Spacing**: 0.05-0.1 mm

#### Step 5: Save Script

- File → Save As
- Filename: `Sprite_8PSN.hs` or `Sprite_4PSN.hs`
- Location: Program directory

---

## 4. Registry Settings

### 4.1. Golden PCB Calibration

**Registry Key**:
```
HKEY_LOCAL_MACHINE\Software\Sample Test\{ProductName}_{StationName}
```

**Value**:
```
Name: Test Time
Type: REG_SZ (String)
Data: YYYY_MM_DD HH:MM
Example: 2025_01_14 12:30
```

**Purpose**: Track last calibration time for Golden PCB

**Check Interval**: Configurable (in .tab file, not implemented in current version)

---

## 5. Example Configuration Files

### 5.1. Production Environment

```ini
[General]
CMD_COM=COM3
FIX_COM=COM4
SFIS_Action=Loading
OP_Num=OP99999
AllPartSN=PART000001
Title=HANS Laser Marking System Version V1.1
ProductName=iPhone_Main
StationName=LM_Line1_St01
IsDialogBeforeTest=1
PSNProgramNo=001
PanelProgramNo=002
FrontPSN_Num=P0714M02
MONum=MO20250114
HANS_LM_Script=Sprite_8PSN.hs
HANS_LM_Script2=Sprite_4PSN.hs
LaserPanelLableEnable=1
LM_Config_Enable=1
LM_Config=REV A
PSN1_ProgramNo=001
PSN2_ProgramNo=002
PSN3_ProgramNo=003
PSN4_ProgramNo=004

[PASS/FAIL]
Pass=0
Fail=0

[SAVELOG]
IsLogOnLocal=1
LocalLogPath=D:\LaserLogs\Local
IsLogOnServer=1
ServerDrive=Z:
ServerAddress=\\192.168.10.50\LaserMarkingLogs
ServerLogpath=Z:\Line1\Station01
```

---

### 5.2. Development/Debug Environment

```ini
[General]
CMD_COM=COM1
FIX_COM=COM2
SFIS_Action=Debug
OP_Num=OP00000
AllPartSN=DEBUG
Title=HANS Laser Marking System Version V1.1 DEBUG
ProductName=DEBUG_Product
StationName=DEBUG_Station
IsDialogBeforeTest=0
PSNProgramNo=001
PanelProgramNo=002
FrontPSN_Num=P0714M02
MONum=MO00000000
HANS_LM_Script=Debug_Script1.hs
HANS_LM_Script2=Debug_Script2.hs
LaserPanelLableEnable=0
LM_Config_Enable=0
LM_Config=DEBUG
PSN1_ProgramNo=001
PSN2_ProgramNo=002
PSN3_ProgramNo=003
PSN4_ProgramNo=004

[PASS/FAIL]
Pass=0
Fail=0

[SAVELOG]
IsLogOnLocal=1
LocalLogPath=C:\Temp\LaserDebug
IsLogOnServer=0
ServerDrive=
ServerAddress=
ServerLogpath=
```

---

## 6. Troubleshooting Configuration Issues

### 6.1. COM Port Issues

**Problem**: "Can't open COM port"

**Solutions**:
1. Check COM port exists in Device Manager
2. Check port not used by another application
3. Verify baudrate settings (9600)
4. Check cable connections

---

### 6.2. Network Drive Mapping Issues

**Problem**: "Map server to local fail"

**Solutions**:
1. Check network connectivity: `ping 192.168.1.100`
2. Verify share exists: `\\192.168.1.100\share`
3. Check credentials (oper/wireless)
4. Verify firewall settings
5. Test manual mapping: `net use Z: \\192.168.1.100\share /user:oper wireless`

---

### 6.3. HANS DLL Issues

**Problem**: "Load the <HansAdvInterface.dll> error"

**Solutions**:
1. Verify DLL exists in program directory
2. Check DLL version compatibility
3. Install Visual C++ Redistributable
4. Check Windows compatibility mode

---

### 6.4. Script File Issues

**Problem**: "Laser Marking Script not Find"

**Solutions**:
1. Verify script file exists: `Sprite_8PSN.hs`
2. Check filename matches .tab setting exactly
3. Verify file not corrupted
4. Check file permissions

---

### 6.5. PSN Validation Issues

**Problem**: "PSNC08 PSN Front Error"

**Solutions**:
1. Check FrontPSN_Num setting: `P0714M02`
2. Verify SFIS sending correct PSN format
3. Check PSN format: must be 16 characters
4. Verify first 8 characters match configuration

**Example Check**:
```
FrontPSN_Num = P0714M02
PSN from SFIS = P0714M02ABCD0001
First 8 chars = P0714M02 ✓
```

---

## 7. Best Practices

### 7.1. Configuration Management

1. **Backup**: Backup .tab file before changes
2. **Version Control**: Use Git or similar for .tab and .hs files
3. **Documentation**: Comment changes in .tab file
4. **Testing**: Test in debug mode before production

### 7.2. Security

1. **Network Credentials**: Change default oper/wireless
2. **File Permissions**: Restrict .tab file access
3. **Audit**: Log configuration changes

### 7.3. Maintenance

1. **Regular Backup**: Daily backup of .tab and logs
2. **Monitor**: Check Pass/Fail counters regularly
3. **Calibration**: Golden PCB calibration schedule
4. **Update**: Keep HANS DLL updated

---

**Summary**: Document này cung cấp hướng dẫn chi tiết về tất cả các tham số cấu hình, format file, HANS script, registry settings, và troubleshooting. Mỗi tham số được giải thích rõ ràng về mục đích, format, validation, và usage.

