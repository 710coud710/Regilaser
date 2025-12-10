"""
Bottom Status Bar - Hiển thị thông tin test và thời gian
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
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
            
        # Test Time label
        self.btn_sfis = QPushButton("SFIS OFF")
        self.btn_sfis.setCheckable(True)
        self.btn_sfis.setChecked(False)
        self.btn_sfis.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        # self.btn_sfis.toggled.connect(self._onSfisButtonToggled)
        layout.addWidget(self.btn_sfis)
        
        # PLC status label
        self.btn_plc = QPushButton("PLC OFF")
        self.btn_plc.setCheckable(True)
        self.btn_plc.setChecked(False)
        self.btn_plc.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        # self.btn_plc.toggled.connect(self._onPlcButtonToggled)
        layout.addWidget(self.btn_plc)

        # Laser status label
        self.btn_laser = QPushButton("LASER OFF")
        self.btn_laser.setCheckable(True)
        self.btn_laser.setChecked(False)
        self.btn_laser.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        # self.btn_laser.toggled.connect(self._onLaserButtonToggled)
        layout.addWidget(self.btn_laser)
        
        # Additional info labels (từ ảnh)
        info_labels = ["Version: V1.1.0 Free", 
                      "OP_Num:OP12345", "PC Name:PC12345"]
        
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

