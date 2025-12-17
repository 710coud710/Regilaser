"""
Center Panel - Chứa Sprite label, LM button, COM ports
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QGroupBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class CenterPanel(QWidget):
    """Panel trung tâm"""
    STANDBY = "STANDBY"
    MARKING = "MARKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Standby Status (nền vàng)
        self.lbl_sprite = QLabel(self.STANDBY)
        self.lbl_sprite.setAlignment(Qt.AlignCenter)
        self.lbl_sprite.setStyleSheet("""
            background-color: #5493ff;
            border: 1px solid gray;
            border-radius: 10px;
            padding: 0px;
            color: #ffffff;
            font-size: 28pt;
            font-weight: bold;
        """)
        self.lbl_sprite.setMinimumHeight(70)
        self.lbl_sprite.setMinimumWidth(420)

        # self.lbl_sprite.setMaximumHeight(90)
        # self.lbl_sprite.setMaximumWidth(600)
        layout.addWidget(self.lbl_sprite, stretch=1)

        # Không cần stretch hoặc fixed width panel nữa
    
    def get_sprite_label(self):
        return self.lbl_sprite
    
    def get_lm_button(self):
        return self.btn_lm
    
    def get_selected_com4(self):
        return self.combo_com4.currentText()
    
    def get_selected_com2(self):
        return self.combo_com2.currentText()
    
    def setStatus(self, status):
        """Set status and update UI accordingly"""
        self.lbl_sprite.setText(status)
        
        # Update background color based on status
        if status == self.STANDBY:
            bg_color = "#5493ff"
            text_color = "#ffffff"
        elif status == self.MARKING:
            bg_color = "#ffd600"
            text_color = "#000000"
        elif status == self.COMPLETED:
            bg_color = "#00e676"
            text_color = "#ffffff"
        elif status == self.FAILED:
            bg_color = "#ff9800"
            text_color = "#ffffff"
        elif status == self.ERROR:
            bg_color = "#f44336"
            text_color = "#ffffff"
        else:
            bg_color = "#6f6ffc"
            text_color = "#ffffff"
        
        self.lbl_sprite.setStyleSheet(f"""
            background-color: {bg_color};
            border: 1px solid gray;
            border-radius: 10px;
            padding: 0px;
            color: {text_color};
            font-size: 28pt;
            font-weight: bold;
        """)

