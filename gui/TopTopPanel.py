from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt

class TopTopPanel(QWidget):
    modelChanged = Signal(str)
    def __init__(self):
        super().__init__()
        # Khởi tạo presenter (lazy import để tránh circular import)
        from presenter.toptop_presenter import TopTopPresenter
        self.presenter = TopTopPresenter()
        self._connectSignals()
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # Left: Title label
        title = QLabel("Project:")
        title.setStyleSheet("""
                        font-size: 16px; 
                        font-weight: bold;
                        """)
        title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title.setFixedWidth(90)
        main_layout.addWidget(title, stretch=0)

        # Center: Combo box, centered via stretch
        self.model_combo = QComboBox()
        self.model_combo.setFixedWidth(300)  
        self.model_combo.setPlaceholderText("Loading projects...")
        self.model_combo.addItems(self.presenter.getProjectNames())
        main_layout.addWidget(self.model_combo, stretch=0)

        self.button_change = QPushButton("Change")
        self.button_change.clicked.connect(self._onChangeButtonClicked)
        main_layout.addWidget(self.button_change, stretch=0)
        main_layout.addStretch(2) 


        # Dữ liệu sẽ được load từ presenter qua signal

    def _connectSignals(self):
        """Kết nối signals từ presenter"""
        self.presenter.modelChanged.connect(self._onPresenterModelChanged)
        self.presenter.projectNamesLoaded.connect(self._onProjectNamesLoaded)

    def _onChangeButtonClicked(self):
        """Xử lý khi user click button Change"""
        selected_project = self.model_combo.currentText()
        if selected_project and selected_project != self.presenter.getCurrentModel():
            success = self.presenter.change_model(selected_project)
            if success:
                self.modelChanged.emit(selected_project)

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
            
            self.model_combo.blockSignals(False)
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