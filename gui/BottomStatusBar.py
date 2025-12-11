"""
Bottom Status Bar - Hiển thị trạng thái và điều khiển kết nối SFC, PLC, Laser
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Qt, Signal

from utils.setting import settings_manager

class BottomStatusBar(QWidget):
    """Status bar phía dưới - Điều khiển kết nối SFC, PLC, Laser"""
    
    # Signals
    sfisChanged = Signal(str)
    sfisConnectRequested = Signal(bool, str)  # (connect, port_name)
    plcChanged = Signal(str)
    plcConnectRequested = Signal(bool, str)  # (connect, port_name)
    laserConnectRequested = Signal(bool)  # (connect)
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Load settings
        self.sfis_com = settings_manager.get("connection.sfc.com_port", "COM8")
        self.plc_com = settings_manager.get("connection.plc.com_port", "COM3")
        self.op_num = settings_manager.get("general.op_num", "")
        # ===== SFIS Control =====
        self.btn_sfis = QPushButton("SFIS OFF")
        self.btn_sfis.setCheckable(True)
        self.btn_sfis.setChecked(False)
        self.btn_sfis.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        self.btn_sfis.toggled.connect(self._onSfisButtonToggled)
        layout.addWidget(self.btn_sfis)
        
        # SFIS COM port selector
        self.combo_sfis_com = QComboBox()
        self.combo_sfis_com.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", 
                                       "COM7", "COM8", "COM9", "COM10", "COM11", "COM12"])
        self.combo_sfis_com.setCurrentText(self.sfis_com)
        self.combo_sfis_com.setMaximumWidth(80)
        self.combo_sfis_com.currentTextChanged.connect(self.sfisChanged.emit)
        # layout.addWidget(self.combo_sfis_com)
        
        # ===== PLC Control =====
        self.btn_plc = QPushButton("PLC OFF")
        self.btn_plc.setCheckable(True)
        self.btn_plc.setChecked(False)
        self.btn_plc.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        self.btn_plc.toggled.connect(self._onPlcButtonToggled)
        layout.addWidget(self.btn_plc)
        
        # PLC COM port selector
        self.combo_plc_com = QComboBox()
        self.combo_plc_com.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", 
                                      "COM7", "COM8", "COM9", "COM10", "COM11", "COM12"])
        self.combo_plc_com.setCurrentText(self.plc_com)
        self.combo_plc_com.setMaximumWidth(80)
        self.combo_plc_com.currentTextChanged.connect(self.plcChanged.emit)
        # layout.addWidget(self.combo_plc_com)

        # ===== Laser Control =====
        self.btn_laser = QPushButton("LASER OFF")
        self.btn_laser.setCheckable(True)
        self.btn_laser.setChecked(False)
        self.btn_laser.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        self.btn_laser.toggled.connect(self._onLaserButtonToggled)
        layout.addWidget(self.btn_laser)
        
        # Separator
        layout.addSpacing(20)
        
        # ===== Info Labels =====
        lbl = QLabel("Version: 1.0.1b")
        lbl.setStyleSheet("padding: 2px; border: 1px solid #ccc;")
        layout.addWidget(lbl)

        lbl = QLabel(f"OP_Num: {self.op_num}")
        lbl.setStyleSheet("padding: 2px; border: 1px solid #ccc;")
        layout.addWidget(lbl)
        
        lbl = QLabel("PC Name: ")
        lbl.setStyleSheet("padding: 2px; border: 1px solid #ccc;")
        layout.addWidget(lbl)
        
        layout.addStretch()
        
        self.setMaximumHeight(35)
        self.setStyleSheet("background-color: #f0f0f0;")
    
    # ===== Event Handlers =====
    def _onSfisButtonToggled(self, checked):
        """Xử lý khi toggle nút SFIS ON/OFF"""
        port_name = self.combo_sfis_com.currentText()
        
        if checked:
            # Kết nối
            self.btn_sfis.setText("Connecting...")
            self.btn_sfis.setEnabled(False)
            self.combo_sfis_com.setEnabled(False)
            self.sfisConnectRequested.emit(True, port_name)
        else:
            # Ngắt kết nối
            self.btn_sfis.setText("Disconnecting...")
            self.btn_sfis.setEnabled(False)
            self.sfisConnectRequested.emit(False, port_name)
    
    def _onPlcButtonToggled(self, checked):
        """Xử lý khi toggle nút PLC ON/OFF"""
        port_name = self.combo_plc_com.currentText()
        
        if checked:
            # Kết nối
            self.btn_plc.setText("Connecting...")
            self.btn_plc.setEnabled(False)
            self.combo_plc_com.setEnabled(False)
            self.plcConnectRequested.emit(True, port_name)
        else:
            # Ngắt kết nối
            self.btn_plc.setText("Disconnecting...")
            self.btn_plc.setEnabled(False)
            self.plcConnectRequested.emit(False, port_name)
    
    def _onLaserButtonToggled(self, checked):
        """Xử lý khi toggle nút Laser ON/OFF"""
        if checked:
            # Kết nối
            self.btn_laser.setText("Connecting...")
            self.btn_laser.setEnabled(False)
            self.laserConnectRequested.emit(True)
        else:
            # Ngắt kết nối
            self.btn_laser.setText("Disconnecting...")
            self.btn_laser.setEnabled(False)
            self.laserConnectRequested.emit(False)
    
    # ===== Status Update Methods =====
    def setSFISConnectionStatus(self, connected, message=""):
        """Cập nhật trạng thái kết nối SFIS"""
        self.btn_sfis.setEnabled(True)
        self.combo_sfis_com.setEnabled(not connected)
        
        if connected:
            self.btn_sfis.setChecked(True)
            self.btn_sfis.setText("SFIS ON")
        else:
            self.btn_sfis.setChecked(False)
            self.btn_sfis.setText("SFIS OFF")
    
    def setPLCConnectionStatus(self, connected, message=""):
        """Cập nhật trạng thái kết nối PLC"""
        self.btn_plc.setEnabled(True)
        self.combo_plc_com.setEnabled(not connected)
        
        if connected:
            self.btn_plc.setChecked(True)
            self.btn_plc.setText("PLC ON")
        else:
            self.btn_plc.setChecked(False)
            self.btn_plc.setText("PLC OFF")
    
    def setLaserConnectionStatus(self, connected, message=""):
        """Cập nhật trạng thái kết nối Laser"""
        self.btn_laser.setEnabled(True)
        
        if connected:
            self.btn_laser.setChecked(True)
            self.btn_laser.setText("LASER ON")
        else:
            self.btn_laser.setChecked(False)
            self.btn_laser.setText("LASER OFF")

