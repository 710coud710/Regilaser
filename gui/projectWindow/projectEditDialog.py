"""
Project Edit Dialog - Dialog for editing project information
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QLabel, QPushButton, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal


class ProjectEditDialog(QDialog):
    """Dialog for editing project data"""
    
    # Signal emitted when project is saved
    project_saved = Signal(dict)  # Updated project data
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data.copy()  # Store a copy
        self.original_name = project_data.get("Project_Name", "")
        self._init_ui()
        self._populate_data()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Edit Project")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Edit Project Information")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Project Name
        self.project_name_input = QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_input)
        
        # LM Script Name
        self.lm_script_input = QLineEdit()
        form_layout.addRow("LM Script:", self.lm_script_input)
        
        # LM Num
        self.panel_num_input = QLineEdit()
        form_layout.addRow("Panel Num:", self.panel_num_input)
        
        # PSN PRE
        self.psn_pre_input = QLineEdit()
        form_layout.addRow("PSN PRE:", self.psn_pre_input)
        
        # SFIS Format
        self.sfis_format_input = QComboBox()
        self.sfis_format_input.addItems(["1", "2"])
        form_layout.addRow("SFIS Format:", self.sfis_format_input)
        
        # LM Mode
        self.lm_mode_input = QComboBox()
        self.lm_mode_input.addItems(["1", "2"])
        form_layout.addRow("LM Mode:", self.lm_mode_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.on_save_clicked)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_data(self):
        """Populate form with project data"""
        self.project_name_input.setText(self.project_data.get("Project_Name", ""))
        self.lm_script_input.setText(str(self.project_data.get("LM_Script_Name", 0)))
        self.panel_num_input.setText(str(self.project_data.get("Panel_Num", 1)))
        self.psn_pre_input.setText(self.project_data.get("PSN_PRE", ""))
        self.sfis_format_input.setCurrentText(str(self.project_data.get("SFIS_format", 1)))
        self.lm_mode_input.setCurrentText(str(self.project_data.get("LM_mode", 1)))
    
    def on_save_clicked(self):
        """Handle save button click"""
        try:
            # Validate inputs
            project_name = self.project_name_input.text().strip()
            if not project_name:
                QMessageBox.warning(self, "Validation Error", "Project Name cannot be empty!")
                return
            
            psn_pre = self.psn_pre_input.text().strip()
            if not psn_pre:
                QMessageBox.warning(self, "Validation Error", "PSN PRE cannot be empty!")
                return
            
            # Update project data
            self.project_data["Project_Name"] = project_name
            self.project_data["LM_Script_Name"] = int(self.lm_script_input.text())
            self.project_data["LM_Num"] = int(self.lm_num_input.text())
            self.project_data["PSN_PRE"] = psn_pre
            self.project_data["SFIS_format"] = self.sfis_format_input.currentText()
            self.project_data["LM_mode"] = self.lm_mode_input.currentText()
            
            # Emit signal with updated data
            self.project_saved.emit(self.project_data)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
    
    def get_project_data(self):
        """Get updated project data"""
        return self.project_data

