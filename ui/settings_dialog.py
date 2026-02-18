from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QComboBox, QPushButton, QColorDialog, QLabel, QHBoxLayout, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class AddHolidayDialog(QDialog):
    """Dialog for adding a holiday."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Holiday / Добавить праздник")
        self.holiday_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Holiday name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Month
        self.month_combo = QComboBox()
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_combo.addItems(months)
        form_layout.addRow("Month:", self.month_combo)
        
        # Day
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(1)
        form_layout.addRow("Day:", self.day_spin)
        
        # Color
        self.color_label = QLabel()
        self.color_label.setFixedSize(50, 25)
        self.color_label.setStyleSheet("background-color: #FF0000;")
        self.color = "#FF0000"
        
        color_btn = QPushButton("Choose Color")
        color_btn.clicked.connect(self.choose_color)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(color_btn)
        
        form_layout.addRow("Color:", color_layout)
        
        # Is recurring
        self.recurring_check = QCheckBox("Recurring (every year)")
        self.recurring_check.setChecked(True)
        form_layout.addRow("", self.recurring_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.color_label.setStyleSheet(f"background-color: {self.color};")
    
    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text(),
            "month": self.month_combo.currentIndex() + 1,
            "day": self.day_spin.value(),
            "color": self.color,
            "is_recurring": self.recurring_check.isChecked(),
        }


class AddSpecialDayDialog(QDialog):
    """Dialog for adding a special day."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Special Day / Добавить особый день")
        self.special_day_data = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Special day name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        self.desc_edit.setPlaceholderText("Description (optional)")
        form_layout.addRow("Description:", self.desc_edit)
        
        # Month
        self.month_combo = QComboBox()
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_combo.addItems(months)
        form_layout.addRow("Month:", self.month_combo)
        
        # Day
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(1)
        form_layout.addRow("Day:", self.day_spin)
        
        # Color
        self.color_label = QLabel()
        self.color_label.setFixedSize(50, 25)
        self.color_label.setStyleSheet("background-color: #0000FF;")
        self.color = "#0000FF"
        
        color_btn = QPushButton("Choose Color")
        color_btn.clicked.connect(self.choose_color)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(color_btn)
        
        form_layout.addRow("Color:", color_layout)
        
        # Is recurring
        self.recurring_check = QCheckBox("Recurring (every year)")
        self.recurring_check.setChecked(True)
        form_layout.addRow("", self.recurring_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.color_label.setStyleSheet(f"background-color: {self.color};")
    
    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text(),
            "description": self.desc_edit.toPlainText(),
            "month": self.month_combo.currentIndex() + 1,
            "day": self.day_spin.value(),
            "color": self.color,
            "is_recurring": self.recurring_check.isChecked(),
        }
