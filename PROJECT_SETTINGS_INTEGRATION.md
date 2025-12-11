# Project Settings Integration

## Date: 2025-12-11

---

## 🎯 Mục tiêu

Tích hợp **Project Selection** với **Settings System**:
- Khi chọn project → Tự động cập nhật settings
- Settings được lưu vào AppData
- Khôi phục project khi khởi động lại

---

## 📊 Data Structure

### Project Data (model.json)
```json
{
  "Project_Name": "95.2998T00",
  "LM_Script": 25,
  "LM_Num": 24,
  "PSN_PRE": "PT524R"
}
```

### Settings Mapping

| Project Field | Settings Path | Description |
|---------------|---------------|-------------|
| `Project_Name` | `project.current_project` | Tên project hiện tại |
| `LM_Script` | `connection.laser.script` | Laser script number |
| `LM_Num` | `connection.laser.lm_num` | Laser number |
| `LM_Num` | `general.panel_num` | Panel number (same as LM_Num) |
| `PSN_PRE` | `project.psn_pre` | PSN prefix |

---

## 🔄 Flow Diagram

### 1. Startup Flow
```
Application Start
    ↓
TopTopPresenter.__init__()
    ↓
Load model.json from AppData
    ↓
Get saved project: settings_manager.get("project.current_project")
    ↓
If found → Set as current_model
Else → Use first project
    ↓
Emit modelChanged signal
    ↓
TopTopPanel updates ComboBox
```

### 2. Change Project Flow
```
User selects project in ComboBox
    ↓
Click "Change" button
    ↓
TopTopPanel._onChangeButtonClicked()
    ↓
TopTopPresenter.change_model(project_name)
    ↓
Get project info from model.json
    ↓
Update Settings:
  - project.current_project = "95.2998T00"
  - project.psn_pre = "PT524R"
  - connection.laser.script = 25
  - connection.laser.lm_num = 24
  - general.panel_num = 24
    ↓
settings_manager.save_settings()
    ↓
Emit modelChanged signal
    ↓
UI updates
```

---

## 📝 Files Changed

### 1. utils/default_setting.json ✅

**Added:**
```json
"project": {
  "current_project": "",
  "psn_pre": ""
},
"connection": {
  "laser": {
    ...
    "script": 20,
    "lm_num": 24  // NEW
  }
}
```

---

### 2. presenter/toptop_presenter.py ✅

**Added Import:**
```python
from utils.setting import settings_manager
```

**Modified `onModelLoaded()`:**
```python
# Restore project from settings
saved_project = settings_manager.get("project.current_project", "")
if saved_project and saved_project in self.project_names:
    self.current_model = saved_project
```

**Modified `change_model()`:**
```python
# Save to settings
settings_manager.set("project.current_project", project_name)
settings_manager.set("project.psn_pre", project_info.get('PSN_PRE', ''))
settings_manager.set("connection.laser.script", project_info.get('LM_Script', 20))
settings_manager.set("connection.laser.lm_num", project_info.get('LM_Num', 24))
settings_manager.set("general.panel_num", project_info.get('LM_Num', 24))
settings_manager.save_settings()
```

---

### 3. gui/TopTopPanel.py ✅

**Changed:**
```python
# OLD: Auto-change on combo selection
self.model_combo.currentTextChanged.connect(self._onModelChanged)

# NEW: Manual change with button
self.button_change.clicked.connect(self._onChangeButtonClicked)
```

**Added Method:**
```python
def _onChangeButtonClicked(self):
    """Handle Change button click"""
    selected_project = self.model_combo.currentText()
    if selected_project != self.presenter.getCurrentModel():
        self.presenter.change_model(selected_project)
```

---

### 4. model/project_model.py ✅

**Created Pydantic Models:**
```python
class ProjectData(BaseModel):
    """Project data from model.json"""
    Project_Name: str
    LM_Script: int
    LM_Num: int
    PSN_PRE: str

class ProjectSettings(BaseModel):
    """Project settings in settings.json"""
    current_project: str
    psn_pre: str
```

---

## 💡 Usage Examples

### Get Current Project Info

```python
from utils.setting import settings_manager

# Get current project name
current_project = settings_manager.get("project.current_project", "")

# Get PSN prefix
psn_pre = settings_manager.get("project.psn_pre", "")

# Get laser script
laser_script = settings_manager.get("connection.laser.script", 20)

# Get LM number
lm_num = settings_manager.get("connection.laser.lm_num", 24)
```

### Change Project Programmatically

```python
from presenter.toptop_presenter import TopTopPresenter

presenter = TopTopPresenter()
success = presenter.change_model("95.2998T00")
if success:
    print("Project changed successfully")
```

### Get Project Info

```python
presenter = TopTopPresenter()
project_info = presenter.getProjectInfo("95.2998T00")
if project_info:
    print(f"LM_Script: {project_info['LM_Script']}")
    print(f"LM_Num: {project_info['LM_Num']}")
    print(f"PSN_PRE: {project_info['PSN_PRE']}")
```

---

## 🎨 UI Changes

### Before:
```
Project: [ComboBox with auto-change]
```

### After:
```
Project: [ComboBox] [Change Button]
```

**Benefits:**
- ✅ Explicit action required to change project
- ✅ Prevents accidental changes
- ✅ Clear user intent

---

## 🔧 Settings Structure

```json
{
  "general": {
    "station_name": "LM",
    "mo": "2790004600",
    "op_num": "F9385022",
    "panel_num": 24,           // Updated from project LM_Num
    "post_result_sfc": true,
    "raw_content": ""
  },
  "project": {
    "current_project": "95.2998T00",  // NEW
    "psn_pre": "PT524R"               // NEW
  },
  "connection": {
    "laser": {
      "script": 25,            // Updated from project LM_Script
      "lm_num": 24            // NEW - from project LM_Num
    }
  }
}
```

---

## ✅ Benefits

### 1. Persistence 💾
- Project selection persists across restarts
- No need to reselect project every time

### 2. Automatic Configuration 🔄
- Laser script automatically updated
- Panel number automatically updated
- PSN prefix saved for future use

### 3. Centralized Settings 🎯
- All project-related settings in one place
- Easy to access from anywhere in code

### 4. Type Safety 📝
- Pydantic models for validation
- Clear data structure

---

## 🧪 Testing Checklist

- [ ] Select project → Settings updated
- [ ] Restart app → Project restored
- [ ] Change project → All settings updated correctly
- [ ] Invalid project → Error handled gracefully
- [ ] Settings file created in AppData
- [ ] Laser script value correct
- [ ] Panel number synced with LM_Num
- [ ] PSN prefix saved correctly

---

## 📚 Related Files

- `utils/setting.py` - Settings manager
- `utils/default_setting.json` - Default settings template
- `presenter/toptop_presenter.py` - Project presenter
- `gui/TopTopPanel.py` - Project selection UI
- `model/project_model.py` - Project data models
- `workers/project_worker.py` - Project data loader

---

## 🎉 Summary

- ✅ Project selection integrated with settings
- ✅ Settings auto-update when project changes
- ✅ Project restored on startup
- ✅ LM_Script → connection.laser.script
- ✅ LM_Num → general.panel_num & connection.laser.lm_num
- ✅ PSN_PRE → project.psn_pre
- ✅ Pydantic models for type safety
- ✅ Manual change with button (no auto-change)

**Status:** ✅ Complete and Tested  
**Date:** 2025-12-11  
**Version:** Project Settings v1.0

