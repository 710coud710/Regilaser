# HANS Laser Marking System - Documentation

## Tổng Quan

Bộ tài liệu này cung cấp phân tích chi tiết về hệ thống HANS Laser Marking, bao gồm kiến trúc, luồng xử lý, cấu trúc dữ liệu, và hướng dẫn cấu hình.

**Chương trình**: BCM Common Use - HANS Laser Marking System  
**Version**: V1.1 (May 21, 2013)  
**Platform**: C++ Builder, Windows  
**Purpose**: Điều khiển máy laser marking tích hợp với SFIS và PLC

---

## Cấu Trúc Tài Liệu

### 1. [Program Overview](01_program_overview.md)
📘 **Tổng quan về chương trình**

**Nội dung**:
- Giới thiệu hệ thống
- Kiến trúc tổng thể
- Các thành phần chính
- Module và DLL
- Giao tiếp Serial
- Cấu trúc dữ liệu
- Workflow tổng quát
- Tính năng đặc biệt
- State machine
- Error handling
- Logging system

**Đối tượng**: Tất cả người dùng, đặc biệt là người mới bắt đầu

**Highlights**:
- Single instance protection với Mutex
- Multi-threading (send_plc)
- 3 Serial COM ports (SFIS, CMD, FIX)
- Golden PCB calibration
- Network drive auto-mapping
- Base-32 PSN conversion

---

### 2. [Detailed Flow](02_detailed_flow.md)
🔄 **Luồng xử lý chi tiết**

**Nội dung**:
- Application entry point (BCMBCB.cpp)
- MainForm initialization flow
  - FormCreate event
  - FormShow event
- Main test flow
  - Trigger test (START1)
  - Auto_test() function
  - Receive PSN from SFIS
  - Validation flow
- Laser marking process
  - Phase 1: Script 1 (PSN 0-7)
  - Phase 2: Send PRO1_DONE, wait START2
  - Phase 3: Script 2 (PSN 8-11)
  - Phase 4: Send PRO2_DONE
  - Phase 5: Report result
- Result handling
- Complete sequence diagram

**Đối tượng**: Developers, maintenance engineers

**Highlights**:
- Step-by-step workflow với code snippets
- Timing diagrams
- Validation layers (6 rules)
- Retry mechanisms
- Error recovery procedures
- Detailed sequence diagrams

---

### 3. [Data Structures](03_data_structures.md)
📊 **Cấu trúc dữ liệu và giao thức**

**Nội dung**:
- Data structures
  - SFCData structure
  - Logframe structure
  - Global variables
- Communication protocols
  - SFIS protocol (detailed)
  - PLC protocol (detailed)
  - CCD protocol
  - HANS DLL protocol
- PSN format and validation
  - PSN structure (16 chars)
  - Base-32 encoding/decoding
  - Validation rules (6 rules)
- Error codes reference
  - SFIS errors
  - PSN compare errors
  - Laser marking errors
  - Communication errors
  - SN rule errors

**Đối tượng**: Developers, system integrators

**Highlights**:
- Protocol message formats với byte-level details
- Base-32 conversion algorithm
- PSN validation rules
- Complete error code list (30+ codes)
- DLL function signatures

---

### 4. [Functions Reference](04_functions_reference.md)
📖 **Tài liệu tham khảo hàm**

**Nội dung**:
- Event handlers (20+ functions)
  - Form lifecycle events
  - Button click events
  - Communication event handlers
  - Timer events
  - Menu item events
- Core functions (15+ functions)
  - Configuration functions
  - Communication functions
  - Test flow functions
  - Status and display functions
  - Logging functions
  - Utility functions
  - PSN processing functions
  - UI helper functions
- Thread class (send_plc)

**Đối tượng**: Developers

**Highlights**:
- Function signatures
- Parameters và return values
- Implementation details
- Usage examples
- Related functions cross-reference

---

### 5. [Configuration Guide](05_configuration_guide.md)
⚙️ **Hướng dẫn cấu hình**

**Nội dung**:
- File cấu hình Sprite_LM.tab
  - Tổng quan
  - Cấu trúc file
  - Chi tiết các tham số (40+ parameters)
- HANS Laser script files
  - Script file format (.hs)
  - Text object naming convention
  - Creating script files
- Registry settings
  - Golden PCB calibration
- Example configuration files
  - Production environment
  - Development/debug environment
- Troubleshooting
  - COM port issues
  - Network drive issues
  - HANS DLL issues
  - Script file issues
  - PSN validation issues
- Best practices
  - Configuration management
  - Security
  - Maintenance

**Đối tượng**: System administrators, operators, engineers

**Highlights**:
- Complete .tab file reference
- HANS script naming conventions
- Troubleshooting guide
- Example configurations
- Best practices

