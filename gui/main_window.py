"""
Main Window - Container chính cho toàn bộ giao diện
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from gui.top_control_panel import TopControlPanel
from gui.left_control_panel import LeftControlPanel
from gui.center_panel import CenterPanel
from gui.right_panel import RightPanel
from gui.result_display import ResultDisplay
from gui.bottom_status_bar import BottomStatusBar


class MainWindow(QMainWindow):
    """Main window của Sprite Auto Laser Marking Program"""
    
    # Signals cho menu actions
    menu_clicked = Signal()
    reset_clicked = Signal()
    keyboard_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Regilazi - Version 1.0 Prenium")
        self.setGeometry(100, 100, 1200, 700)
        # Tạo menu bar
        self._create_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        """Top control panel
        A
"""
        self.top_panel = TopControlPanel()
        main_layout.addWidget(self.top_panel)
        # Middle section (left + center + right)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)
        # Left control panel
        self.left_panel = LeftControlPanel()
        middle_layout.addWidget(self.left_panel)        
        self.center_panel = CenterPanel()
        middle_layout.addWidget(self.center_panel)
        self.right_panel = RightPanel()
        middle_layout.addWidget(self.right_panel)
        
        main_layout.addLayout(middle_layout)
        
        # Result display area
        # self.result_display = ResultDisplay()
        # main_layout.addWidget(self.result_display, stretch=1)
        
        # Bottom status bar
        # self.bottom_status = BottomStatusBar()
        # main_layout.addWidget(self.bottom_status)
        
        # Kết nối signals (sẽ được xử lý bởi presenter)
        self._connect_signals()
    
    def _create_menu_bar(self):
        """Tạo menu bar với các actions"""
        menubar = self.menuBar()
        # File menu
        file_menu = menubar.addMenu("&File")
        tools_menu = menubar.addMenu("&Tools")
        reset_menu = menubar.addMenu("&Reset")
        keyboard_menu = menubar.addMenu("&Keyboard")
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
        
        ######Tools menu#####
        # Reset action
        reset_action = QAction("Reset", self)
        reset_action.setShortcut("F5")
        reset_action.triggered.connect(self.reset_clicked.emit)
        tools_menu.addAction(reset_action)
        
        # Keyboard action
        keyboard_action = QAction("Keyboard", self)
        keyboard_action.setShortcut("Ctrl+K")
        keyboard_action.triggered.connect(self.keyboard_clicked.emit)
        tools_menu.addAction(keyboard_action)
        
        ######Reset menu#####
        reset_action = QAction("Pass to Zero", self)
        reset_action.setShortcut("F5")
        reset_action.triggered.connect(self.reset_clicked.emit)
        reset_menu.addAction(reset_action)
       
        reset_action = QAction("Fail to Zero", self)
        reset_action.setShortcut("F6")
        reset_action.triggered.connect(self.reset_clicked.emit)
        reset_menu.addAction(reset_action)

        reset_menu.addSeparator()

    def _connect_signals(self):
        """Kết nối các signals giữa các panel"""
        # Các signals này sẽ được presenter subscribe
        pass
    
    # Getter methods để presenter có thể truy cập các panel
    def get_top_panel(self):
        return self.top_panel
    
    def get_left_panel(self):
        return self.left_panel
    
    def get_center_panel(self):
        return self.center_panel
    
    def get_right_panel(self):
        return self.right_panel
    
    def get_result_display(self):
        return self.result_display
    
    def get_bottom_status(self):
        return self.bottom_status

