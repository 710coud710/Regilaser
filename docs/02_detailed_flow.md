# Luồng Xử Lý Chi Tiết

## 1. Application Entry Point (BCMBCB.cpp)

### 1.1. WinMain Function Flow

```cpp
int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int)
{
    // Step 1: Check Single Instance
    HANDLE Mutex;
    const char ProgramName[] = "BCMCommonUse";
    
    Mutex = OpenMutex(MUTEX_ALL_ACCESS, false, ProgramName);
    if (Mutex == NULL) {
        // First instance - Create mutex
        Mutex = CreateMutex(NULL, true, ProgramName);
    } else {
        // Already running - Show error and exit
        ShowMessage("Program already Running!!!");
        return 0;
    }
    
    // Step 2: Initialize Application
    Application->Initialize();
    
    // Step 3: Create Forms
    Application->CreateForm(__classid(TForm1), &Form1);
    Application->CreateForm(__classid(TQuestionDlg), &QuestionDlg);
    
    // Step 4: Run Application
    Application->Run();
    
    // Step 5: Cleanup
    ReleaseMutex(Mutex);
    return 0;
}
```

### 1.2. Sequence Diagram

```
User                Application              Mutex                Forms
 │                      │                      │                    │
 │──Start Program──────►│                      │                    │
 │                      │──OpenMutex()────────►│                    │
 │                      │◄─────NULL────────────│                    │
 │                      │──CreateMutex()──────►│                    │
 │                      │◄──────OK─────────────│                    │
 │                      │──Initialize()────────┼───────────────────►│
 │                      │──CreateForm(TForm1)──┼───────────────────►│
 │                      │──CreateForm(Dialog)──┼───────────────────►│
 │                      │──Run()───────────────┼───────────────────►│
 │◄──Show Main Window──┼──────────────────────┼────────────────────│
```

## 2. MainForm Initialization Flow

### 2.1. FormCreate Event (Line 141-166)

```
FormCreate()
    │
    ├─► Get current path
    │     chrCurrentPath = ExtractFileDir(ParamStr(0))
    │
    ├─► Build .tab file path
    │     chrTabPath = currentPath + "\\Sprite_LM.tab"
    │
    ├─► Check if .tab file exists
    │     if (!FileExists(chrTabPath))
    │         ShowMessage("Can't found...")
    │         Application->Terminate()
    │
    ├─► Get PC hostname
    │     WSAStartup()
    │     gethostname(szHostName, 128)
    │     gethostbyname(szHostName)
    │     strPCName = host->h_name.SubString(1,12)
    │
    └─► Display PC name in StatusBar
          StatusBar1->Panels->Items[8]->Text = strPCName
```

### 2.2. FormShow Event (Line 168-362)

