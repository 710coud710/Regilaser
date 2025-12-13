from PySide6.QtWidgets import (
    QDialog,QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Signal

class ProjectTable(QDialog):
    # Signal emitted when a project is selected
    project_selected = Signal(str)  # project_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()


    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Label/title for the table
        title_label = QLabel("Project Table")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Table 7 columns: Project_Name, LM_Script_Name, LM_Num, PSN_PRE, SFIS Format, LM Mode, Action
        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels([
            "Project Name", "LM Script", "LM Num", "PSN PRE","SFIS Format", "LM Mode", "Action"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def set_data(self, data):
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            project_item = QTableWidgetItem(str(item.get("Project_Name", "")))
            script_item = QTableWidgetItem(str(item.get("LM_Script_Name", "")))
            lm_num_item = QTableWidgetItem(str(item.get("LM_Num", "")))
            psn_pre_item = QTableWidgetItem(str(item.get("PSN_PRE", "")))
            sfis_format_item = QTableWidgetItem(str(item.get("SFIS_format", "")))
            lm_mode_item = QTableWidgetItem(str(item.get("LM_mode", "")))

            self.table.setItem(row, 0, project_item)
            self.table.setItem(row, 1, script_item)
            self.table.setItem(row, 2, lm_num_item)
            self.table.setItem(row, 3, psn_pre_item)
            self.table.setItem(row, 4, sfis_format_item)
            self.table.setItem(row, 5, lm_mode_item)
            # Action button: Select this project
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda checked, idx=row: self.on_select_clicked(idx))
            self.table.setCellWidget(row, 6, action_btn)

    def on_select_clicked(self, row):
        """Handle select button click for the given row"""
        try:
            # Get project name from the selected row
            project_name_item = self.table.item(row, 0)
            if project_name_item:
                project_name = project_name_item.text()
                print(f"Selected project: {project_name}")
                # Emit signal to notify the presenter
                self.project_selected.emit(project_name)
                self.accept()  # Close dialog after selection
        except Exception as e:
            print(f"Error selecting project: {str(e)}")

    # def on_action_clicked(self, row):
    #     # Handle action button click for the given row
    #     pass
        
