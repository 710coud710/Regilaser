from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QSpinBox, QCheckBox, QFrame
)


class ConnectionSettingPage(QWidget):
    """Connection settings page with SFC, PLC, and LaserMachine groups."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Connection Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # --- SFC settings group ---
        self._createSFCGroup(layout)
        self.add_line(layout)
        # --- PLC settings group ---
        self._createPLCGroup(layout)
        self.add_line(layout)
        # --- LaserMachine settings group ---
        self._createLaserGroup(layout)
        layout.addStretch()

    def add_line(self, parent_layout):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        parent_layout.addWidget(line)

    def _createSFCGroup(self, parent_layout):
        """Create SFC connection settings group"""
        sfc_layout = QHBoxLayout()
        sfc_label = QLabel("SFC")
        sfc_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        sfc_layout.addWidget(sfc_label)

        # SFC: Choose COM or TCP/IP, chỉ cho phép COM, TCP/IP bị disable tạm thời
        self.sfc_com_checkbox = QCheckBox("COM")
        self.sfc_tcpip_checkbox = QCheckBox("TCP/IP")
        self.sfc_com_checkbox.setChecked(True)
        self.sfc_tcpip_checkbox.setChecked(False)
        self.sfc_tcpip_checkbox.setEnabled(False)  # TCP/IP không thể tích

        sfc_layout.addWidget(self.sfc_com_checkbox)
        sfc_layout.addWidget(self.sfc_tcpip_checkbox)
        sfc_layout.addStretch()
        parent_layout.addLayout(sfc_layout)

        sfc_settings_split = QHBoxLayout()

        # --- Left: SFC COM settings ---
        self.sfc_com_widget = QWidget()
        sfc_com_vbox = QVBoxLayout(self.sfc_com_widget)
        sfc_com_form = QFormLayout()
        self.sfc_com_port = QLineEdit()
        self.sfc_baudrate = QLineEdit()
        sfc_com_form.addRow("COM:", self.sfc_com_port)
        sfc_com_form.addRow("Baudrate:", self.sfc_baudrate)
        sfc_com_vbox.addLayout(sfc_com_form)
        sfc_com_vbox.addStretch()
        sfc_settings_split.addWidget(self.sfc_com_widget)

        # --- Right: SFC TCP/IP settings ---
        self.sfc_tcpip_widget = QWidget()
        sfc_tcpip_vbox = QVBoxLayout(self.sfc_tcpip_widget)
        sfc_tcpip_form = QFormLayout()
        self.sfc_ip = QLineEdit()
        self.sfc_port = QLineEdit()
        sfc_tcpip_form.addRow("IP:", self.sfc_ip)
        sfc_tcpip_form.addRow("Port:", self.sfc_port)
        sfc_tcpip_vbox.addLayout(sfc_tcpip_form)
        sfc_tcpip_vbox.addStretch()
        sfc_settings_split.addWidget(self.sfc_tcpip_widget)

        parent_layout.addLayout(sfc_settings_split)

        # Enable/disable functions
        def set_sfc_com_enabled(enable):
            self.sfc_com_port.setEnabled(enable)
            self.sfc_baudrate.setEnabled(enable)
            self.sfc_com_widget.setEnabled(enable)

        def set_sfc_tcpip_enabled(enable):
            self.sfc_ip.setEnabled(enable)
            self.sfc_port.setEnabled(enable)
            self.sfc_tcpip_widget.setEnabled(enable)

        # Event handlers
        def on_sfc_com_checked(state):
            if state:
                self.sfc_tcpip_checkbox.setChecked(False)
                set_sfc_com_enabled(True)
                set_sfc_tcpip_enabled(False)
            else:
                if not self.sfc_tcpip_checkbox.isChecked():
                    self.sfc_com_checkbox.setChecked(True)

        def on_sfc_tcpip_checked(state):
            if state:
                self.sfc_com_checkbox.setChecked(False)
                set_sfc_com_enabled(False)
                set_sfc_tcpip_enabled(True)
            else:
                if not self.sfc_com_checkbox.isChecked():
                    self.sfc_tcpip_checkbox.setChecked(True)

        # Connect events
        self.sfc_com_checkbox.toggled.connect(on_sfc_com_checked)
        self.sfc_tcpip_checkbox.toggled.connect(on_sfc_tcpip_checked)

        # Set initial state
        set_sfc_com_enabled(self.sfc_com_checkbox.isChecked())
        set_sfc_tcpip_enabled(self.sfc_tcpip_checkbox.isChecked())



    def _createPLCGroup(self, parent_layout):
        """Create PLC connection settings group"""
        plc_layout = QHBoxLayout()
        plc_label = QLabel("PLC")
        plc_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        plc_layout.addWidget(plc_label)

        # plc: Choose COM or TCP/IP, only one can be edited
        self.plc_com_checkbox = QCheckBox("COM")
        self.plc_tcpip_checkbox = QCheckBox("TCP/IP")
        self.plc_com_checkbox.setChecked(True)
        self.plc_tcpip_checkbox.setChecked(False)
        self.plc_tcpip_checkbox.setEnabled(False)  # TCP/IP không thể tích

        plc_layout.addWidget(self.plc_com_checkbox)
        plc_layout.addWidget(self.plc_tcpip_checkbox)
        plc_layout.addStretch()
        parent_layout.addLayout(plc_layout)

        plc_settings_split = QHBoxLayout()

        # --- Left: plc COM settings ---
        self.plc_com_widget = QWidget()
        plc_com_vbox = QVBoxLayout(self.plc_com_widget)
        plc_com_form = QFormLayout()
        self.plc_com_port = QLineEdit()
        self.plc_baudrate = QLineEdit()
        plc_com_form.addRow("COM:", self.plc_com_port)
        plc_com_form.addRow("Baudrate:", self.plc_baudrate)
        plc_com_vbox.addLayout(plc_com_form)
        plc_com_vbox.addStretch()
        plc_settings_split.addWidget(self.plc_com_widget)

        # --- Right: plc TCP/IP settings ---
        self.plc_tcpip_widget = QWidget()
        plc_tcpip_vbox = QVBoxLayout(self.plc_tcpip_widget)
        plc_tcpip_form = QFormLayout()
        self.plc_ip = QLineEdit()
        self.plc_port = QLineEdit()
        plc_tcpip_form.addRow("IP:", self.plc_ip)
        plc_tcpip_form.addRow("Port:", self.plc_port)
        plc_tcpip_vbox.addLayout(plc_tcpip_form)
        plc_tcpip_vbox.addStretch()
        plc_settings_split.addWidget(self.plc_tcpip_widget)

        parent_layout.addLayout(plc_settings_split)

        # Enable/disable functions
        def set_plc_com_enabled(enable):
            self.plc_com_port.setEnabled(enable)
            self.plc_baudrate.setEnabled(enable)
            self.plc_com_widget.setEnabled(enable)

        def set_plc_tcpip_enabled(enable):
            self.plc_ip.setEnabled(enable)
            self.plc_port.setEnabled(enable)
            self.plc_tcpip_widget.setEnabled(enable)

        # Event handlers
        def on_plc_com_checked(state):
            if state:
                self.plc_tcpip_checkbox.setChecked(False)
                set_plc_com_enabled(True)
                set_plc_tcpip_enabled(False)
            else:
                if not self.plc_tcpip_checkbox.isChecked():
                    self.plc_com_checkbox.setChecked(True)

        def on_plc_tcpip_checked(state):
            if state:
                self.plc_com_checkbox.setChecked(False)
                set_plc_com_enabled(False)
                set_plc_tcpip_enabled(True)
            else:
                if not self.plc_com_checkbox.isChecked():
                    self.plc_tcpip_checkbox.setChecked(True)

        # Connect events
        self.plc_com_checkbox.toggled.connect(on_plc_com_checked)
        self.plc_tcpip_checkbox.toggled.connect(on_plc_tcpip_checked)

        # Set initial state
        set_plc_com_enabled(self.plc_com_checkbox.isChecked())
        set_plc_tcpip_enabled(self.plc_tcpip_checkbox.isChecked())

    def _createLaserGroup(self, parent_layout):
        """Create LaserMachine connection settings group"""
        laser_layout = QHBoxLayout()
        laser_label = QLabel("Laser")
        laser_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        laser_layout.addWidget(laser_label)

        # laser: Choose COM or TCP/IP, only one can be edited
        self.laser_com_checkbox = QCheckBox("COM")
        self.laser_tcpip_checkbox = QCheckBox("TCP/IP")
        self.laser_com_checkbox.setChecked(True)
        self.laser_tcpip_checkbox.setChecked(False)

        laser_layout.addWidget(self.laser_com_checkbox)
        laser_layout.addWidget(self.laser_tcpip_checkbox)
        laser_layout.addStretch()
        parent_layout.addLayout(laser_layout)

        laser_settings_split = QHBoxLayout()

        # --- Left: laser COM settings ---
        self.laser_com_widget = QWidget()
        laser_com_vbox = QVBoxLayout(self.laser_com_widget)
        laser_com_form = QFormLayout()
        self.laser_com_port = QLineEdit()
        self.laser_baudrate = QLineEdit()
        laser_com_form.addRow("COM:", self.laser_com_port)
        laser_com_form.addRow("Baudrate:", self.laser_baudrate)
        laser_com_vbox.addLayout(laser_com_form)
        laser_com_vbox.addStretch()
        laser_settings_split.addWidget(self.laser_com_widget)

        # --- Right: laser TCP/IP settings ---
        self.laser_tcpip_widget = QWidget()
        laser_tcpip_vbox = QVBoxLayout(self.laser_tcpip_widget)
        laser_tcpip_form = QFormLayout()
        self.laser_ip = QLineEdit()
        self.laser_port = QLineEdit()
        laser_tcpip_form.addRow("IP:", self.laser_ip)
        laser_tcpip_form.addRow("Port:", self.laser_port)
        laser_tcpip_vbox.addLayout(laser_tcpip_form)
        laser_tcpip_vbox.addStretch()
        laser_settings_split.addWidget(self.laser_tcpip_widget)

        parent_layout.addLayout(laser_settings_split)

        # Enable/disable functions
        def set_laser_com_enabled(enable):
            self.laser_com_port.setEnabled(enable)
            self.laser_baudrate.setEnabled(enable)
            self.laser_com_widget.setEnabled(enable)

        def set_laser_tcpip_enabled(enable):
            self.laser_ip.setEnabled(enable)
            self.laser_port.setEnabled(enable)
            self.laser_tcpip_widget.setEnabled(enable)

        # Event handlers
        def on_laser_com_checked(state):
            if state:
                self.laser_tcpip_checkbox.setChecked(False)
                set_laser_com_enabled(True)
                set_laser_tcpip_enabled(False)
            else:
                if not self.laser_tcpip_checkbox.isChecked():
                    self.laser_com_checkbox.setChecked(True)

        def on_laser_tcpip_checked(state):
            if state:
                self.laser_com_checkbox.setChecked(False)
                set_laser_com_enabled(False)
                set_laser_tcpip_enabled(True)
            else:
                if not self.laser_com_checkbox.isChecked():
                    self.laser_tcpip_checkbox.setChecked(True)

        # Connect events
        self.laser_com_checkbox.toggled.connect(on_laser_com_checked)
        self.laser_tcpip_checkbox.toggled.connect(on_laser_tcpip_checked)

        # Set initial state
        set_laser_com_enabled(self.laser_com_checkbox.isChecked())
        set_laser_tcpip_enabled(self.laser_tcpip_checkbox.isChecked())        
        # ------
        laser_settings_layout = QVBoxLayout()
        laser_settings_layout.setContentsMargins(7, 0, 0, 0)
        laser_settings_layout.setSpacing(5)
        # laser: Choose COM or TCP/IP, only one can be edited
        self.laser_timeout_ms = QLineEdit()
        self.laser_timeout_form = QFormLayout()
        self.laser_timeout_form.addRow("Time out (ms):", self.laser_timeout_ms)
        laser_settings_layout.addLayout(self.laser_timeout_form)
        self.laser_timeout_ms.setFixedWidth(150)
        parent_layout.addLayout(laser_settings_layout)

    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            "sfc_use_com": self.sfc_com_checkbox.isChecked(),
            "sfc_com_port": self.sfc_com_port.text().strip(),
            "sfc_baudrate": self.sfc_baudrate.value(),
            "sfc_ip": self.sfc_ip.text().strip(),
            "sfc_port": self.sfc_port.value(),
            "plc_com": self.plc_com.text().strip(),
            "laser_ip": self.laser_ip.text().strip(),
            "laser_port": self.laser_port.value(),
            "laser_com_port": self.laser_com_port.text().strip(),
            "laser_baudrate": self.laser_baudrate.value(),
        }

    def set_settings(self, settings):
        """Set settings from dictionary"""
        self.sfc_com_checkbox.setChecked(settings.get("sfc_use_com", True))
        self.sfc_tcpip_checkbox.setChecked(not settings.get("sfc_use_com", True))
        self.sfc_com_port.setText(settings.get("sfc_com_port", ""))
        self.sfc_baudrate.setValue(settings.get("sfc_baudrate", 9600))
        self.sfc_ip.setText(settings.get("sfc_ip", ""))
        self.sfc_port.setValue(settings.get("sfc_port", 8080))
        self.plc_com.setText(settings.get("plc_com", ""))
        self.laser_ip.setText(settings.get("laser_ip", ""))
        self.laser_port.setValue(settings.get("laser_port", 50002))
        self.laser_com_port.setText(settings.get("laser_com_port", ""))
        self.laser_baudrate.setValue(settings.get("laser_baudrate", 9600))