```
FormShow()
    │
    ├─► [1] Hide unnecessary controls
    │     danbao_xuanze->Visible = false
    │     Keyboard1->Enabled = false
    │     HookOn1->Enabled = false
    │
    ├─► [2] Load settings from .tab file
    │     GetTabSettingAndShow()
    │       │
    │       ├─► Read COM ports (CMD_COM, FIX_COM)
    │       ├─► Read SFIS_Action
    │       ├─► Read OP_Number
    │       ├─► Read AllPartSN
    │       ├─► Read Product/Station names
    │       ├─► Read program numbers
    │       ├─► Read MO_Number
    │       ├─► Read Pass/Fail counters
    │       └─► Read log paths (Local/Server)
    │
    ├─► [3] Setup network drive (if enabled)
    │     if (Tab_IsLogOnServer)
    │         MapNetworkDrive(Tab_ServerDrive, Tab_ServerAddress, 
    │                         error, "oper", "wireless")
    │
    ├─► [4] Create log directories
    │     if (Tab_IsLogOnLocal)
    │         ForceDirectories(Tab_LocalLogPath)
    │     if (Tab_IsLogOnServer)
    │         ForceDirectories(Tab_ServerLogPath)
    │
    ├─► [5] Load HANS DLL and Initialize
    │     hInstance = LoadLibrary("HansAdvInterface.dll")
    │     if (hInstance == NULL)
    │         ShowMessage("Load DLL error")
    │         return
    │     
    │     HS_InitialMachine = GetProcAddress(hInstance, "HS_InitialMachine")
    │     i_function_Return = HS_InitialMachine(NULL)
    │     if (i_function_Return != 0)
    │         ShowMessage("Initial HANS Machine fail")
    │         Application->Terminate()
    │
    ├─► [6] Initialize COM ports
    │     ComboBoxSFISCOMChange()  // SFIS COM
    │     ComboBoxCMDCOMChange()   // CMD & FIX COM
    │
    ├─► [7] Setup UI display
    │     FormStationName->Caption = Tab_StationName
    │     FormProductName->Caption = Tab_ProductName
    │     StatusBar1 update Pass/Fail/Version
    │
    ├─► [8] Confirm MO Number
    │     QuestionYesNO("确认当前工单是否为：" + MO_Number)
    │     if (NO) → Allow user to input new MO
    │     WriteIniValue("General", "MONum", new_MO, chrTabPath)
    │
    ├─► [9] Check SMT Type (E5 or H7)
    │     type_str = InputBox("请确认您的PCB是哪一批", "", "")
    │     if (type_str == "E5")
    │         PSN_title = Tab_FrontPSN_Num
    │     else if (type_str == "H7")
    │         PSN_title = "P11"
    │     else
    │         ShowMessage("输入类型错误")
    │         Application->Terminate()
    │
    └─► [10] Click EMP_btn (Send UNDO to SFIS)
          EMP_btn->Click()
```

### 2.3. State Diagram

```
┌──────────────┐
│ Application  │
│   Start      │
└──────┬───────┘
       │
       ├─ FormCreate
       │    └─► Load .tab path
       │        Check file exists
       │        Get PC name
       │
       ├─ FormShow
       │    ├─► Load all settings
       │    ├─► Setup network
       │    ├─► Init HANS DLL
       │    ├─► Connect COM ports
       │    ├─► Confirm MO
       │    └─► Check SMT type
       │
┌──────▼───────┐
│ Ready State  │
│ (Stand By)   │
└──────────────┘
```

## 3. Main Test Flow

### 3.1. Trigger Test (START1 from PLC)

```
FIX_COMReceiveData() [Line 2674-2723]
    │
    ├─► Receive data from PLC
    │     chrBuffer = (char*)Buffer
    │     F_RecvBuffer += chrBuffer
    │
    ├─► Check if START1 signal
    │     if (!IsRunStatus && strReceive.Pos("START1"))
    │         IsRunStatus = true
    │         IsPassDCTResponse = false
    │         Clear memo/debug listbox
    │         Auto_test()  // ◄── Trigger test sequence
    │
    ├─► Check if CHECK1 signal (từ CCD)
    │     if (strReceive.Pos("CHECK1"))
    │         CMD_COM->WriteCommData("CHECK1")
    │         Wait for CHE_OK or CHE_NG
    │
    └─► Check if START2 signal
          if (strReceive.Pos("START2"))
              GetStart2 = true
```

### 3.2. Auto_test() Function (Line 2032-2101)

```
Auto_test()
    │
    ├─► Hide single panel controls
    │     danbao_xuanze->Visible = false
    │     danbao_lable->Visible = false
    │
    ├─► Initialize
    │     FormSN->Text = MO_Number.Trim()
    │     InitFailResumeLog()
    │     Logcsv.clear()
    │     Panel_Number = ""
    │     psn_i = 12  // Request 12 PSNs
    │
    ├─► Build SFIS request string
    │     if (CK_AllPartSN->Checked)
    │         // Format: MO(20) + AllPartSN(12) + Panel(20) + "NEEDPSN12"
    │         tempsfc.sprintf("%-20s%-12s%-20sNEEDPSN%d\r\n",
    │                         MO_Number, FormAllPart->Text.Trim(),
    │                         Panel_Number, psn_i)
    │     else
    │         // Format: MO(20) + Panel(20) + "NEEDPSN12"
    │         tempsfc.sprintf("%-20s%-20sNEEDPSN%d\r\n",
    │                         MO_Number, Panel_Number, psn_i)
    │
    └─► Send to SFIS
          SFIS_COM->WriteCommData(tempsfc.c_str(), strlen(tempsfc.c_str()))
          SFIS_memo->Lines->Add("TE Send SFC:" + tempsfc)
          DebugListBox->Lines->Add("TE Send SFC:" + tempsfc)
```

