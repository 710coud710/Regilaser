"""
Left Control Panel - Chứa ALL PARTS checkbox, Start button, SFIS/LCD controls
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QPushButton,
                             QGroupBox, QLabel, QLineEdit)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class LeftControlPanel(QWidget):
    """Panel điều khiển bên trái"""
    
    # Signals
    start_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Start button (to, in nghiêng)
        self.btn_start = QPushButton("Start")
        font = QFont()
        font.setPointSize(24)
        font.setItalic(True)
        font.setBold(True)
        self.btn_start.setFont(font)
        self.btn_start.setMinimumHeight(80)
        self.btn_start.setStyleSheet("background-color: #f0f0f0;")
        self.btn_start.clicked.connect(self.start_clicked.emit)
        layout.addWidget(self.btn_start)
        
        #INTERVAL
        self.lbl_interval = QLabel("Time Test: 20s")
        self.lbl_interval.setAlignment(Qt.AlignCenter)
        self.lbl_interval.setStyleSheet("""
            background-color: cyan;
            padding: 5px;
            font-size: 16pt;
            font-weight: bold;
            border: 1px solid black;
        """)
        self.lbl_interval.setMaximumHeight(40)
        layout.addWidget(self.lbl_interval)        
        
        layout.addStretch()
        
        self.setFixedWidth(200)
    
    
    
    def getStartButton(self):
        return self.btn_start
    
    def getIntervalLabel(self):
        return self.lbl_interval

