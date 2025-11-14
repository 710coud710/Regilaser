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
    all_parts_changed = Signal(bool)
    start_clicked = Signal()
    sfis_toggled = Signal(bool)
    lcd_toggled = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # ALL PARTS checkbox với input
        parts_group = QGroupBox()
        parts_layout = QVBoxLayout()
        
        self.chk_all_parts = QCheckBox("ALL PARTS.N:")
        self.chk_all_parts.setChecked(True)
        self.chk_all_parts.stateChanged.connect(
            lambda state: self.all_parts_changed.emit(state == Qt.Checked)
        )
        parts_layout.addWidget(self.chk_all_parts)
        
        self.input_parts = QLineEdit("wwwltsadsad")
        parts_layout.addWidget(self.input_parts)
        
        # MO label và input
        mo_label = QLabel("MO:")
        parts_layout.addWidget(mo_label)
        
        self.input_mo = QLineEdit()
        parts_layout.addWidget(self.input_mo)
        
        parts_group.setLayout(parts_layout)
        layout.addWidget(parts_group)
        
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
        
        # Mark result label
        label_mark = QLabel("Mark result")
        layout.addWidget(label_mark)
        
        # SFIS control
        sfis_group = QGroupBox()
        sfis_layout = QVBoxLayout()
        
        self.btn_sfis = QPushButton("SFIS OFF")
        self.btn_sfis.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.btn_sfis.setMinimumHeight(35)
        self.btn_sfis.clicked.connect(self._toggle_sfis)
        sfis_layout.addWidget(self.btn_sfis)
        
        sfis_group.setLayout(sfis_layout)
        layout.addWidget(sfis_group)
        
        # LCD control
        lcd_group = QGroupBox()
        lcd_layout = QVBoxLayout()
        
        self.btn_lcd = QPushButton("LCD OFF")
        self.btn_lcd.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.btn_lcd.setMinimumHeight(35)
        self.btn_lcd.clicked.connect(self._toggle_lcd)
        lcd_layout.addWidget(self.btn_lcd)
        
        lcd_group.setLayout(lcd_layout)
        layout.addWidget(lcd_group)
        
        layout.addStretch()
        
        self.setFixedWidth(200)
    
    def _toggle_sfis(self):
        """Toggle SFIS state"""
        is_on = self.btn_sfis.text() == "SFIS OFF"
        if is_on:
            self.btn_sfis.setText("SFIS ON")
            self.btn_sfis.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        else:
            self.btn_sfis.setText("SFIS OFF")
            self.btn_sfis.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.sfis_toggled.emit(is_on)
    
    def _toggle_lcd(self):
        """Toggle LCD state"""
        is_on = self.btn_lcd.text() == "LCD OFF"
        if is_on:
            self.btn_lcd.setText("LCD ON")
            self.btn_lcd.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        else:
            self.btn_lcd.setText("LCD OFF")
            self.btn_lcd.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.lcd_toggled.emit(is_on)
    
    def get_start_button(self):
        return self.btn_start
    
    def is_all_parts_checked(self):
        return self.chk_all_parts.isChecked()
    
    def get_parts_input(self):
        return self.input_parts.text()