### 3.3. Receive PSN from SFIS (Line 570-852)

```
SFIS_COMReceiveData()
    │
    ├─► Receive buffer and parse
    │     chrReceBuffer = (char*)Buffer
    │     iTempLen = strlen(chrReceBuffer)
    │
    ├─► Check message length
    │     Expected: 20+20+20*12+4 = 284 bytes
    │     (MO + PanelNO + PSN[12] + Status)
    │
    ├─► Parse data (iTempStatus = 1)
    │     strncpy(chrSFISMO, chrReceBuffer, 10)           // MO: 10 bytes
    │     strncpy(chrPanelNO, chrReceBuffer+20, 9)        // Panel: 9 bytes
    │     strncpy(chrSFISPSN[0], chrReceBuffer+40, 16)    // PSN1: 16 bytes
    │     strncpy(chrSFISPSN[1], chrReceBuffer+60, 16)    // PSN2: 16 bytes
    │     ...
    │     strncpy(chrSFISPSN[11], chrReceBuffer+260, 16)  // PSN12: 16 bytes
    │     strncpy(chrSFISStatus, chrReceBuffer+280, 4)    // Status: 4 bytes
    │
    ├─► Validate PSN format
    │     [V1] Check PSN front matches PSN_title
    │         if (strSFISPSN[i].Pos(PSN_title))
    │             ERROR: PSNC03 (PSN Front Error)
    │     
    │     [V2] Check first 8 chars of PSN1 and PSN12
    │         if (strSFISPSN[0].SubString(1,8) != Tab_FrontPSN_Num
    │             && strSFISPSN[11].SubString(1,8) != Tab_FrontPSN_Num)
    │             ERROR: PSNC08 (PSN Front Error)
    │     
    │     [V3] Check PSN1 and PSN12 first 10 bytes match
    │         if (strSFISPSN[0].SubString(3,10) != strSFISPSN[11].SubString(3,10))
    │             ERROR: PSNC10 (PSN Compare Error)
    │     
    │     [V4] Check PSN sequence (last 4 chars base-32)
    │         int_PSN0 = PSNSub4_32To10(strSFISPSN[0])
    │         int_PSN11 = PSNSub4_32To10(strSFISPSN[11])
    │         if ((int_PSN11 - int_PSN0) < 11)
    │             ERROR: ComPSN (PSN sequence error)
    │     
    │     [V5] Check MO and Panel Number
    │         if (MO_Number != chrSFISMO || Panel_Number != chrPanelNO)
    │             ERROR: SRPEMO (Receive MO/PO Error)
    │     
    │     [V6] Check PSN length (16 characters)
    │         if (all PSNs not 16 chars)
    │             ERROR: SRPE00 (Receive PSN Error)
    │
    ├─► Append to log CSV
    │     AppendLogcsv("Panel_Lable", Panel_Number)
    │     AppendLogcsv("MO_Number", MO_Number)
    │     for (i=0; i<12; i++)
    │         AppendLogcsv("PSN_" + i, strSFISPSN[i])
    │
    └─► Trigger marking process
          if (FormSFISStatus->Caption == "SFIS ON")
              FormStartBtnClick()  // ◄── Start laser marking
```

### 3.4. Validation Flow Chart

