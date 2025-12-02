"""
Top Control Panel - Chứa ALL PARTS SN, MO, SFIS, CCD inputs
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, 
                               QGroupBox, QComboBox, 
                               QPushButton, QLabel)
from PySide6.QtCore import Signal

from config import ConfigManager
config = ConfigManager().get()

class TopControlPanel(QWidget):
    """Panel điều khiển phía trên"""
    sfisChanged = Signal(str)
    sfisConnectRequested = Signal(bool, str)  # (connect, port_name)
    plcChanged = Signal(str)
    plcConnectRequested = Signal(bool, str)  # (connect, port_name)
    def __init__(self):
        super().__init__()
        self._init_ui()
     
    def _init_ui(self):
        self.sfis_com = getattr(config, "SFIS_COM", None) if getattr(config, "SFIS_COM", None) else "COM8"
        self.plc_com = getattr(config, "PLC_COM", None) if getattr(config, "PLC_COM", None) else "COM3" 
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)              
        
        #--------------------------------SFIS--------------------------------
        sfis_group = QGroupBox()
        sfis_layout = QHBoxLayout()
        sfis_layout.setContentsMargins(5, 5, 5, 5)
        sfis_layout.setSpacing(10)

        # SFIS button
        self.btn_sfis = QPushButton("SFIS OFF")
        self.btn_sfis.setCheckable(True)
        self.btn_sfis.setChecked(False)
        self.btn_sfis.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        self.btn_sfis.toggled.connect(self._onSfisButtonToggled)
        sfis_layout.addWidget(self.btn_sfis)

        #SFIS COM port
        self.combo_sfis_com = QComboBox()
        self.combo_sfis_com.addItems(["COM1", "COM2", "COM3", "COM4", "COM5","COM6", "COM7", "COM8", "COM9", "COM10","COM11", "COM12"])
        self.combo_sfis_com.setCurrentText(self.sfis_com)
        self.combo_sfis_com.currentTextChanged.connect(self.sfisChanged.emit)
        sfis_layout.addWidget(self.combo_sfis_com)
    
        # sfis_layout.addStretch()
        sfis_group.setLayout(sfis_layout)
        layout.addWidget(sfis_group)

        #--------------------------------PLC--------------------------------
        plc_group = QGroupBox()
        plc_layout = QHBoxLayout()
        plc_layout.setContentsMargins(5, 5, 5, 5)
        plc_layout.setSpacing(10)

        # SFIS button
        self.btn_plc = QPushButton("PLC OFF")
        self.btn_plc.setCheckable(True)
        self.btn_plc.setChecked(False)
        self.btn_plc.setStyleSheet("""
            QPushButton { 
                background-color: #ffc0cb; 
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:checked { 
                background-color: #9fff9f; 
            }
        """)
        self.btn_plc.toggled.connect(self._onPlcButtonToggled)
        plc_layout.addWidget(self.btn_plc)

        # SFIS COM port
        self.combo_plc_com = QComboBox()
        self.combo_plc_com.addItems(["COM1", "COM2", "COM3", "COM4", "COM5","COM6", "COM7", "COM8", "COM9", "COM10","COM11", "COM12"])
        self.combo_plc_com.setCurrentText(config.PLC_COM)
        self.combo_plc_com.currentTextChanged.connect(self.plcChanged.emit)
        plc_layout.addWidget(self.combo_plc_com)
    
        # plc_layout.addStretch()
        plc_group.setLayout(plc_layout)
        layout.addWidget(plc_group)
        

        
        #--------------------------------Status dot Laser--------------------------------
        status_group = QGroupBox()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(10)

        laser_status = QHBoxLayout()
        laser_status.setContentsMargins(0, 0, 0, 0)
        laser_status.setSpacing(8)

        # Dot indicator
        self.dot_laser_status = QLabel()
        self.dot_laser_status.setFixedSize(20, 20)
        self.dot_laser_status.setStyleSheet(
            """
            background-color: red;
            border-radius: 10px;
            border: 1px solid #444;
            """
        )
        laser_status.addWidget(self.dot_laser_status)

        # Label text
        self.lbl_laser_status = QLabel("Laser Machine")
        self.lbl_laser_status.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: #313647;
            padding-left: 5px;
        """)        
        laser_status.addWidget(self.lbl_laser_status)


        status_layout.addLayout(laser_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Stretch để
        layout.addStretch()
        self.setMaximumHeight(80)



    def _onSfisButtonToggled(self, checked):
        """Xử lý khi toggle nút SFIS ON/OFF"""
        port_name = self.combo_sfis_com.currentText()
        
        if checked:
            # kết nối
            self.btn_sfis.setText("Connecting...")
            self.btn_sfis.setEnabled(False)
            self.combo_sfis_com.setEnabled(False)
            self.sfisConnectRequested.emit(True, port_name)
        else:
            # ngắt kết nối
            self.btn_sfis.setText("Disconnecting...")
            self.btn_sfis.setEnabled(False)
            self.sfisConnectRequested.emit(False, port_name)
    
    def setSFISConnectionStatus(self, connected, message=""):
        self.btn_sfis.setEnabled(True)
        self.combo_sfis_com.setEnabled(not connected)
        
        if connected:
            self.btn_sfis.setChecked(True)
            self.btn_sfis.setText("SFIS ON")
        else:
            self.btn_sfis.setChecked(False)
            self.btn_sfis.setText("SFIS OFF")
    


    def _onPlcButtonToggled(self, checked):
        """Xử lý khi toggle nút PLC ON/OFF"""
        port_name = self.combo_plc_com.currentText()
        
        if checked:
            # kết nối
            self.btn_plc.setText("Connecting...")
            self.btn_plc.setEnabled(False)
            self.combo_plc_com.setEnabled(False)
            self.plcConnectRequested.emit(True, port_name)
        else:
            # ngắt kết nối
            self.btn_plc.setText("Disconnecting...")
            self.btn_plc.setEnabled(False)
            self.plcConnectRequested.emit(False, port_name)

    def setPLCConnectionStatus(self, connected, message=""):
        self.btn_plc.setEnabled(True)
        self.combo_plc_com.setEnabled(not connected)
        
        if connected:
            self.btn_plc.setChecked(True)
            self.btn_plc.setText("PLC ON")
        else:
            self.btn_plc.setChecked(False)
            self.btn_plc.setText("PLC OFF")

    def setLaserConnectionStatus(self, connected, message=""):
        """Cập nhật trạng thái kết nối laser trên UI"""
        if connected:
            # Màu xanh khi đã kết nối
            self.dot_laser_status.setStyleSheet(
                """
                background-color: green;
                border-radius: 10px;
                border: 1px solid #444;
                """
            )
            self.lbl_laser_status.setText("Laser Machine (Connected)")
        else:
            # Màu đỏ khi chưa kết nối
            self.dot_laser_status.setStyleSheet(
                """
                background-color: red;
                border-radius: 10px;
                border: 1px solid #444;
                """
            )
            self.lbl_laser_status.setText("Laser Machine (Disconnected)")