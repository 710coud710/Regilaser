"""
Right Panel - Chứa SFIS Action display với debug options
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QCheckBox,
                             QGroupBox, QLabel)
from PySide6.QtCore import Qt


class RightPanel(QWidget):
    """Panel bên phải hiển thị SFIS Action"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # SFIS Action header
        header_group = QGroupBox()
        header_layout = QVBoxLayout()
        
        lbl_header = QLabel("_SFIS_Action(642.642)")
        lbl_header.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(lbl_header)
        
        self.txt_action = QTextEdit("dasdasd")
        self.txt_action.setMaximumHeight(50)
        header_layout.addWidget(self.txt_action)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Debug options
        options_group = QGroupBox()
        options_layout = QVBoxLayout()
        
        self.chk_debug = QCheckBox("Debug")
        options_layout.addWidget(self.chk_debug)
        
        self.chk_emp = QCheckBox("EMP")
        options_layout.addWidget(self.chk_emp)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        self.setFixedWidth(200)
    
    def set_action_text(self, text):
        """Set SFIS action text"""
        self.txt_action.setText(text)
    
    def get_action_text(self):
        """Get SFIS action text"""
        return self.txt_action.toPlainText()
    
    def is_debug_checked(self):
        return self.chk_debug.isChecked()
    
    def is_emp_checked(self):
        return self.chk_emp.isChecked()

