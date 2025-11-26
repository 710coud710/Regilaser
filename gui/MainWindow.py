"""
Main Window - Container chính cho toàn bộ giao diện
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from gui import (
    TopControlPanel,
    LeftControlPanel,
    CenterPanel,
    RightPanel,
    LogDisplay,
    BottomStatusBar
)

class MainWindow(QMainWindow):
    """Main window của Sprite Auto Laser Marking Program"""
    
    # Signals cho menu actions
    menu_clicked = Signal()
    reset_clicked = Signal()
    keyboard_clicked = Signal()
    sendLaserPsn20_clicked = Signal()
    sendLaserPsn16_clicked = Signal()
    sendPLCPOK_clicked = Signal()
    sendPLCNG_clicked = Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regilazi - Version 1.0 Prenium")
        # self.setGeometry(100, 100, 1000, 700)
        # Tạo menu bar
        self._createMenuBar()
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        """Main layout"""
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        """Top control panel"""
        self.top_panel = TopControlPanel()
        main_layout.addWidget(self.top_panel)
   
        """Middle control panel"""
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)
        self.left_panel = LeftControlPanel()
        middle_layout.addWidget(self.left_panel)        
        self.center_panel = CenterPanel()
        middle_layout.addWidget(self.center_panel)
        # self.right_panel = RightPanel()
        # middle_layout.addWidget(self.right_panel)

        main_layout.addLayout(middle_layout)
        
        """Result display panel"""
        self.result_display = LogDisplay()
        main_layout.addWidget(self.result_display, stretch=1)
        
        """Bottom status panel"""
        self.bottom_status = BottomStatusBar()
        # main_layout.addWidget(self.bottom_status)
        
        # Kết nối signals (sẽ được xử lý bởi presenter)
        self._connectSignals()
    
    def _createMenuBar(self):
        """Tạo menu bar với các actions"""
        menubar = self.menuBar()
        # File menu
        file_menu = menubar.addMenu("&File")
        plc_menu = menubar.addMenu("&PLC")
        sfis_menu = menubar.addMenu("&SFIS")
        laser_menu = menubar.addMenu("&Laser")
        check_menu = menubar.addMenu("&Check")
        ######File menu#####
        # Menu action
        menu_action = QAction("Menu", self)
        menu_action.setShortcut("Ctrl+M")
        menu_action.triggered.connect(self.menu_clicked.emit)
        file_menu.addAction(menu_action)
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        #--------------------------------PLC menu--------------------------------
        send_plc_ok_action = QAction("Send OK to PLC", self)
        send_plc_ok_action.setShortcut("Ctrl+P")
        send_plc_ok_action.triggered.connect(self.sendPLCPOK_clicked.emit)
        plc_menu.addAction(send_plc_ok_action)

        send_plc_ng_action = QAction("Send NG to PLC", self)
        send_plc_ng_action.setShortcut("Ctrl+N")
        send_plc_ng_action.triggered.connect(self.sendPLCNG_clicked.emit)
        plc_menu.addAction(send_plc_ng_action)  


        ######Check menu#####


        
        send_psn16_action = QAction("Send PSN16 to LASER", self)
        send_psn16_action.setShortcut("Ctrl+1")
        send_psn16_action.triggered.connect(self.sendLaserPsn16_clicked.emit)
        check_menu.addAction(send_psn16_action)


        send_psn_action = QAction("Send PSN20 to LASER", self)
        send_psn_action.setShortcut("Ctrl+2")
        send_psn_action.triggered.connect(self.sendLaserPsn20_clicked.emit)
        check_menu.addAction(send_psn_action)
        

        check_menu.addSeparator()

    def _connectSignals(self):
        """Kết nối các signals giữa các panel"""
        # Các signals này sẽ được presenter subscribe
        pass
    
    # Getter methods để presenter có thể truy cập các panel
    def getTopPanel(self):
        return self.top_panel
    
    def getLeftPanel(self):
        return self.left_panel
    
    def getCenterPanel(self):
        return self.center_panel
    
    def getRightPanel(self):
        return self.right_panel
    
    def getResultDisplay(self):
        return self.result_display
    
    def getBottomStatus(self):
        return self.bottom_status