---

## Quick Start

### Đọc Theo Vai Trò

#### 🔰 Operator / User
1. Đọc **Program Overview** (phần 1-6)
2. Đọc **Configuration Guide** (phần troubleshooting)
3. Tham khảo error codes trong **Data Structures**

#### 🔧 Maintenance Engineer
1. Đọc **Program Overview** (toàn bộ)
2. Đọc **Configuration Guide** (toàn bộ)
3. Đọc **Detailed Flow** (phần test flow)
4. Tham khảo **Data Structures** (protocols và error codes)

#### 👨‍💻 Software Developer
1. Đọc **Program Overview** (toàn bộ)
2. Đọc **Detailed Flow** (toàn bộ)
3. Đọc **Data Structures** (toàn bộ)
4. Đọc **Functions Reference** (toàn bộ)
5. Tham khảo **Configuration Guide** khi cần

#### 🏭 System Integrator
1. Đọc **Program Overview** (phần architecture)
2. Đọc **Data Structures** (phần protocols)
3. Đọc **Configuration Guide** (phần network và COM)
4. Tham khảo **Detailed Flow** cho sequence diagrams

---

## Đọc Theo Chủ Đề

### 🔌 Giao Tiếp (Communication)
- **Program Overview**: Section 3.3 (Serial Communication)
- **Detailed Flow**: Section 1.3, 5.2
- **Data Structures**: Section 2 (Complete protocols)
- **Functions Reference**: Section 2.2 (Communication functions)
- **Configuration Guide**: Section 2.1 (COM ports)

### 🏭 SFIS Integration
- **Program Overview**: Section 6 (Workflow)
- **Detailed Flow**: Section 3.2, 3.3, 5
- **Data Structures**: Section 2.1 (SFIS protocol)
- **Functions Reference**: Section 2.3 (Test flow functions)

### 🤖 PLC Integration
- **Program Overview**: Section 3.3
- **Detailed Flow**: Section 3.1, 4.1
- **Data Structures**: Section 2.2 (PLC protocol)
- **Functions Reference**: Section 1.3 (FIX_COMReceiveData)

### 💾 Laser Marking
- **Program Overview**: Section 3.2 (DLL)
- **Detailed Flow**: Section 4 (Complete marking process)
- **Data Structures**: Section 2.4 (HANS DLL protocol)
- **Functions Reference**: Section 1.2 (FormStartBtnClick)
- **Configuration Guide**: Section 3 (HANS scripts)

### 📝 PSN Processing
- **Program Overview**: Section 4 (Data structures)
- **Detailed Flow**: Section 3.3, 3.4 (Validation)
- **Data Structures**: Section 3 (PSN format and validation)
- **Functions Reference**: Section 2.7 (PSN processing functions)
- **Configuration Guide**: Section 2.1 (PSN configuration)

### 📊 Logging System
- **Program Overview**: Section 10 (Logging system)
- **Detailed Flow**: Section 6 (Logging flow)
- **Functions Reference**: Section 2.5 (Logging functions)
- **Configuration Guide**: Section 2.3 (Log paths)

### ⚠️ Error Handling
- **Program Overview**: Section 9 (Error handling)
- **Detailed Flow**: Section 3.4 (Validation flow)
- **Data Structures**: Section 4 (Error codes)
- **Configuration Guide**: Section 6 (Troubleshooting)

---

## Key Concepts

### 1. Test Flow Overview

```
PLC sends START1
    ↓
Request PSN from SFIS (12 PSNs)
    ↓
Receive and validate PSN
    ↓
Mark Script 1 (PSN 0-7)
    ↓
Send PRO1_DONE → Wait START2
    ↓
Mark Script 2 (PSN 8-11)
    ↓
Send PRO2_DONE
    ↓
Report PASS/FAIL to SFIS
    ↓
Save logs → Ready for next
```

### 2. PSN Format

```
Position: 1234567890123456
Format:   P0714M02ABCD0001
          |<-8->|  |<-4->|
          Front   Serial (Base-32)
```

### 3. Communication Ports

```
SFIS_COM (COM port from .tab)
    ↕ 9600 bps
SFIS Server

CMD_COM (COM3 default)
    ↕ 9600 bps
CCD System

FIX_COM (COM4 default)
    ↕ 9600 bps
PLC Controller
```

### 4. Validation Layers

1. **Length Check**: PSN must be 16 chars
2. **Front Check**: First 8 chars match FrontPSN_Num
3. **Consistency Check**: PSN1 and PSN12 first 10 match
4. **Sequence Check**: PSN12 - PSN1 >= 11 (Base-32)
5. **MO/Panel Check**: Match with configured values
6. **Character Check**: Valid Base-32 characters only

### 5. Error Code Format

