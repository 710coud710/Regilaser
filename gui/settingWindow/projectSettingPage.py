from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QCheckBox, QComboBox
)
from PySide6.QtWidgets import QFrame

class ProjectSettingPage(QWidget):
    """Project Configuration settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Project Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        # General config fields
        self.current_project = QLineEdit()
        self.psn_pre = QLineEdit()
        self.sfis_format = QComboBox()
        self.sfis_format.addItems(["1", "2"])
        self.lm_mode = QComboBox()
        self.lm_mode.addItems(["1", "2"])
        self.script = QLineEdit()
        self.lm_num = QLineEdit()
        
        form.addRow("Current Project:", self.current_project)
        form.addRow("PSN PRE:", self.psn_pre)
        form.addRow("SFIS Format:", self.sfis_format)
        form.addRow("LM Mode:", self.lm_mode)
        form.addRow("Script:", self.script)
        form.addRow("LM Num:", self.lm_num)
        layout.addLayout(form)
        layout.addStretch()

    def get_settings(self):
        return {
            "psn_pre": self.psn_pre.text().strip(),
            "sfis_format": self.sfis_format.currentText(),
            "lm_mode": self.lm_mode.currentText(),
            "script": self.script.text().strip(),
            "lm_num": self.lm_num.text().strip(),
        }
    def add_line(self, parent_layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        parent_layout.addWidget(line)


    def set_settings(self, settings):
        """Set settings from dictionary"""
        def _to_text(value):
            """Ensure QLineEdit receives a string."""
            return "" if value is None else str(value)
        self.current_project.setText(_to_text(settings.get("current_project", "")))
        self.psn_pre.setText(_to_text(settings.get("psn_pre", "")))
        self.sfis_format.setCurrentText((_to_text(settings.get("SFIS_format", ""))))
        self.lm_mode.setCurrentText((_to_text(settings.get("LM_mode", ""))))
        self.script.setText((_to_text(settings.get("script", ""))))
        self.lm_num.setText((_to_text(settings.get("lm_num", ""))))