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
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.lbl_sprite.setFont(font)
        self.lbl_sprite.setStyleSheet("""
            background-color: aqua;
            border: 2px solid black;
            border-radius: 10px;
            padding: 0px;
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
            bg_color = "aqua"
        elif status == self.MARKING:
            bg_color = "yellow"
        elif status == self.COMPLETED:
            bg_color = "lightgreen"
        elif status == self.FAILED:
            bg_color = "orange"
        elif status == self.ERROR:
            bg_color = "red"
        else:
            bg_color = "aqua"
        
        self.lbl_sprite.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid black;
            border-radius: 10px;
            padding: 0px;
        """)