```
Receive PSN Data
      │
      ├─► Length Check (284 bytes?)
      │     │  NO → Error: Invalid message
      │     └─ YES
      │
      ├─► Parse 12 PSNs
      │
      ├─► [V1] PSN Front Check
      │     │  Contains PSN_title? → Error: PSNC03
      │     └─ OK
      │
      ├─► [V2] First 8 chars check
      │     │  Not match Tab_FrontPSN_Num? → Error: PSNC08
      │     └─ OK
      │
      ├─► [V3] PSN1 vs PSN12 (10 bytes)
      │     │  Not match? → Error: PSNC10
      │     └─ OK
      │
      ├─► [V4] Sequence Check (Base-32)
      │     │  Diff < 11? → Error: ComPSN
      │     └─ OK
      │
      ├─► [V5] MO/Panel Check
      │     │  Not match? → Error: SRPEMO
      │     └─ OK
      │
      ├─► [V6] Length Check (16 chars)
      │     │  Not 16? → Error: SRPE00
      │     └─ OK
      │
      └─► All Valid → Start Marking
```

## 4. Laser Marking Process

### 4.1. FormStartBtnClick() Overview (Line 854-1334)

```
FormStartBtnClick()
    │
    ├─► Check if running
    │     if (!IsRunStatus) return
    │
    ├─► [PHASE 1] Mark Script 1 (PSN 0-7)
    │     │
    │     ├─► ShowStatus(0) // Status: Marking
    │     │
    │     ├─► Load marking file 1
    │     │     HANS_Script_str = currentPath + Tab_HANS_LM_Script
    │     │     HS_LoadMarkFile(HANS_Script_str.c_str())
    │     │
    │     ├─► Set text for PSN 0-7
    │     │     for (i=0; i<8; i++)
    │     │         TextName = "2D_" + i
    │     │         Text = strSFISPSN[i]
    │     │         HS_ChangeTextByName(TextName, Text)
    │     │         if (Tab_LM_Config_Enable)
    │     │             ConfigTextName = "2D_" + i + "_title"
    │     │             ConfigText = Tab_LM_Config
    │     │             HS_ChangeTextByName(ConfigTextName, ConfigText)
    │     │
    │     ├─► Set Panel Number
    │     │     HS_ChangeTextByName("PN", Panel_Number)
    │     │
    │     ├─► Start marking
    │     │     HS_Mark(0, false, false, 500, true)
    │     │
    │     ├─► Wait for completion (max 60s)
    │     │     for (i=0; i<60; i++)
    │     │         Sleep(500)
    │     │         HS_IsMarkEnd(&flag)
    │     │         if (flag == 1) break      // Complete
    │     │         if (flag == 2) ERROR      // Exception Stop
    │     │
    │     └─► Close marking file
    │           HS_CloseMarkFile(Tab_HANS_LM_Script, false)
    │
    ├─► [PHASE 2] Send PRO1_DONE to PLC
    │     │
    │     └─► Retry 4 times
    │           for (i=0; i<4; i++)
    │               FIXWriteCommDataWaitFor("PRO1_DONE", "PRO1_DONE", 3000)
    │               if (success || GetStart2) break
    │               if (i==3) ShowStatus(2) // FAIL
    │
    ├─► [PHASE 3] Wait for START2 (max 9s)
    │     │
    │     └─► for (j=0; j<9; j++)
    │           if (F_RecvBuffer.Pos("START2")) break
    │           Delay(1000)
    │
    ├─► [PHASE 4] Mark Script 2 (PSN 8-11)
    │     │
    │     ├─► Load marking file 2
    │     │     HANS_Script2_str = currentPath + Tab_HANS_LM_Script2
    │     │     HS_LoadMarkFile(HANS_Script2_str.c_str())
    │     │
    │     ├─► Set MO Number
    │     │     HS_ChangeTextByName("MO", MO_Number)
    │     │
    │     ├─► Set text for PSN 8-11
    │     │     for (i=8; i<12; i++)
    │     │         TextName = "2D_" + i
    │     │         Text = strSFISPSN[i]
    │     │         HS_ChangeTextByName(TextName, Text)
    │     │         if (Tab_LM_Config_Enable)
    │     │             ConfigTextName = "2D_" + i + "_title"
    │     │             ConfigText = Tab_LM_Config
    │     │             HS_ChangeTextByName(ConfigTextName, ConfigText)
    │     │
    │     ├─► Start marking
    │     │     HS_Mark(0, false, false, 500, true)
    │     │
    │     ├─► Wait for completion (max 60s)
    │     │     Similar to Phase 1
    │     │
    │     └─► Close marking file
    │           HS_CloseMarkFile(Tab_HANS_LM_Script2, false)
    │
    ├─► [PHASE 5] Complete and report
    │     │
    │     ├─► OnPass() // Internal pass handling
    │     │
    │     ├─► Send PRO2_DONE to PLC (retry 3 times)
    │     │
    │     ├─► Check SFIS response
    │     │     if (!IsPassDCTResponse && CK_AllPartSN->Checked)
    │     │         FIXWriteCommDataWaitFor("E-STOP")
    │     │         ShowStatus(2) // FAIL
    │     │     else
    │     │         ShowStatus(1) // PASS
    │     │
    │     └─► IsRunStatus = false
    │
    └─► return
```

