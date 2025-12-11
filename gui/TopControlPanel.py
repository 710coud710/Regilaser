"""
Top Control Panel - Hiển thị trạng thái kết nối (chỉ hiển thị, không điều khiển)
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGroupBox, QLabel)
from PySide6.QtCore import Signal

class TopControlPanel(QWidget):
    """Panel hiển thị trạng thái phía trên"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
     
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # ===== SFIS Status Display =====
        sfis_group = QGroupBox("SFIS")
        sfis_layout = QHBoxLayout()
        sfis_layout.setContentsMargins(5, 5, 5, 5)
        sfis_layout.setSpacing(8)
        
        self.dot_sfis_status = QLabel()
        self.dot_sfis_status.setFixedSize(20, 20)
        self.dot_sfis_status.setStyleSheet("""
            background-color: red;
            border-radius: 10px;
            border: 1px solid #444;
        """)
        sfis_layout.addWidget(self.dot_sfis_status)
        
        self.lbl_sfis_status = QLabel("Disconnected")
        self.lbl_sfis_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        sfis_layout.addWidget(self.lbl_sfis_status)
        
        sfis_group.setLayout(sfis_layout)
        layout.addWidget(sfis_group)
        
        # ===== PLC Status Display =====
        plc_group = QGroupBox("PLC")
        plc_layout = QHBoxLayout()
        plc_layout.setContentsMargins(5, 5, 5, 5)
        plc_layout.setSpacing(8)
        
        self.dot_plc_status = QLabel()
        self.dot_plc_status.setFixedSize(20, 20)
        self.dot_plc_status.setStyleSheet("""
            background-color: red;
            border-radius: 10px;
            border: 1px solid #444;
        """)
        plc_layout.addWidget(self.dot_plc_status)
        
        self.lbl_plc_status = QLabel("Disconnected")
        self.lbl_plc_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        plc_layout.addWidget(self.lbl_plc_status)
        
        plc_group.setLayout(plc_layout)
        layout.addWidget(plc_group)
        
        # ===== Laser Status Display =====
        laser_group = QGroupBox("Laser Machine")
        laser_layout = QHBoxLayout()
        laser_layout.setContentsMargins(5, 5, 5, 5)
        laser_layout.setSpacing(8)
        
        self.dot_laser_status = QLabel()
        self.dot_laser_status.setFixedSize(20, 20)
        self.dot_laser_status.setStyleSheet("""
            background-color: red;
            border-radius: 10px;
            border: 1px solid #444;
        """)
        laser_layout.addWidget(self.dot_laser_status)
        
        self.lbl_laser_status = QLabel("Disconnected")
        self.lbl_laser_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        laser_layout.addWidget(self.lbl_laser_status)
        
        laser_group.setLayout(laser_layout)
        layout.addWidget(laser_group)
        
        # Stretch
        layout.addStretch()
        self.setMaximumHeight(80)

    # ===== Status Update Methods (chỉ hiển thị) =====
    def setSFISConnectionStatus(self, connected, message=""):
        """Cập nhật hiển thị trạng thái SFIS"""
        if connected:
            self.dot_sfis_status.setStyleSheet("""
                background-color: green;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_sfis_status.setText("Connected")
        else:
            self.dot_sfis_status.setStyleSheet("""
                background-color: red;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_sfis_status.setText("Disconnected")
    
    def setPLCConnectionStatus(self, connected, message=""):
        """Cập nhật hiển thị trạng thái PLC"""
        if connected:
            self.dot_plc_status.setStyleSheet("""
                background-color: green;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_plc_status.setText("Connected")
        else:
            self.dot_plc_status.setStyleSheet("""
                background-color: red;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_plc_status.setText("Disconnected")
    
    def setLaserConnectionStatus(self, connected, message=""):
        """Cập nhật hiển thị trạng thái Laser"""
        if connected:
            self.dot_laser_status.setStyleSheet("""
                background-color: green;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_laser_status.setText("Connected")
        else:
            self.dot_laser_status.setStyleSheet("""
                background-color: red;
                border-radius: 10px;
                border: 1px solid #444;
            """)
            self.lbl_laser_status.setText("Disconnected")
