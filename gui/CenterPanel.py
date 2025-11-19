"""
Center Panel - Chứa Sprite label, LM button, COM ports
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QComboBox, QGroupBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class CenterPanel(QWidget):
    """Panel trung tâm"""
    
    # Signals
    lm_clicked = Signal()
    com4_changed = Signal(str)
    com2_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Sprite label (nền vàng)
        self.lbl_sprite = QLabel("Sprite")
        self.lbl_sprite.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.lbl_sprite.setFont(font)
        self.lbl_sprite.setStyleSheet("""
            background-color: yellow;
            border: 2px solid black;
            padding: 20px;
        """)
        self.lbl_sprite.setMinimumHeight(100)
        layout.addWidget(self.lbl_sprite)
        
        # LM button (nền vàng)
        self.btn_lm = QPushButton("LM")
        font_lm = QFont()
        font_lm.setPointSize(20)
        font_lm.setBold(True)
        self.btn_lm.setFont(font_lm)
        self.btn_lm.setStyleSheet("""
            background-color: yellow;
            border: 2px solid black;
            padding: 10px;
        """)
        self.btn_lm.setMinimumHeight(60)
        self.btn_lm.clicked.connect(self.lm_clicked.emit)
        layout.addWidget(self.btn_lm)
        
        # COM4 selection
        com4_group = QGroupBox()
        com4_layout = QVBoxLayout()
        
        lbl_com4 = QLabel("COM4")
        com4_layout.addWidget(lbl_com4)
        
        self.combo_com4 = QComboBox()
        self.combo_com4.addItems(["COM4", "COM1", "COM3", "COM5"])
        self.combo_com4.currentTextChanged.connect(self.com4_changed.emit)
        com4_layout.addWidget(self.combo_com4)
        
        com4_group.setLayout(com4_layout)
        layout.addWidget(com4_group)
        
        # COM2 selection
        com2_group = QGroupBox()
        com2_layout = QVBoxLayout()
        
        lbl_com2 = QLabel("COM2")
        com2_layout.addWidget(lbl_com2)
        
        self.combo_com2 = QComboBox()
        self.combo_com2.addItems(["COM2", "COM1", "COM3", "COM5"])
        self.combo_com2.currentTextChanged.connect(self.com2_changed.emit)
        com2_layout.addWidget(self.combo_com2)
        
        com2_group.setLayout(com2_layout)
        layout.addWidget(com2_group)
        
        layout.addStretch()
        
        self.setFixedWidth(180)
    
    def get_sprite_label(self):
        return self.lbl_sprite
    
    def get_lm_button(self):
        return self.btn_lm
    
    def get_selected_com4(self):
        return self.combo_com4.currentText()
    
    def get_selected_com2(self):
        return self.combo_com2.currentText()

