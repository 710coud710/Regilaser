"""
Top Control Panel - Chứa ALL PARTS SN, MO, SFIS, CCD inputs
"""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QLineEdit, 
                               QCheckBox, QGroupBox, QVBoxLayout, QComboBox, 
                               QPushButton)
from PySide6.QtCore import Signal, Qt


class TopControlPanel(QWidget):
    """Panel điều khiển phía trên"""
    
    # Signals
    allPartsSnChanged = Signal(str)
    moChanged = Signal(str)
    sfisChanged = Signal(str)
    sfisConnectRequested = Signal(bool, str)  # (connect, port_name)
    ccdChanged = Signal(str)
    
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
        self.combo_sfis_com.addItems(["COM2", "COM1", "COM3", "COM4", "COM5","COM6", "COM7", "COM8", "COM9", "COM10","COM11", "COM12"])
        self.combo_sfis_com.currentTextChanged.connect(self.sfisChanged.emit)
        sfis_layout.addWidget(self.combo_sfis_com)
    
        # sfis_layout.addStretch()
        sfis_group.setLayout(sfis_layout)
        layout.addWidget(sfis_group)

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
        """
        Cập nhật trạng thái kết nối SFIS từ Presenter
        
        Args:
            connected (bool): True nếu đã kết nối
            message (str): Thông báo (optional)
        """
        self.btn_sfis.setEnabled(True)
        self.combo_sfis_com.setEnabled(not connected)
        
        if connected:
            self.btn_sfis.setChecked(True)
            self.btn_sfis.setText("SFIS ON")
        else:
            self.btn_sfis.setChecked(False)
            self.btn_sfis.setText("SFIS OFF")
    
    # Getter methods
    def getAllPartsSN(self):
        """Lấy giá trị ALL PARTS SN"""
        return self.input_all_parts_sn.text()
    
    def getMO(self):
        """Lấy giá trị MO"""
        return self.input_mo.text()
    
    def getSFIS(self):
        """Lấy giá trị SFIS COM port"""
        return self.combo_sfis_com.currentText()
    
    def getCCD(self):
        """Lấy giá trị CCD COM port"""
        return self.combo_ccd_com.currentText()
    
    def isAllPartsChecked(self):
        """Kiểm tra xem checkbox ALL PARTS có được check không"""
        return self.chk_all_parts.isChecked()
    
    # Setter methods
    def setAllPartsSN(self, text):
        """Set giá trị ALL PARTS SN"""
        self.input_all_parts_sn.setText(text)
    
    def setMO(self, text):
        """Set giá trị MO"""
        self.input_mo.setText(text)
    
    def setSFIS(self, com_port):
        """Set giá trị SFIS COM port"""
        index = self.combo_sfis_com.findText(com_port)
        if index >= 0:
            self.combo_sfis_com.setCurrentIndex(index)
    
    def setCCD(self, com_port):
        """Set giá trị CCD COM port"""
        index = self.combo_ccd_com.findText(com_port)
        if index >= 0:
            self.combo_ccd_com.setCurrentIndex(index)




