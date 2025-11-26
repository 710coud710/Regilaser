"""
Top Control Panel - Chứa ALL PARTS SN, MO, SFIS, CCD inputs
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, 
                               QGroupBox, QComboBox, 
                               QPushButton)
from PySide6.QtCore import Signal


class TopControlPanel(QWidget):
    """Panel điều khiển phía trên"""
    
    # Signals
    # allPartsSnChanged = Signal(str)
    # moChanged = Signal(str)
    sfisChanged = Signal(str)
    sfisConnectRequested = Signal(bool, str)  # (connect, port_name)
    plcChanged = Signal(str)
    plcConnectRequested = Signal(bool, str)  # (connect, port_name)
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
              
        # # MO
        # mo_group = QGroupBox()
        # mo_layout = QVBoxLayout()
        # mo_layout.setContentsMargins(5, 5, 5, 5)
        # mo_layout.setSpacing(2)
        
        # lbl_mo = QLabel("MO:")
        # lbl_mo.setStyleSheet("font-weight: bold;")
        # mo_layout.addWidget(lbl_mo)
        
        # self.input_mo = QLineEdit()
        # # self.input_mo.setReadOnly(True)
        # self.input_mo.setPlaceholderText("1234567890")
        # # self.input_mo.textChanged.connect(self.mo_changed.emit)
        # mo_layout.addWidget(self.input_mo)
        
        # mo_group.setLayout(mo_layout)
        # layout.addWidget(mo_group)
        
        # SFIS
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

        # SFIS COM port
        self.combo_sfis_com = QComboBox()
        self.combo_sfis_com.addItems(["COM1", "COM2", "COM3", "COM4", "COM5","COM6", "COM7", "COM8", "COM9", "COM10","COM11", "COM12"])
        self.combo_sfis_com.setCurrentText("COM8")
        self.combo_sfis_com.currentTextChanged.connect(self.sfisChanged.emit)
        sfis_layout.addWidget(self.combo_sfis_com)
    
        # sfis_layout.addStretch()
        sfis_group.setLayout(sfis_layout)
        layout.addWidget(sfis_group)

        #PLC COM Button
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
        self.combo_plc_com.setCurrentText("COM3")
        self.combo_plc_com.currentTextChanged.connect(self.plcChanged.emit)
        plc_layout.addWidget(self.combo_plc_com)
    
        # plc_layout.addStretch()
        plc_group.setLayout(plc_layout)
        layout.addWidget(plc_group)
        


        # Stretch để các group không bị kéo dãn quá mức
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