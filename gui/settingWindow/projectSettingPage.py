from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QCheckBox, QComboBox, QDoubleSpinBox
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
        title = QLabel("Project Settings")
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
        self.panel_num = QLineEdit()
        self.delay_step = QDoubleSpinBox()
        self.delay_step.setRange(0.0, 10.0)
        self.delay_step.setDecimals(1)
        self.delay_step.setSingleStep(0.1)
        form.addRow("Current Project:", self.current_project)
        form.addRow("PSN PRE:", self.psn_pre)
        form.addRow("SFIS Format:", self.sfis_format)
        form.addRow("LM Mode:", self.lm_mode)
        form.addRow("Script:", self.script)
        form.addRow("Panel Num:", self.panel_num)
        form.addRow("Delay Step:", self.delay_step)
        layout.addLayout(form)
        layout.addStretch()

    def get_settings(self):
        return {
            "current_project": self.current_project.text().strip(),
            "psn_pre": self.psn_pre.text().strip(),
            "script": int(self.script.text().strip()) if self.script.text().strip().isdigit() else None,
            "panel_num": int(self.panel_num.text().strip()) if self.panel_num.text().strip().isdigit() else None,       
            "sfis_format": int(self.sfis_format.currentText()) if self.sfis_format.currentText().isdigit() else None,
            "lm_mode": int(self.lm_mode.currentText()) if self.lm_mode.currentText().isdigit() else None,
            "delay_step": self.delay_step.value(),
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
        self.sfis_format.setCurrentText((_to_text(settings.get("sfis_format", ""))))
        self.lm_mode.setCurrentText((_to_text(settings.get("lm_mode", ""))))
        self.script.setText((_to_text(settings.get("script", ""))))
        self.panel_num.setText((_to_text(settings.get("panel_num", ""))))
        self.delay_step.setValue(float(settings.get("delay_step", "0.1")))
