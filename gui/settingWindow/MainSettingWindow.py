from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget, QPushButton, QMessageBox
)

from .GeneralSettingPage import GeneralSettingPage
from .ConnectionSettingPage import ConnectionSettingPage
from .LaserSettingPage import LaserSettingPage
from .AdvancedSettingPage import AdvancedSettingPage


class MainSettingWindow(QDialog):
    """Main Setting window with sidebar navigation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Regilaser Settings")
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.resize(600, 500)
        self._build_ui()

    def _build_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Top horizontal layout for menu and content
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)

        # Left sidebar menu
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(120)
        self.menu_list.addItem("General")
        self.menu_list.addItem("Connection")
        self.menu_list.addItem("Laser")
        self.menu_list.addItem("Advanced")
        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self._on_menu_changed)

        # Right content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #ffffff;
                border: 1px solid #333333;
            }
        """)
        
        # Create pages
        self.general_page = GeneralSettingPage()
        self.connection_page = ConnectionSettingPage()
        self.laser_page = LaserSettingPage()
        self.advanced_page = AdvancedSettingPage()
        self.content_stack.addWidget(self.general_page)
        self.content_stack.addWidget(self.connection_page)
        self.content_stack.addWidget(self.laser_page)
        self.content_stack.addWidget(self.advanced_page)
        # Add to content layout
        content_layout.addWidget(self.menu_list)
        content_layout.addWidget(self.content_stack)

        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        # Add bottom buttons
        self._add_bottom_buttons(main_layout)

    def _add_bottom_buttons(self, main_layout):
        """Add Save/Reset buttons at bottom of dialog"""
        button_row = QHBoxLayout()
        button_row.addStretch(1)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        
        button_row.addWidget(ok_btn)
        button_row.addWidget(cancel_btn)
        button_row.addWidget(apply_btn)
        
        main_layout.addLayout(button_row)

    def _on_menu_changed(self, index):
        """Handle menu selection change"""
        self.content_stack.setCurrentIndex(index)

    def _on_ok(self):
        """Handle save and close button click."""
        QMessageBox.information(self, "Info", "Settings saved and closed successfully.")
        self.close()

    def _on_apply(self):
        """Apply current settings"""
        QMessageBox.information(self, "Info", "Settings applied successfully.")
