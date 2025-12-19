from multiprocessing import set_forkserver_preload
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from utils.AppPathService import getAppDirectory
import os

class TopTopPanel(QWidget):
    modelChanged = Signal(str)
    
    def __init__(self):
        super().__init__()
        # Khởi tạo presenter (lazy import để tránh circular import)
        from presenter.toptop_presenter import TopTopPresenter
        self.presenter = TopTopPresenter()
        self._connectSignals()
        self._init_ui()
        
        # Track initial project
        self.initial_project = self.presenter.getCurrentModel()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        main_layout.addStretch(1)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(10)
        self.setStyleSheet("""
            TopTopPanel QLabel {
                font-size: 24pt; 
                font-weight: bold;
                color: #041d36;
            }    
            TopTopPanel QComboBox {
                font-size: 14pt;
                font-weight: bold;
                color: #101033;
            }
            QComboBox:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox:enabled:hover {
                background-color: lightblue;
            }
            QComboBox:editable {
                font-size: 18pt;
                font-weight: bold;
                color: #101033;
            }
            QComboBox:editable:hover {
                background-color: lightblue;
            }   
            TopTopPanel QPushButton {
                font-size: 14pt;
                font-weight: bold;
                color: #101033;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:enabled {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            QPushButton:enabled:hover {
                background-color: #45a049;
            }
        """)
        # Title label
        title = QLabel("PROJECT :")
        center_layout.addWidget(title)
        # Combo box
        self.model_combo = QComboBox()
        self.model_combo.setPlaceholderText("Loading projects...")
        self.model_combo.addItems(self.presenter.getProjectNames())
        self.model_combo.currentTextChanged.connect(self._onComboSelectionChanged)
        center_layout.addWidget(self.model_combo)
        # Button
        self.button_change = QPushButton("Change")
        self.button_change.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/change.svg")))
        self.button_change.setEnabled(False)  # Disabled by default
        self.button_change.clicked.connect(self._onChangeButtonClicked)
        center_layout.addWidget(self.button_change)
        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)

    def _connectSignals(self):
        """Kết nối signals từ presenter"""
        self.presenter.modelChanged.connect(self._onPresenterModelChanged)
        self.presenter.projectNamesLoaded.connect(self._onProjectNamesLoaded)

    def _onComboSelectionChanged(self, text):
        """Xử lý khi user thay đổi selection trong combo box"""
        # Enable button chỉ khi selection khác với current project
        current_project = self.presenter.getCurrentModel()
        self.button_change.setEnabled(text != current_project and text != "")
    
    def _onChangeButtonClicked(self):
        """Xử lý khi user click button Change"""
        selected_project = self.model_combo.currentText()
        current_project = self.presenter.getCurrentModel()
        
        if not selected_project or selected_project == current_project:
            return
        
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "Confirm Project Change",
            f"Change project from '{current_project}' to '{selected_project}'?\n\n"
            f"The application will restart to apply changes.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Change model and save to settings
            success = self.presenter.change_model(selected_project)
            if success:
                self.modelChanged.emit(selected_project)
                # Restart application
                self._restartApplication()
    
    def _restartApplication(self):
        """Restart the application using restart service"""
        # Delegate to presenter
        self.presenter.requestRestart()

    def _onPresenterModelChanged(self, model):
        """Xử lý khi presenter thông báo model đã thay đổi"""
        self.model = model
        # Cập nhật combo box nếu cần
        current_text = self.model_combo.currentText()
        if current_text != model:
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.blockSignals(True)  # Tránh loop
                self.model_combo.setCurrentIndex(index)
                self.model_combo.blockSignals(False)

    def _onProjectNamesLoaded(self, project_names):
        """Xử lý khi danh sách project names được load"""
        try:
            # Clear combo box
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            
            # Add project names
            for project_name in project_names:
                self.model_combo.addItem(project_name)
            
            # Set default selection
            current_model = self.presenter.getCurrentModel()
            if current_model:
                index = self.model_combo.findText(current_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                    self.initial_project = current_model
            
            self.model_combo.blockSignals(False)
            
            # Button starts disabled (no change yet)
            self.button_change.setEnabled(False)
            
            print(f"Loaded {len(project_names)} project names to combo box")
            
        except Exception as e:
            print(f"Error loading project names to combo box: {e}")

    def getCurrentModel(self):
        """Lấy model hiện tại"""
        return self.presenter.getCurrentModel()

    def getModelData(self):
        """Lấy dữ liệu model"""
        return self.presenter.getModelData()

    def getProjectNames(self):
        """Lấy danh sách project names"""
        return self.presenter.getProjectNames()

    def refreshModelData(self):
        """Refresh dữ liệu model"""
        self.presenter.refreshModelData()