"""
Main Window - Container chính cho toàn bộ giao diện
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import  Signal
from PySide6.QtGui import QAction, QIcon, QFont
from utils.AppPathService import getAppDirectory
import os
from gui import (   
    TopTopPanel,
    TopControlPanel,
    LeftControlPanel,
    CenterPanel, 
    LogDisplay,
    BottomStatusBar,
)
from gui.projectWindow import ProjectTable

class MainWindow(QMainWindow):
    """Main window của Sprite Auto Laser Marking Program"""
    
    # Signals cho menu actions
    menu_clicked = Signal()
    project_clicked = Signal()
    #Laser menu
    sendC2_clicked = Signal()
    sendGA_clicked = Signal()
    sendNT_clicked = Signal()
    #PLC menu
    sendPLCPOK_clicked = Signal()
    sendPLCNG_clicked = Signal()
    #SFIS menu
    sendNeedPSN_clicked = Signal()
    sendActivateSFIS_clicked = Signal()
    sendBOMVER_clicked = Signal()
    sendBOMVERNeedSN_clicked = Signal()
    #Help menu
    setting_clicked = Signal()
    about_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regilazi - Version 1.0 Prenium")
        self.setWindowIcon(QIcon(os.path.join(getAppDirectory(), "icon.ico")))
    
        # self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 450)
        
        # Set default font cho toàn bộ application
        # app_font = QFont("Arial", 10)
        # self.setFont(app_font)

        # Apply background image
        bg_path = os.path.join(getAppDirectory(), "assets", "items", "bg.jpg").replace("\\", "/")
        
        # self.setStyleSheet(f"""
        #     QMainWindow {{
        #         background-image: url({bg_path});
        #         background-repeat: no-repeat;
        #         background-position: center;
        #         background-size: contain;
        #     }}
        # """)
        self.setStyleSheet(f"""
            QMainWindow {{
                 border-image: url({bg_path})  0 0 0 0 stretch stretch;
            }}
            * {{
                 font-family: Arial, sans-serif;
            }}
        """)
        
        # Tạo menu bar
        self._createMenuBar()
        # Chỉnh màu menubar bằng stylesheet
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background-color: transparent;
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QMenuBar::item:pressed {
                background: #4caf50;
                color: white;
            }
        """)
        # Main widget
        main_widget = QWidget()
        # main_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(main_widget)
        
        """Main layout"""
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        """Top control panel"""
        self.top_top_panel = TopTopPanel()
        main_layout.addWidget(self.top_top_panel)
        self.top_panel = TopControlPanel()
        # main_layout.addWidget(self.top_panel)
   
        """Middle control panel"""
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)
        self.left_panel = LeftControlPanel()
        middle_layout.addWidget(self.left_panel)        
        self.center_panel = CenterPanel()
        middle_layout.addWidget(self.center_panel)

        main_layout.addLayout(middle_layout)
        
        """Result display panel"""
        self.result_display = LogDisplay()
        main_layout.addWidget(self.result_display, stretch=1)
        
        """Bottom status panel"""
        self.bottom_status = BottomStatusBar()
        main_layout.addWidget(self.bottom_status)
        
        # Initialize project table dialog
        self.project_table_dialog = None
        
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
        help_menu = menubar.addMenu("&Help")

        #------------------------------File menu------------------------------
        # Menu action
        menu_action = QAction("Menu", self)
        menu_action.setShortcut("Ctrl+M")
        menu_action.triggered.connect(self.menu_clicked.emit)
        file_menu.addAction(menu_action)
        # Project action
        project_action = QAction("Projects", self)
        project_action.setShortcut("Ctrl+P")
        project_action.triggered.connect(self.showProjectTable)
        file_menu.addAction(project_action)
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+C")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        #------------------------------PLC menu------------------------------
        send_plc_ok_action = QAction("Send OK to PLC", self)
        send_plc_ok_action.setShortcut("Ctrl+P")
        send_plc_ok_action.triggered.connect(self.sendPLCPOK_clicked.emit)
        plc_menu.addAction(send_plc_ok_action)

        send_plc_ng_action = QAction("Send NG to PLC", self)
        send_plc_ng_action.setShortcut("Ctrl+N")
        send_plc_ng_action.triggered.connect(self.sendPLCNG_clicked.emit)
        plc_menu.addAction(send_plc_ng_action)  

        #------------------------------SFIS menu------------------------------
        Send_Activate_Action = QAction("Activate SFIS", self)
        Send_Activate_Action.setShortcut("Ctrl+8")
        Send_Activate_Action.triggered.connect(self.sendActivateSFIS_clicked.emit)
        sfis_menu.addAction(Send_Activate_Action)

        Send_needPSN_Action = QAction("Send NEEDPSN", self)
        Send_needPSN_Action.setShortcut("Ctrl+9")
        Send_needPSN_Action.triggered.connect(self.sendNeedPSN_clicked.emit)
        sfis_menu.addAction(Send_needPSN_Action)
        sfis_menu.addSeparator()
        Send_BOMVER_Action = QAction("Send BOMVER", self)
        Send_Activate_Action.setShortcut("Ctrl+8")
        Send_BOMVER_Action.triggered.connect(self.sendBOMVER_clicked.emit)
        sfis_menu.addAction(Send_BOMVER_Action)

        Send_BOMVERNeedSN_Action = QAction("Send BOMVERNeedSN", self)
        Send_BOMVERNeedSN_Action.setShortcut("Ctrl+9")
        Send_BOMVERNeedSN_Action.triggered.connect(self.sendBOMVERNeedSN_clicked.emit)
        sfis_menu.addAction(Send_BOMVERNeedSN_Action)
       #--------------------------------Laser menu--------------------------------
        send_ga_action = QAction("Activate Job", self)
        send_ga_action.setShortcut("Ctrl+1")
        send_ga_action.triggered.connect(self.sendGA_clicked.emit)
        laser_menu.addAction(send_ga_action)

        send_c2_action = QAction("Set Content", self)
        send_c2_action.setShortcut("Ctrl+2")
        send_c2_action.triggered.connect(self.sendC2_clicked.emit)
        laser_menu.addAction(send_c2_action)
        
        send_nt_action = QAction("Start Marking", self)
        send_nt_action.setShortcut("Ctrl+3")
        send_nt_action.triggered.connect(self.sendNT_clicked.emit)
        laser_menu.addAction(send_nt_action)

        laser_menu.addSeparator()

        #------------------------------Help menu------------------------------
        about_action = QAction("About", self)
        about_action.setShortcut("Ctrl+A")
        about_action.triggered.connect(self.about_clicked.emit)
        help_menu.addAction(about_action)

        setting_action = QAction("Setting", self)
        setting_action.setShortcut("Ctrl+S")
        setting_action.triggered.connect(self.setting_clicked.emit)
        help_menu.addAction(setting_action)

    def _connectSignals(self):
        """Kết nối các signals giữa các panel"""
        # Các signals này sẽ được presenter subscribe
        pass
    
    # Getter methods để presenter có thể truy cập các panel
    def getTopTopPanel(self):
        return self.top_top_panel
        
    def getTopPanel(self):
        return self.top_panel
    
    def getLeftPanel(self):
        return self.left_panel
    
    def getCenterPanel(self):
        return self.center_panel
    
    def getResultDisplay(self):
        return self.result_display
    
    def getBottomStatus(self):
        return self.bottom_status
    
    def showProjectTable(self):
        """Show project table dialog"""
        try:
            # Create dialog if not exists
            if self.project_table_dialog is None:
                self.project_table_dialog = ProjectTable(self)
                self.project_table_dialog.setWindowTitle("Project Management")
                self.project_table_dialog.resize(800, 600)
            
            # Emit signal to notify presenter to load data
            self.project_clicked.emit()
            
            # Show dialog
            self.project_table_dialog.show()
            self.project_table_dialog.raise_()
            self.project_table_dialog.activateWindow()
            
        except Exception as e:
            print(f"Error showing project table: {str(e)}")
    
    def getProjectTableDialog(self):
        """Get project table dialog instance"""
        return self.project_table_dialog


