# Project Management Architecture

## Tổng quan

Hệ thống quản lý project đã được tái cấu trúc để tuân thủ nguyên tắc **Single Responsibility Principle** và **Separation of Concerns**.

## Kiến trúc mới

### 1. **ProjectPresenter** (`presenter/project_presenter.py`)
**Chức năng chính:** Quản lý CRUD operations cho project data

**Responsibilities:**
- ✅ Load project data từ JSON file
- ✅ Update project information
- ✅ Delete project
- ✅ Add new project
- ✅ Validate project data
- ✅ Quản lý ProjectWorker thread

**Signals:**
- `projectDataLoaded(list)` - Dữ liệu đã load thành công
- `projectUpdated(str)` - Project đã được update
- `projectDeleted(str)` - Project đã được xóa
- `projectAdded(str)` - Project mới đã được thêm
- `logMessage(str, str)` - Log messages

**Public Methods:**
```python
loadProjectData()              # Load data asynchronously
loadProjectDataImmediate()     # Load data immediately
getProjectData()               # Get all project data
getProjectNames()              # Get list of project names
getProjectInfo(project_name)   # Get specific project info
updateProject(project_data)    # Update project
deleteProject(project_name)    # Delete project
addProject(project_data)       # Add new project
refreshProjectData()           # Refresh data from file
projectExists(project_name)    # Check if project exists
cleanup()                      # Clean up resources
```

---

### 2. **TopTopPresenter** (`presenter/toptop_presenter.py`)
**Chức năng chính:** Quản lý model/project selection và settings

**Responsibilities:**
- ✅ Quản lý current project selection
- ✅ Lưu project settings vào settings.json
- ✅ Thông báo khi project thay đổi
- ✅ Khởi tạo model.json từ default
- ✅ Request application restart

**Signals:**
- `modelChanged(str)` - Current model đã thay đổi
- `modelDataLoaded(list)` - Dữ liệu model đã load
- `projectDataLoaded(list)` - Alias cho modelDataLoaded
- `projectNamesLoaded(list)` - Danh sách project names

**Key Methods:**
```python
change_model(project_name)     # Switch to different project
getCurrentModel()              # Get current selected project
getProjectInfo(project_name)   # Get project details
getProjectNames()              # Get all project names
getModelData()                 # Get all model data
refreshModelData()             # Refresh data
requestRestart()               # Restart application
```

**Note:** Update/Delete operations đã được chuyển sang ProjectPresenter

---

### 3. **MainPresenter** (`presenter/main_presenter.py`)
**Chức năng chính:** Điều phối giữa các presenter và view

**Project-related Methods:**
```python
onProjectClicked()             # Open project table dialog
onProjectSelected(name)        # Handle project selection
onProjectEdit(data)            # Handle project edit
onProjectDelete(name)          # Handle project delete
```

**Signal Connections:**
```python
# ProjectPresenter signals
project_presenter.logMessage → forwardLog
project_presenter.projectDataLoaded → onProjectDataLoadedFromPresenter
project_presenter.projectUpdated → onProjectUpdatedFromPresenter
project_presenter.projectDeleted → onProjectDeletedFromPresenter
```

---

## Data Flow

### 1. **Load Project Data**
```
MainPresenter.onProjectClicked()
    ↓
ProjectPresenter.loadProjectDataImmediate()
    ↓
ProjectPresenter.onProjectDataLoaded()
    ↓
Signal: projectDataLoaded.emit(data)
    ↓
ProjectTable.set_data(data)
    ↓
Display in table
```

### 2. **Update Project**
```
User clicks "Fix" button
    ↓
ProjectTable.on_fix_clicked()
    ↓
ProjectEditDialog opens
    ↓
User saves changes
    ↓
Signal: project_edit.emit(updated_data)
    ↓
MainPresenter.onProjectEdit(data)
    ↓
ProjectPresenter.updateProject(data)
    ↓
ProjectWorker.updateProject(data)
    ↓
Update JSON file
    ↓
Signal: projectUpdated.emit(project_name)
    ↓
Refresh TopTopPresenter if needed
    ↓
Refresh ProjectTable
```

