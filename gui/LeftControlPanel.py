"""
Left Control Panel - Chứa ALL PARTS checkbox, Start button, SFIS/LCD controls
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QPushButton,
                             QGroupBox, QLabel, QLineEdit)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont


class LeftControlPanel(QWidget):
    """Panel điều khiển bên trái"""
    
    # Signals
    startClicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.elapsed_seconds = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._updateTimer)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #cadcaf;
                border: 1px solid black;
                border-radius: 5px;
                padding: 10px;
                font-size: 16pt;
            }         
            QPushButton:hover {
                background-color: #cadcfc;
                color: black;
            }
            QPushButton:pressed {
                background-color: #00236b;
                color: white;
            }

            QLabel {
                background-color: white;
                border: 1px solid gray;
                border-radius: 10px;
                font-size: 19pt;
                font-weight: bold;
                color: #101033;
            }
        """)
 
        # Start button (to, in nghiêng)
        self.btn_start = QPushButton("Start")
        font = QFont()
        font.setPointSize(24)
        font.setItalic(True)
        font.setBold(True)
        self.btn_start.setFont(font)
        self.btn_start.setMinimumHeight(80)
        self.btn_start.clicked.connect(self.startClicked.emit)
        layout.addWidget(self.btn_start)
        
        #INTERVAL
        self.lbl_interval = QLabel("Time Test: 11s")
        self.lbl_interval.setAlignment(Qt.AlignCenter)
        self.lbl_interval.setMaximumHeight(40)
        layout.addWidget(self.lbl_interval)        
        
        layout.addStretch()
        
        self.setFixedWidth(200)

    def getStartButton(self):
        return self.btn_start
    
    def getIntervalLabel(self):
        return self.lbl_interval
    
    def startTimer(self):
        """Start the timer"""
        self.elapsed_seconds = 0
        self.lbl_interval.setText("Time Test: 0s")
        self.timer.start(1000)  # Update every second
    
    def stopTimer(self):
        """Stop the timer"""
        self.timer.stop()
    
    def resetTimer(self):
        """Reset the timer"""
        self.timer.stop()
        self.elapsed_seconds = 0
        self.lbl_interval.setText("Time Test: 0s")
    
    def getElapsedTime(self):
        """Get elapsed time in seconds"""
        return self.elapsed_seconds
    
    def _updateTimer(self):
        """Update timer display"""
        self.elapsed_seconds += 1
        self.lbl_interval.setText(f"Time Test: {self.elapsed_seconds}s")

