from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QSpinBox, QCheckBox, QFrame, QComboBox
)

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
        layout.addLayout(form)
        layout.addStretch()

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "language": self.language_select.currentData(),
        }

    def set_settings(self, settings):
        """Set settings from dictionary"""
        lang = settings.get("language", "en")
        idx = self.language_select.findData(lang)
        if idx >= 0:
            self.language_select.setCurrentIndex(idx)

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "command_timeout_ms": self.command_timeout_ms.value(),
        }
    def set_settings(self, settings):
        """Set settings from dictionary"""
        self.command_timeout_ms.setValue(settings.get("command_timeout_ms", 10000))