### 4.2. Marking Timeline

```
Time    Event                           Status
────────────────────────────────────────────────────────────
00:00   FormStartBtnClick()             Marking (Yellow)
00:01   Load Script 1
00:02   Set PSN 0-7 text
00:03   HS_Mark() - Start marking
00:03~  Wait for completion (flag)
  30s   
00:30   HS_CloseMarkFile()
00:31   Send PRO1_DONE to PLC
00:32   Wait for START2
00:33~  Load Script 2
  41s   Set PSN 8-11 text
        HS_Mark() - Start marking
00:41~  Wait for completion
  71s
01:11   HS_CloseMarkFile()
01:12   OnPass()
01:13   Send PRO2_DONE to PLC
01:14   Check SFIS response
01:15   ShowStatus(Pass/Fail)           Pass (Green) / Fail (Red)
```

### 4.3. Detailed Phase Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    MARKING PROCESS                       │
└─────────────────────────────────────────────────────────┘

[PHASE 1: Script 1]
    Load File (script1.hs)
         │
         ├─► Set 2D_0 = PSN[0]
         ├─► Set 2D_1 = PSN[1]
         ├─► Set 2D_2 = PSN[2]
         ├─► Set 2D_3 = PSN[3]
         ├─► Set 2D_4 = PSN[4]
         ├─► Set 2D_5 = PSN[5]
         ├─► Set 2D_6 = PSN[6]
         ├─► Set 2D_7 = PSN[7]
         ├─► Set PN = Panel_Number
         │
         ├─► HS_Mark()
         │     │
         │     └─► Wait loop (60s max)
         │           HS_IsMarkEnd(&flag)
         │           flag=0: Marking...
         │           flag=1: Complete ✓
         │           flag=2: Exception ✗
         │
         └─► Close File

[Wait for PLC]
    Send PRO1_DONE (retry 4x)
         │
         └─► Wait START2 (9s max)

[PHASE 2: Script 2]
    Load File (script2.hs)
         │
         ├─► Set MO = MO_Number
         ├─► Set 2D_8 = PSN[8]
         ├─► Set 2D_9 = PSN[9]
         ├─► Set 2D_10 = PSN[10]
         ├─► Set 2D_11 = PSN[11]
         │
         ├─► HS_Mark()
         │     │
         │     └─► Wait loop (60s max)
         │
         └─► Close File

[Complete]
    OnPass()
         │
         ├─► Send PRO2_DONE
         │
         └─► Report to SFIS
```

## 5. Result Handling

### 5.1. OnPass() Function (Line 1725-1755)

```
OnPass()
    │
    ├─► Add to debug log
    │     DebugListBox->Lines->Add("-------->Test Pass")
    │
    └─► if (IsSFISON)
          OnSFISPass()  // Send to SFIS
```

### 5.2. OnSFISPass() Function (Line 1757-1791)

```
OnSFISPass()
    │
    ├─► Set status
    │     IsRunStatus = false
    │
    ├─► Build SFIS message
    │     Format: MO(20) + Panel(20) + "END\r\n"
    │     tosfcdata.sprintf("%-20s%-20sEND\r\n", MO_Number, Panel_Number)
    │
    ├─► Send to SFIS (retry 3 times)
    │     for (i=1; i<4; i++)
    │         SFIS_COM->WriteCommData(tosfcdata)
    │         SFIS_memo->Lines->Add("TE To SFC[" + i + "]:" + tosfcdata)
    │         delay_run(100)
    │         if (IsPassDCTResponse) return  // Got ACK
    │
    └─► Wait for SFIS response "ENDPASS"
