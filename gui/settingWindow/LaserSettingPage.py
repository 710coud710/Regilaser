from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, 
    QSpinBox, QTextEdit
)


class LaserSettingPage(QWidget):
    """Laser specific settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Laser Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        # Laser fields
        self.laser_mode = QComboBox()
        self.laser_mode.addItem("TCP", 1)
        self.laser_mode.addItem("RS232", 2)
        
        self.laser_script = QSpinBox()
        self.laser_script.setMaximum(999999)
        
        self.laser_timeout_ms = QSpinBox()
        self.laser_timeout_ms.setMaximum(120000)
        
        self.raw_content = QTextEdit()
        self.raw_content.setFixedHeight(100)
        
        form.addRow("Laser Mode:", self.laser_mode)
        form.addRow("Laser Script:", self.laser_script)
        form.addRow("Timeout (ms):", self.laser_timeout_ms)
        form.addRow("Raw Content:", self.raw_content)
        
        layout.addLayout(form)
        layout.addStretch()

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "laser_mode": self.laser_mode.currentData(),
            "laser_script": self.laser_script.value(),
            "laser_timeout_ms": self.laser_timeout_ms.value(),
            "raw_content": self.raw_content.toPlainText().strip(),
        }

    def set_settings(self, settings):
        """Set settings from dictionary"""
        mode_value = settings.get("laser_mode", 1)
        mode_index = self.laser_mode.findData(mode_value)
        if mode_index != -1:
            self.laser_mode.setCurrentIndex(mode_index)
        
        self.laser_script.setValue(settings.get("laser_script", 20))
        self.laser_timeout_ms.setValue(settings.get("laser_timeout_ms", 5000))
        self.raw_content.setPlainText(settings.get("raw_content", ""))
