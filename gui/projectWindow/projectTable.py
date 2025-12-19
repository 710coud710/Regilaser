from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QLabel, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from gui.projectWindow.projectEditDialog import ProjectEditDialog
from utils.AppPathService import getAppDirectory
import os
class ProjectTable(QDialog):
    # Signals emitted for different actions
    project_selected = Signal(str)  # project_name
    project_edit = Signal(dict)  # project_data (full row data)
    project_delete = Signal(str)  # project_name
    project_add = Signal(dict)  # project_data (new project)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()


    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title bar with label and add button
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label/title for the table
        title_label = QLabel("Project Management") 
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # Add spacer to push button to the right
        title_layout.addStretch()
        
        # Add Project button
        add_btn = QPushButton()
        add_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/add.svg")))
        add_btn.setToolTip("Add New Project")
        add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                padding: 8px;
                border-radius: 5px;
                max-width: 35px;
                max-height: 35px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        add_btn.clicked.connect(self.onAddClicked)
        title_layout.addWidget(add_btn)
        layout.addLayout(title_layout)
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #CCCCCC; margin-bottom: 2px; margin-top: 2px;")
        layout.addWidget(line)

        # Table 7 columns: Project_Name, LM_Script_Name, Panel_Num, PSN_PRE, SFIS Format, LM Mode, Actions
        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels([
            "Project Name", "LM Script", "Panel Num", "PSN PRE", "SFIS Format", "LM Mode", "Actions"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # # Make column headers bold
        # font = self.table.horizontalHeader().font()
        # font.setBold(True)
        # self.table.horizontalHeader().setFont(font)

        # Add line under the horizontal header (by using stylesheet)
        self.table.setStyleSheet("""
            QHeaderView::section {
                border-bottom: 1px solid black;
                font-weight: bold;
                font-size: 12px;
                font-weight: bold;
            }
            QHeaderView::section:selected {
                background-color: lightblue;
            }
        """)

        layout.addWidget(self.table)

    def set_data(self, data):
        """Set data to the table and store it for later use"""
        self.project_data = data  # Store data for reference
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # Set text items for each column
            project_item = QTableWidgetItem(str(item.get("Project_Name", "")))
            script_item = QTableWidgetItem(str(item.get("LM_Script_Name", "")))
            panel_num_item = QTableWidgetItem(str(item.get("Panel_Num", "")))
            psn_pre_item = QTableWidgetItem(str(item.get("PSN_PRE", "")))
            sfis_format_item = QTableWidgetItem(str(item.get("SFIS_format", "")))
            lm_mode_item = QTableWidgetItem(str(item.get("LM_mode", "")))

            # Center align all items
            project_item.setTextAlignment(Qt.AlignCenter)
            script_item.setTextAlignment(Qt.AlignCenter)
            panel_num_item.setTextAlignment(Qt.AlignCenter)
            psn_pre_item.setTextAlignment(Qt.AlignCenter)
            sfis_format_item.setTextAlignment(Qt.AlignCenter)
            lm_mode_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row, 0, project_item)
            self.table.setItem(row, 1, script_item)
            self.table.setItem(row, 2, panel_num_item)
            self.table.setItem(row, 3, psn_pre_item)
            self.table.setItem(row, 4, sfis_format_item)
            self.table.setItem(row, 5, lm_mode_item)
            
            # Action buttons: Select, Fix, Delete
            action_widget = self.ActionButtonProjectTable(row)
            self.table.setCellWidget(row, 6, action_widget)
    
    def ActionButtonProjectTable(self, row):
        """Create action buttons widget for a row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Select button
        select_btn = QPushButton()
        select_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/select.svg")))
        select_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 10px;
                max-width: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: lightgreen;
            }
        """)
        select_btn.clicked.connect(lambda checked, idx=row: self.onSelectClicked(idx))
        select_btn.enterEvent = lambda event: select_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/select-hover.svg")))
        select_btn.leaveEvent = lambda event: select_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/select.svg")))
        
        # Fix/Edit button
        fix_btn = QPushButton()
        fix_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/edit.svg")))
        fix_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        fix_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 10px;
                max-width: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: lightskyblue;
            }
        """)
        fix_btn.clicked.connect(lambda checked, idx=row: self.onFixClicked(idx))
        fix_btn.enterEvent = lambda event: fix_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/edit-hover.svg")))
        fix_btn.leaveEvent = lambda event: fix_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/edit.svg")))

        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/delete.svg")))
        delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 10px;
                max-width: 30px;
                max-height: 30px;
            }
            QPushButton:hover {
                background-color: lightcoral;
            }
        """)
        # Use event to change icon color on hover (assuming SVG is mono and colored)
        delete_btn.enterEvent = lambda event: delete_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/delete-hover.svg")))
        delete_btn.leaveEvent = lambda event: delete_btn.setIcon(QIcon(os.path.join(getAppDirectory(), "assets/delete.svg")))
        delete_btn.clicked.connect(lambda checked, idx=row: self.onDeleteClicked(idx))
        
        layout.addWidget(select_btn)
        layout.addWidget(fix_btn)
        layout.addWidget(delete_btn)
        
        return widget

    def onSelectClicked(self, row):
        try:
            project_name_item = self.table.item(row, 0)
            if project_name_item:
                project_name = project_name_item.text()
                print(f"Selected project: {project_name}")
                # Emit signal to notify the presenter
                reply = QMessageBox.question(
                    self,
                    "Confirm Select",
                    f"Are you sure you want to select project '{project_name}'?\n\n"
                    f"The application will restart to apply changes.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    self.project_selected.emit(project_name)
                    self.accept()
        except Exception as e:
            print(f"Error selecting project: {str(e)}")
    
    def onFixClicked(self, row):
        """Handle fix/edit button click for the given row"""
        try:
            # Get project data from the stored data
            if hasattr(self, 'project_data') and row < len(self.project_data):
                project_data = self.project_data[row]
                print(f"Fix project: {project_data.get('Project_Name', '')}")
                
                # Open edit dialog
                edit_dialog = ProjectEditDialog(project_data, self)
                edit_dialog.project_saved.connect(self._on_project_edited)
                edit_dialog.exec()
        except Exception as e:
            print(f"Error fixing project: {str(e)}")
    
    def _on_project_edited(self, updated_data):
        """Handle when project data is edited"""
        try:
            # Emit signal with updated project data
            self.project_edit.emit(updated_data)
        except Exception as e:
            print(f"Error handling edited project: {str(e)}")
    
    def onDeleteClicked(self, row):
        """Handle delete button click for the given row"""
        try:
            # Get project name from the selected row
            project_name_item = self.table.item(row, 0)
            if project_name_item:
                project_name = project_name_item.text()
                
                # Confirm deletion
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete project '{project_name}'?\n\n"
                    f"This action cannot be undone.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    print(f"Delete project: {project_name}")
                    # Emit signal to notify the presenter
                    self.project_delete.emit(project_name)
        except Exception as e:
            print(f"Error deleting project: {str(e)}")
    
    def onAddClicked(self):
        """Handle add new project button click"""
        try:
            print("Add new project clicked")
            
            # Create empty project data template
            new_project_data = {
                "Project_Name": "",
                "LM_Script_Name": 1,
                "Panel_Num": 10,
                "PSN_PRE": "",
                "sfis_format": 1,
                "lm_mode": 1
            }
            
            # Open edit dialog for new project
            edit_dialog = ProjectEditDialog(new_project_data, self)
            edit_dialog.setWindowTitle("Add New Project")
            edit_dialog.project_saved.connect(self._on_project_added)
            edit_dialog.exec()
            
        except Exception as e:
            print(f"Error adding project: {str(e)}")
    
    def _on_project_added(self, new_project_data):
        """Handle when new project is added"""
        try:
            # Emit signal with new project data
            self.project_add.emit(new_project_data)
        except Exception as e:
            print(f"Error handling added project: {str(e)}")
        
