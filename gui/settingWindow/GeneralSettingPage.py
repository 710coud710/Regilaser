from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QCheckBox
)
from PySide6.QtWidgets import QFrame

class GeneralSettingPage(QWidget):
    """General Configuration settings page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("General Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        # General config fields
        self.station_name = QLineEdit()
        self.mo = QLineEdit()
        self.op_num = QLineEdit()
        self.panel_num = QLineEdit()
        self.post_result_sfc = QCheckBox("Enable POST_RESULT_SFC")
        
        form.addRow("Station Name:", self.station_name)
        form.addRow("MO:", self.mo)
        form.addRow("OP Number:", self.op_num)
        form.addRow("Panel Number:", self.panel_num)
        form.addRow("", self.post_result_sfc)
        
        layout.addLayout(form)
        self.add_line(layout)
        # Form  BOMver
        form2 = QFormLayout()
        form2.setLabelAlignment(Qt.AlignRight)
        self.pcb_product_name = QLineEdit()
        self.pcb_number = QLineEdit()
        form2.addRow("PCB Product Name:", self.pcb_product_name)
        form2.addRow("PCB Number:", self.pcb_number)
        layout.addLayout(form2)
        layout.addStretch()

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "station_name": self.station_name.text().strip(),
            "mo": self.mo.text().strip(),
            "op_num": self.op_num.text().strip(),
            "panel_num": self.panel_num.text().strip(),
            "post_result_sfc": self.post_result_sfc.isChecked(),
            "pcb_product_name": self.pcb_product_name.text().strip(),
            "pcb_number": self.pcb_number.text().strip(),
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
        self.station_name.setText(_to_text(settings.get("station_name", "")))
        self.mo.setText(_to_text(settings.get("mo", "")))
        self.op_num.setText(_to_text(settings.get("op_num", "")))
        self.panel_num.setText(_to_text(settings.get("panel_num", "")))
        self.post_result_sfc.setChecked(settings.get("post_result_sfc", False))
        self.pcb_product_name.setText(_to_text(settings.get("pcb_product_name", "")))
        self.pcb_number.setText(_to_text(settings.get("pcb_number", "")))