```

### 5.3. ShowStatus() Function (Line 1552-1688)

```
ShowStatus(StatusMode)
    │
    ├─► case 0: Marking
    │     │
    │     ├─► Start timer
    │     │     iStartTime = clock()
    │     │     CountTestTimer->Enabled = true
    │     │
    │     ├─► Clear error
    │     │     memset(chrErrorCode, '\0')
    │     │     FormErrorCode->Caption = ""
    │     │
    │     └─► Update UI
    │           P_F_Status->Color = clYellow
    │           P_F_Status->Caption = "Marking"
    │           TestItem->Caption = "Start test"
    │
    ├─► case 1: Pass
    │     │
    │     ├─► Stop test timer, start free timer
    │     │     CountTestTimer->Enabled = false
    │     │     CountFreeTimer->Enabled = true
    │     │
    │     ├─► Update counters
    │     │     Tab_Pass++
    │     │     WriteIniValue("PASS/FAIL", "Pass", Tab_Pass)
    │     │     StatusBar1->Update()
    │     │
    │     ├─► Save logs
    │     │     SaveAllLog("PASS")
    │     │     AppendLogcsv("Test_Result", "PASS")
    │     │     SaveResumeLog("PASS")
    │     │
    │     └─► Update UI
    │           P_F_Status->Color = clLime
    │           P_F_Status->Caption = "Pass"
    │           TestItem->Caption = "Test Pass"
    │
    ├─► case 2: Fail
    │     │
    │     ├─► Display error
    │     │     FormErrorCode->Caption = chrErrorCode
    │     │
    │     ├─► Update counters
    │     │     Tab_Fail++
    │     │     WriteIniValue("PASS/FAIL", "Fail", Tab_Fail)
    │     │
    │     ├─► Save logs
    │     │     SaveAllLog("FAIL")
    │     │     AppendLogcsv("Test_Result", "FAIL")
    │     │     SaveResumeLog("FAIL")
    │     │
    │     ├─► Reset status
    │     │     IsRunStatus = false
    │     │     EMP_btn->Enabled = true
    │     │
    │     └─► Update UI
    │           P_F_Status->Color = clRed
    │           P_F_Status->Caption = "Fail"
    │           TestItem->Caption = "Test Fail"
    │
    └─► case 3: Stand By
          │
          ├─► Clear display
          │     FormErrorCode->Caption = ""
          │     FormSN->Text = ""
          │
          ├─► Reset status
          │     IsRunStatus = false
          │     EMP_btn->Enabled = true
          │     iSec = 0
          │
          └─► Update UI
                P_F_Status->Color = clAqua
                P_F_Status->Caption = "StandBy"
                TestItem->Caption = "Stand By"
```

## 6. Logging System

### 6.1. SaveAllLog() Function (Line 1401-1437)

```
SaveAllLog(Result)  // Result = "PASS" or "FAIL"
    │
    ├─► Get current datetime
    │     dtTempData = Now()
    │
    ├─► Build folder paths
    │     localresultfile = Tab_LocalLogPath + "\\" + Result
    │     serverresultfile = Tab_ServerLogPath + "\\" + Result
    │
    ├─► Create directories if not exist
    │     ForceDirectories(localresultfile)
    │     ForceDirectories(serverresultfile)
    │
    ├─► Save to Local (if enabled)
    │     if (Tab_IsLogOnLocal)
    │         path = localresultfile + "\\" + FormatDateTime("YYYYMMDD")
    │         ForceDirectories(path)
    │         filename = path + "\\Result_" + strSFISPSN[0] + "_" 
    │                    + FormatDateTime("HHNNSS") + ".txt"
    │         DebugListBox->Lines->SaveToFile(filename)
    │
    └─► Save to Server (if enabled)
          if (Tab_IsLogOnServer)
              Similar to local path
              DebugListBox->Lines->SaveToFile(serverfilename)
