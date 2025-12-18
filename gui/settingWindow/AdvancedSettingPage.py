from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QSpinBox, QCheckBox, QFrame, QComboBox
)
from PySide6.QtWidgets import QPushButton, QFileDialog

class AdvancedSettingPage(QWidget):
    """Advanced settings page - including language selection."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):


        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Advanced Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Form for advanced options
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Language Dropdown
        self.language_select = QComboBox()
        self.language_select.addItem("English", "en")
        self.language_select.addItem("Vietnamese", "vi")
        form.addRow("Language:", self.language_select)

        # Path App with file dialog button
        path_app_layout = QHBoxLayout()
        self.path_app = QLineEdit()
        self.path_app.setReadOnly(True)
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self._choose_folder)
        path_app_layout.addWidget(self.path_app)
        path_app_layout.addWidget(self.select_folder_btn)
        form.addRow("Folder Application:", path_app_layout)

        layout.addLayout(form)
        layout.addStretch()

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Application Folder")
        if folder:
            self.path_app.setText(folder)

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "language": self.language_select.currentData(),
            "path_app": self.path_app.text().strip(),
        }

    def set_settings(self, settings):
        """Set settings from dictionary"""
        lang = settings.get("language", "en")
        idx = self.language_select.findData(lang)
        if idx >= 0:
            self.language_select.setCurrentIndex(idx)
        # Path App
        self.path_app.setText(settings.get("path_app", ""))

