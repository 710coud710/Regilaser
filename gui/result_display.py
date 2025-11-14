"""
Result Display - Hiển thị kết quả test (Fail/Pass) với nền đỏ/xanh
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ResultDisplay(QWidget):
    """Widget hiển thị kết quả test"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Interval label
        self.lbl_interval = QLabel("Interval:3320s")
        self.lbl_interval.setAlignment(Qt.AlignCenter)
        self.lbl_interval.setStyleSheet("""
            background-color: white;
            border: 2px solid black;
            padding: 5px;
            font-size: 14pt;
            font-weight: bold;
        """)
        self.lbl_interval.setMaximumHeight(40)
        layout.addWidget(self.lbl_interval)
        
        # Mystery label (??????)
        self.lbl_mystery = QLabel("??????")
        self.lbl_mystery.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_mystery.setStyleSheet("""
            background-color: red;
            color: white;
            padding: 5px 10px;
            font-weight: bold;
        """)
        self.lbl_mystery.setMaximumHeight(30)
        layout.addWidget(self.lbl_mystery)
        
        # Main result label (Fail/Pass)
        self.lbl_result = QLabel("Fail")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(72)
        font.setBold(True)
        self.lbl_result.setFont(font)
        self.lbl_result.setStyleSheet("""
            background-color: red;
            color: black;
            border: none;
        """)
        layout.addWidget(self.lbl_result, stretch=1)
        
        self.setMinimumHeight(300)
    
    def show_fail(self, message="Fail"):
        """Hiển thị trạng thái Fail"""
        self.lbl_result.setText(message)
        self.lbl_result.setStyleSheet("""
            background-color: red;
            color: black;
            border: none;
        """)
    
    def show_pass(self, message="Pass"):
        """Hiển thị trạng thái Pass"""
        self.lbl_result.setText(message)
        self.lbl_result.setStyleSheet("""
            background-color: green;
            color: white;
            border: none;
        """)
    
    def set_interval(self, interval_text):
        """Set interval text"""
        self.lbl_interval.setText(f"Interval:{interval_text}")
    
    def set_mystery_text(self, text):
        """Set mystery label text"""
        self.lbl_mystery.setText(text)

