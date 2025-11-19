"""
Log Display - Bảng hiển thị log với thời gian, level và message
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor, QFont


class LogDisplay(QWidget):
    """Widget hiển thị log dạng bảng"""
    
    # Log levels
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    SUCCESS = "SUCCESS"
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header label
        self.lbl_header = QLabel("LOG:")
        self.lbl_header.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lbl_header.setStyleSheet("""
            color: black;
            padding: 3px 5px;
            font-size: 10pt;
            font-weight: bold;
            border: 1px solid grey;
            background-color: #f0f0f0;
        """)
        self.lbl_header.setMaximumHeight(30)
        layout.addWidget(self.lbl_header)
        
        # Table widget for logs
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        
        # Set column widths
        header = self.table.horizontalHeader()

        
        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        
        # Font settings
        font = QFont()
        font.setPointSize(9)
        font.setFamily("Consolas")
        self.table.setFont(font)
        
        # Style
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid grey;
                background-color: white;
            }
            QTableWidget::item {
                padding: 3px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid grey;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table, stretch=1)
        
        self.setMinimumHeight(300)
    
    def add_log(self, message, level=INFO):
        """Thêm một dòng log vào bảng"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Time column
        time_item = QTableWidgetItem(current_time)
        time_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setItem(row, 0, time_item)
        
        # Level column
        level_item = QTableWidgetItem(level)
        level_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        # Set color based on level
        if level == self.ERROR:
            level_item.setForeground(QColor("red"))
            level_item.setBackground(QColor("#ffe0e0"))
        elif level == self.WARNING:
            level_item.setForeground(QColor("orange"))
            level_item.setBackground(QColor("#fff4e0"))
        elif level == self.SUCCESS:
            level_item.setForeground(QColor("green"))
            level_item.setBackground(QColor("#e0ffe0"))
        elif level == self.DEBUG:
            level_item.setForeground(QColor("blue"))
            level_item.setBackground(QColor("#e0e0ff"))
        else:  # INFO
            level_item.setForeground(QColor("black"))
            level_item.setBackground(QColor("#f0f0f0"))
        
        self.table.setItem(row, 1, level_item)
        
        # Message column
        message_item = QTableWidgetItem(str(message))
        message_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setItem(row, 2, message_item)
        
        # Auto scroll to bottom
        self.table.scrollToBottom()
    
    def add_info(self, message):
        """Thêm log INFO"""
        self.add_log(message, self.INFO)
    
    def add_warning(self, message):
        """Thêm log WARNING"""
        self.add_log(message, self.WARNING)
    
    def add_error(self, message):
        """Thêm log ERROR"""
        self.add_log(message, self.ERROR)
    
    def add_debug(self, message):
        """Thêm log DEBUG"""
        self.add_log(message, self.DEBUG)
    
    def add_success(self, message):
        """Thêm log SUCCESS"""
        self.add_log(message, self.SUCCESS)
    
    def clear_logs(self):
        """Xóa tất cả logs"""
        self.table.setRowCount(0)
    
    def set_header_text(self, text):
        """Set text cho header label"""
        self.lbl_header.setText(text)