```

### 6.2. SaveResumeLog() Function (Line 1500-1550)

```
SaveResumeLog(resumeresult)  // "PASS" or "FAIL"
    │
    ├─► Build CSV data from Logcsv vector
    │     for each item in Logcsv
    │         strtitle += item.Title + ","
    │         strdata += item.Data + ","
    │
    ├─► Build paths
    │     localresumefile = LocalPath + result + date + "Resume_Local_Log.csv"
    │     serverresumefile = ServerPath + result + date + "Resume_Server_Log.csv"
    │
    ├─► Save to Local CSV
    │     if (!FileExists(localresumefile))
    │         // Create file with header
    │         fprintf(pfile, "%s\n", strtitle)
    │     // Append data
    │     fprintf(pfile, "%s\n", strdata)
    │
    ├─► Save to Server CSV
    │     Similar to local
    │
    └─► Clear log vector
          Logcsv.clear()
```

### 6.3. Log File Structure

```
D:\Logs\
├─ PASS\
│  └─ 20250114\
│     ├─ Result_PSN0001_120530.txt
│     │   ├─ Panel_Lable: PANEL001
│     │   ├─ MO_Number: MO12345678
│     │   ├─ PSN_1: PSN0001...
│     │   ├─ ...
│     │   ├─ Test_Times: 0:0:45
│     │   └─ Test_Result: PASS
│     │
│     └─ Resume_Local_Log.csv
│         Panel_Lable,MO_Number,PSN_1,...,Test_Times,Test_Result
│         PANEL001,MO12345678,PSN0001,...,0:0:45,PASS
│
└─ FAIL\
   └─ 20250114\
      ├─ Result_PSN0010_130245.txt
      └─ Resume_Local_Log.csv
```

## 7. Complete Sequence Diagram

```
User    PLC         MainForm        SFIS        HANS_DLL      CCD
 │       │            │              │             │           │
 │       │──START1───►│              │             │           │
 │       │            │──NEEDPSN12──►│             │           │
 │       │            │◄─12 PSNs─────│             │           │
 │       │            │                            │           │
 │       │            │──Validate PSN              │           │
 │       │            │                            │           │
 │       │            │──LoadMarkFile──────────────►│           │
 │       │            │──ChangeText(PSN0-7)────────►│           │
 │       │            │──HS_Mark()─────────────────►│           │
 │       │            │  (Marking...)               │           │
 │       │            │◄─MarkEnd────────────────────│           │
 │       │            │──CloseMarkFile──────────────►│           │
 │       │            │                            │           │
 │       │            │──PRO1_DONE──►│             │           │
 │       │            │◄─PRO1_DONE───│             │           │
 │       │◄─CHECK1────│              │             │           │
 │       │            │──CHECK1──────────────────────────────►│
 │       │            │◄─CHE_OK/NG──────────────────────────────│
 │       │──CHE_OK───►│              │             │           │
 │       │            │              │             │           │
 │       │◄─START2────│              │             │           │
 │       │            │                            │           │
 │       │            │──LoadMarkFile2─────────────►│           │
 │       │            │──ChangeText(PSN8-11)───────►│           │
 │       │            │──HS_Mark()─────────────────►│           │
 │       │            │  (Marking...)               │           │
 │       │            │◄─MarkEnd────────────────────│           │
 │       │            │──CloseMarkFile──────────────►│           │
 │       │            │                            │           │
 │       │            │──PRO2_DONE──►│             │           │
 │       │            │◄─PRO2_DONE───│             │           │
 │       │            │                            │           │
 │       │            │──END PASS───►│             │           │
 │       │            │◄─ENDPASS─────│             │           │
 │       │            │                            │           │
 │       │            │──Save Logs                 │           │
 │       │◄─Display───│  (PASS)                    │           │
 │       │            │                            │           │
```

---

**Tổng kết**: Luồng hoạt động phức tạp với nhiều bước validation, retry mechanism, và synchronization giữa các thành phần (PLC, SFIS, HANS DLL, CCD). Hệ thống đảm bảo tính toàn vẹn dữ liệu và khả năng trace log đầy đủ.