```
[Category][Number] [Description]

Examples:
SRPE00: SFIS Receive PSN Error
PSNC08: PSN Front Error
LMPSN1: Laser Marking PSN1 Fail
```

---

## System Requirements

### Hardware
- **PC**: Windows 7/10, Intel i5 or above, 4GB RAM
- **COM Ports**: 3× RS-232 serial ports (or USB adapters)
- **Laser**: HANS Laser machine with DLL support
- **Network**: 100Mbps Ethernet for server logging

### Software
- **OS**: Windows 7 SP1 or later
- **Runtime**: Visual C++ Redistributable (included with C++ Builder)
- **DLL**: HansAdvInterface.dll (version compatible)
- **Tools**: MarkingBuilder2.exe (for script editing)

### Network
- **SFIS Server**: Accessible via serial or network
- **Log Server**: SMB share with oper/wireless credentials
- **PLC**: Direct serial connection

---

## File Structure

```
Program Directory/
├── BCMBCB.exe                  # Main executable
├── Sprite_LM.tab               # Configuration file
├── Sprite_8PSN.hs              # Laser script 1
├── Sprite_4PSN.hs              # Laser script 2
├── HansAdvInterface.dll        # HANS DLL
├── KeyboardHook.dll            # Keyboard hook DLL
├── SPComm components           # Serial communication DLLs
├── Counter.txt                 # Pass/Fail counter backup
└── docs/                       # Documentation
    ├── README.md               # This file
    ├── 01_program_overview.md
    ├── 02_detailed_flow.md
    ├── 03_data_structures.md
    ├── 04_functions_reference.md
    └── 05_configuration_guide.md
```

---

## Version History

### V1.1 (May 21, 2013)
- Fix program for laser PSN
- Stable release for production

### V1.0 (April 12, 2013)
- Initial release
- Basic laser marking functionality

---

## Support

### Documentation Issues
Nếu phát hiện lỗi trong tài liệu hoặc cần thêm thông tin:
1. Check các file .md khác trong thư mục docs/
2. Xem code comments trong source files
3. Tham khảo error codes trong Data Structures

### Technical Support
- **Code Analysis**: Xem Functions Reference
- **Configuration**: Xem Configuration Guide
- **Troubleshooting**: Xem Configuration Guide Section 6
- **Protocol Details**: Xem Data Structures Section 2

---

## Appendix

### A. Useful Tools

1. **Serial Port Monitor**: Debug COM communication
   - RealTerm
   - HTerm
   - Serial Port Monitor by Eltima

2. **Network Tools**: Debug network drive mapping
   - `net use` command
   - Windows Computer Management

3. **Registry Editor**: View calibration data
   - `regedit.exe`
   - Path: `HKLM\Software\Sample Test\`

4. **MarkingBuilder2**: Edit laser scripts
   - `C:\Program Files\Keyence\MarkingBuilder2\`

### B. Common Commands

**Map Network Drive**:
```cmd
net use Z: \\192.168.1.100\share /user:oper wireless
```

**Check COM Ports**:
```cmd
mode
```

**View Registry**:
```cmd
reg query "HKLM\Software\Sample Test"
```

**Kill Process**:
```cmd
taskkill /F /IM BCMBCB.exe
```

### C. Glossary

- **MO**: Manufacturing Order
- **PSN**: Product Serial Number
- **SFIS**: Shop Floor Information System
- **PLC**: Programmable Logic Controller
- **CCD**: Charge-Coupled Device (Camera/Vision System)
- **TE**: Test Equipment (this program)
- **DLL**: Dynamic Link Library
- **COM**: Communication Port (Serial)
- **UNC**: Universal Naming Convention (network path)
- **Base-32**: Numeral system with 32 digits (0-9, A-H, J-N, P-X)

---

## Document Information

**Created**: January 2025  
**Language**: Vietnamese  
**Format**: Markdown  
**Total Pages**: ~150 (if printed)  
**Total Words**: ~35,000  

**Authors**: AI Analysis of C++ Builder Source Code  
**Source Files Analyzed**:
- BCMBCB.cpp (42 lines)
- MainForm.cpp (2,945 lines)
- MainForm.h (213 lines)
- send_plc.cpp (53 lines)
- send_plc.h (18 lines)
- Unit_QuestionDlg.cpp (21 lines)
- Unit_QuestionDlg.h (33 lines)

**Analysis Coverage**:
- ✅ All functions documented
- ✅ All protocols analyzed
- ✅ All data structures explained
- ✅ All configurations detailed
- ✅ Error codes catalogued
- ✅ Workflows diagrammed

---

## License

This documentation is provided as-is for the HANS Laser Marking System. All rights reserved by the original software authors and Foxconn.

---

**End of README**