### 3. **Delete Project**
```
User clicks "Delete" button
    ↓
Confirmation dialog
    ↓
ProjectTable.on_delete_clicked()
    ↓
Signal: project_delete.emit(project_name)
    ↓
MainPresenter.onProjectDelete(name)
    ↓
Check if current project (prevent deletion)
    ↓
ProjectPresenter.deleteProject(name)
    ↓
ProjectWorker.deleteProject(name)
    ↓
Update JSON file
    ↓
Signal: projectDeleted.emit(project_name)
    ↓
Refresh TopTopPresenter
    ↓
Refresh ProjectTable
```

### 4. **Select Project**
```
User clicks "Select" button
    ↓
ProjectTable.on_select_clicked()
    ↓
Signal: project_selected.emit(project_name)
    ↓
MainPresenter.onProjectSelected(name)
    ↓
TopTopPresenter.change_model(name)
    ↓
Update settings.json
    ↓
Signal: modelChanged.emit(project_name)
    ↓
Update UI
```

---

## Separation of Concerns

| Presenter | Responsibility | Data Source |
|-----------|---------------|-------------|
| **ProjectPresenter** | CRUD operations on project data | model.json (via ProjectWorker) |
| **TopTopPresenter** | Current project selection & settings | settings.json + model.json |
| **MainPresenter** | Coordinate between presenters & views | All presenters |

---

## Benefits of New Architecture

### ✅ **Single Responsibility**
- Mỗi presenter có một trách nhiệm rõ ràng
- ProjectPresenter: Quản lý data
- TopTopPresenter: Quản lý selection
- MainPresenter: Điều phối

### ✅ **Maintainability**
- Code dễ đọc và maintain hơn
- Dễ dàng tìm bug
- Dễ dàng thêm features mới

### ✅ **Testability**
- Có thể test từng presenter độc lập
- Mock dependencies dễ dàng

### ✅ **Reusability**
- ProjectPresenter có thể được sử dụng ở nhiều nơi
- Không phụ thuộc vào TopTopPresenter

### ✅ **Thread Safety**
- ProjectWorker chạy trong QThread riêng
- Không block UI thread

---

## Files Modified/Created

### Created:
- ✅ `presenter/project_presenter.py` - New presenter for project management
- ✅ `gui/projectWindow/projectEditDialog.py` - Edit dialog
- ✅ `docs/PROJECT_MANAGEMENT_ARCHITECTURE.md` - This file

### Modified:
- ✅ `presenter/main_presenter.py` - Added ProjectPresenter integration
- ✅ `presenter/toptop_presenter.py` - Removed update/delete methods
- ✅ `gui/projectWindow/projectTable.py` - Added Fix/Delete actions
- ✅ `gui/projectWindow/__init__.py` - Export new dialog
- ✅ `workers/project_worker.py` - Added update/delete methods

---

## Usage Example

```python
# In MainPresenter
self.project_presenter = ProjectPresenter()

# Connect signals
self.project_presenter.logMessage.connect(self.forwardLog)
self.project_presenter.projectUpdated.connect(self.onProjectUpdated)

# Load data
self.project_presenter.loadProjectDataImmediate()

# Get data
projects = self.project_presenter.getProjectData()

# Update project
success = self.project_presenter.updateProject(project_data)

# Delete project
success = self.project_presenter.deleteProject("ProjectName")

# Check if exists
exists = self.project_presenter.projectExists("ProjectName")
```

---

## Future Enhancements

### Possible improvements:
1. **Add Project Dialog** - Dialog để thêm project mới
2. **Duplicate Project** - Clone existing project
3. **Import/Export** - Import/export project data
4. **Search/Filter** - Tìm kiếm và filter projects
5. **Validation** - Validate project data trước khi save
6. **Undo/Redo** - Undo/redo cho edit operations
7. **Project Templates** - Templates cho các loại project khác nhau

---

## Testing Checklist

- [ ] Load project data successfully
- [ ] Display projects in table
- [ ] Select project and switch
- [ ] Edit project information
- [ ] Delete project (not current)
- [ ] Prevent deleting current project
- [ ] Refresh data after operations
- [ ] Handle errors gracefully
- [ ] Thread safety
- [ ] UI responsiveness

---

## Notes

- ProjectPresenter và TopTopPresenter đều sử dụng cùng một ProjectWorker instance riêng
- MainPresenter điều phối giữa hai presenters này
- Khi update/delete project, cần refresh cả ProjectPresenter và TopTopPresenter
- Không thể xóa project đang active

