"""
Top Control Panel - Chứa Reset, Keyboard, PSN input, MO
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal


class TopControlPanel(QWidget):
    """Panel điều khiển phía trên"""
    
    # Signals
    reset_clicked = Signal()
    keyboard_clicked = Signal()
    psn_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Reset button
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedWidth(80)
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
        layout.addWidget(self.btn_reset)
        
        # Keyboard button
        self.btn_keyboard = QPushButton("Keyboard")
        self.btn_keyboard.setFixedWidth(80)
        self.btn_keyboard.clicked.connect(self.keyboard_clicked.emit)
        layout.addWidget(self.btn_keyboard)
        
        # Mystery buttons (từ ảnh: ??PSN?? và ???????)
        self.btn_psn_label = QPushButton("??PSN??")
        self.btn_psn_label.setFixedWidth(80)
        layout.addWidget(self.btn_psn_label)
        
        self.btn_mystery = QPushButton("???????")
        self.btn_mystery.setFixedWidth(80)
        layout.addWidget(self.btn_mystery)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.setMaximumHeight(50)
    
    def get_reset_button(self):
        return self.btn_reset
    
    def get_keyboard_button(self):
        return self.btn_keyboard

