"""
Bottom Status Bar - Hiển thị thông tin test và thời gian
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class BottomStatusBar(QWidget):
    """Status bar phía dưới"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Error message label
        self.lbl_error = QLabel("CPSN00 Calibration PCB_PSN Fail")
        self.lbl_error.setStyleSheet("""
            background-color: #FFFFE0;
            padding: 3px;
            border: 1px solid #ccc;
        """)
        layout.addWidget(self.lbl_error, stretch=1)
        
        # Test Time label
        self.lbl_test_time = QLabel("Test Time")
        self.lbl_test_time.setAlignment(Qt.AlignCenter)
        self.lbl_test_time.setStyleSheet("""
            background-color: cyan;
            padding: 3px;
            font-weight: bold;
            border: 1px solid black;
        """)
        self.lbl_test_time.setFixedWidth(120)
        layout.addWidget(self.lbl_test_time)
        
        # Time value
        self.lbl_time_value = QLabel("0")
        self.lbl_time_value.setAlignment(Qt.AlignCenter)
        self.lbl_time_value.setStyleSheet("""
            background-color: cyan;
            padding: 3px;
            font-weight: bold;
            border: 1px solid black;
        """)
        self.lbl_time_value.setFixedWidth(60)
        layout.addWidget(self.lbl_time_value)
        
        # Additional info labels (từ ảnh)
        info_labels = ["CPEI", "TE", "Pass:", "Fail:", "Version", "Hook Off", 
                      "OP_Num:F9583701", "PC Name:", "DESKTOP-HQ87"]
        
        for text in info_labels:
            lbl = QLabel(text)
            lbl.setStyleSheet("padding: 2px; border: 1px solid #ccc;")
            if text in ["CPEI", "TE", "Pass:", "Fail:"]:
                lbl.setFixedWidth(60)
            elif ":" in text:
                lbl.setFixedWidth(140)
            else:
                lbl.setFixedWidth(80)
            layout.addWidget(lbl)
        
        self.setMaximumHeight(35)
        self.setStyleSheet("background-color: #f0f0f0;")
    
    def set_error_message(self, message):
        """Set error message"""
        self.lbl_error.setText(message)
    
    def set_test_time(self, time_value):
        """Set test time value"""
        self.lbl_time_value.setText(str(time_value))
    
    def clear_error(self):
        """Clear error message"""
        self.lbl_error.setText("")

