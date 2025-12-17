"""
Log Display - Hiển thị log dạng text có thể copy và cuộn
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit, QHBoxLayout
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont


class LogDisplay(QWidget):
    """Widget hiển thị log dạng text"""
    
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
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid grey;
            }
            QLabel {
                color: black;
                padding: 3px 5px;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid grey;
                background-color: white;
            }
            QPlainTextEdit {
                background-color: white;
                border: 1px solid grey;
                color: black;
                padding: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f4f6fa;
                width: 10px;
                margin: 2px 0 2px 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #B0BEC5, stop:1 #78909C
                );
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover,
            QScrollBar::handle:vertical:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #616161, stop:1 #37474F
                );
            }
            /* Horizontal modern scrollbar */
            QScrollBar:horizontal {
                border: none;
                background: #f4f6fa;
                height: 10px;
                margin: 0px 2px 0px 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #B0BEC5, stop:1 #78909C
                );
                min-width: 24px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover,
            QScrollBar::handle:horizontal:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #616161, stop:1 #37474F
                );
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
         """)
        # Header label
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)
        self.lbl_header = QLabel("History:")
        self.lbl_header.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        header_layout.addWidget(self.lbl_header)
        header_layout.addStretch(10)
        layout.addLayout(header_layout)
        
        # Text area for logs
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_view.setMaximumBlockCount(3000)  # Giữ lại 2000 dòng gần nhất

        font = QFont("Consolas", 10)
        self.log_view.setFont(font)        
        layout.addWidget(self.log_view, stretch=1)
        
        self.setMinimumHeight(300)
    
    def formatEntry(self, message, level):
        timestamp = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")
        return f"[{timestamp}] [{level:>7}]  {message}"

    def addLog(self, message, level=INFO):
        """Thêm một dòng log vào text area"""
        entry = self.formatEntry(message, level)
        self.log_view.appendPlainText(entry)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
    
    def addInfo(self, message):
        """Thêm log INFO"""
        self.addLog(message, self.INFO)
    
    def addWarning(self, message):
        """Thêm log WARNING"""
        self.addLog(message, self.WARNING)
    
    def addError(self, message):
        """Thêm log ERROR"""
        self.addLog(message, self.ERROR)
    
    def addDebug(self, message):
        """Thêm log DEBUG"""
        self.addLog(message, self.DEBUG)
    
    def addSuccess(self, message):
        """Thêm log SUCCESS"""
        self.addLog(message, self.SUCCESS)
    
    def clearLogs(self):
        """Xóa tất cả logs"""
        self.log_view.clear()
    
    def setHeaderText(self, text):
        """Set text cho header label"""
        self.lbl_header.setText(text)

