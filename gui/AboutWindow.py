from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout


class AboutWindow(QDialog):
    """Simple setting window placeholder."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.about_UI()

    def about_UI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        about_label = QLabel(
            "<h2>About</h2>"
            "<p><b>Created by:</b> Ryder</p>"
            "<p><b>Team:</b> SWE</p>"
        )
        about_label.setTextFormat(Qt.RichText)
        about_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(about_label)

        button_row_widget = QWidget()
        button_row = QHBoxLayout(button_row_widget)
        button_row.addStretch(1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)

        layout.addWidget(button_row_widget)
