"""
Path Setup Dialog - Dialog yêu cầu chọn đường dẫn lưu log khi khởi động lần đầu
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QLineEdit, QMessageBox)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os
import sys


class PathSetupDialog(QDialog):
    """Dialog chọn đường dẫn lưu log"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self._init_ui()
    
    def _init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("First Time Setup - Log Path")
        self.setModal(True)
        self.setMinimumSize(200, 100)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Welcome to Regilazi Laser Marking System!")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Please select a directory to store application logs.\n"
            "A subfolder 'RegilaserLog' will be created automatically."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #555; padding: 10px;")
        layout.addWidget(desc)
        
        # Path selection
        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a directory...")
        self.path_input.setReadOnly(True)
        self.path_input.setMinimumHeight(35)
        path_layout.addWidget(self.path_input, stretch=1)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setMinimumHeight(35)
        self.browse_btn.setMinimumWidth(100)
        self.browse_btn.clicked.connect(self._on_browse)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        path_layout.addWidget(self.browse_btn)
        
        layout.addLayout(path_layout)
        
        # Info label
        info_label = QLabel("You can change this path later in Settings > Advanced")
        info_label.setStyleSheet("color: #666; font-size: 10pt; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Use Default")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.clicked.connect(self._on_use_default)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setMinimumHeight(35)
        self.ok_btn.setMinimumWidth(120)
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self._on_ok)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.ok_btn)
        
        layout.addLayout(button_layout)
    
    def _on_browse(self):
        """Xử lý khi click Browse"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Log Directory",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.path_input.setText(directory)
            self.selected_path = directory
            self.ok_btn.setEnabled(True)
    
    def _on_ok(self):
        """Xử lý khi click OK"""
        if not self.selected_path:
            QMessageBox.warning(self, "Warning", "Please select a directory!")
            return

        if not os.access(self.selected_path, os.W_OK):
            QMessageBox.warning(
                self, 
                "Permission Denied", 
                f"Cannot write to directory:\n{self.selected_path}\n\nPlease select another directory."
            )
            return
        self.accept()
    
    def _on_use_default(self):
        reply = QMessageBox.question(
            self,
            "Use Default Path",
            "Use default 'logs' folder in application directory?\n\n"
            "You can change this later in Settings.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.selected_path = "logs"  # Will be handled as default
            self.reject()
    
    def get_selected_path(self):
        """Lấy đường dẫn đã chọn"""
        return self.selected_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = PathSetupDialog()
    dialog.exec()
    sys.exit(app.exec())