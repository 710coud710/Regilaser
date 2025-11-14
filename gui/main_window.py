"""
Main Window - Container chính cho toàn bộ giao diện
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from gui.top_control_panel import TopControlPanel
from gui.left_control_panel import LeftControlPanel
from gui.center_panel import CenterPanel
from gui.right_panel import RightPanel
from gui.result_display import ResultDisplay
from gui.bottom_status_bar import BottomStatusBar


class MainWindow(QMainWindow):
    """Main window của Sprite Auto Laser Marking Program"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprite Auto Laser Marking Program - Version 2.0")
        self.setGeometry(100, 100, 1200, 700)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Top control panel
        self.top_panel = TopControlPanel()
        main_layout.addWidget(self.top_panel)
        
        # Middle section (left + center + right)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)
        
        # Left control panel
        self.left_panel = LeftControlPanel()
        middle_layout.addWidget(self.left_panel)
        
        # Center panel
        self.center_panel = CenterPanel()
        middle_layout.addWidget(self.center_panel)
        
        # Right panel
        self.right_panel = RightPanel()
        middle_layout.addWidget(self.right_panel)
        
        main_layout.addLayout(middle_layout)
        
        # Result display area
        self.result_display = ResultDisplay()
        main_layout.addWidget(self.result_display, stretch=1)
        
        # Bottom status bar
        self.bottom_status = BottomStatusBar()
        main_layout.addWidget(self.bottom_status)
        
        # Kết nối signals (sẽ được xử lý bởi presenter)
        self._connect_signals()
    
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

