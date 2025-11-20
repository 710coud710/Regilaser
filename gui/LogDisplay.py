"""
Log Display - Hiển thị log dạng text có thể copy và cuộn
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
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
        
        # Text area for logs
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_view.setMaximumBlockCount(2000)  # Giữ lại 2000 dòng gần nhất

        font = QFont("Consolas", 10)
        self.log_view.setFont(font)

        self.log_view.setStyleSheet("""
            QPlainTextEdit {
                border: 1px solid grey;
                background-color: #f0f0f0;
                color: black;
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.log_view, stretch=1)
        
        self.setMinimumHeight(300)

        # thử mẫu vài giá trị log
        sample_logs = [
            ("System initialized successfully", self.INFO),
            ("Application version: 1.0.0", self.INFO),
            ("Device detected: ARDUINO UNO", self.INFO),
            ("Port COM3 opened", self.INFO),
            ("Loading configuration...", self.INFO),
            ("Configuration loaded", self.SUCCESS),
            ("Checking connection to PLC...", self.INFO),
            ("PLC responded successfully", self.SUCCESS),
            ("User pressed Start", self.DEBUG),
            ("Sending initialization command to device", self.DEBUG),
            ("Device ACK received", self.SUCCESS),
            ("Sensor 1 value: 23.1", self.DEBUG),
            ("Sensor 2 disconnected", self.WARNING),
            ("Timeout waiting for response", self.WARNING),
            ("Received unexpected value from device", self.WARNING),
            ("Data packet malformed", self.ERROR),
            ("Test step #3 failed", self.ERROR),
            ("Test step #4 passed", self.SUCCESS),
            ("Test complete", self.INFO),
            ("All tests passed", self.SUCCESS),
        ]       
        for msg, lvl in sample_logs:
            self.addLog(msg, lvl)
    
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

