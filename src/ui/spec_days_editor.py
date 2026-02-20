"""Special days editor with visual controls."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QScrollArea, QFrame, QSplitter, QLabel,QLineEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from src.ui.widgets.date_picker import DatePicker
from src.ui.widgets.image_preview import ImagePreview


class SpecDayEditor(QWidget):
    """Editor for a single special day."""

    changed = Signal()

    def __init__(self, spec_day: dict = None, parent=None):
        super().__init__(parent)
        self.spec_day = spec_day or {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box
        group = QGroupBox("Special Day")
        group_layout = QVBoxLayout()

        # Date picker
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_picker = DatePicker(self.spec_day.get('date', ''))
        self.date_picker.date_changed.connect(self.on_change)
        date_layout.addWidget(self.date_picker)
        date_layout.addStretch()
        group_layout.addLayout(date_layout)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter name (e.g., Birthday)")
        self.name_edit.setText(self.spec_day.get('name', ''))
        self.name_edit.textChanged.connect(self.on_change)
        group_layout.addRow("Name:", self.name_edit) if hasattr(group_layout, 'addRow') else group_layout.addWidget(QLabel("Name:"))
        group_layout.addWidget(self.name_edit)

        # Description
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Enter description (optional)")
        self.desc_edit.setText(self.spec_day.get('desc', ''))
        self.desc_edit.textChanged.connect(self.on_change)
        group_layout.addWidget(QLabel("Description:"))
        group_layout.addWidget(self.desc_edit)

        # Background image
        group_layout.addWidget(QLabel("Background Image:"))
        self.image_preview = ImagePreview(
            self.spec_day.get('background', ''),
            "No background image"
        )
        self.image_preview.image_changed.connect(self.on_change)
        group_layout.addWidget(self.image_preview)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def on_change(self):
        self.changed.emit()

    def get_spec_day(self) -> dict:
        return {
            'date': self.date_picker.get_date(),
            'name': self.name_edit.text(),
            'desc': self.desc_edit.text(),
            'background': self.image_preview.get_image_path()
        }

    def set_spec_day(self, spec_day: dict):
        self.spec_day = spec_day
        self.date_picker.set_date(spec_day.get('date', ''))
        self.name_edit.setText(spec_day.get('name', ''))
        self.desc_edit.setText(spec_day.get('desc', ''))
        self.image_preview.set_image_path(spec_day.get('background', ''))


class SpecDaysEditor(QWidget):
    """Editor for special days list with visual controls."""

    changed = Signal()

    def __init__(self, spec_days: list, parent=None):
        super().__init__(parent)
        self.spec_days = spec_days or []
        self.editors = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Special Days:"))
        
        add_btn = QPushButton("Add Special Day")
        add_btn.clicked.connect(self.add_day)
        header_layout.addWidget(add_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Scroll area for special day editors
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        # Container for editors
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(10)

        # Load existing special days
        self.load_spec_days()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def load_spec_days(self):
        """Load special days into editors."""
        # Clear existing editors
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.editors = []

        # Create editors for each special day
        for spec_day in self.spec_days:
            editor = SpecDayEditor(spec_day)
            editor.changed.connect(self.on_change)
            self.editors.append(editor)
            self.container_layout.addWidget(editor)

        self.container_layout.addStretch()

    def add_day(self):
        """Add a new special day."""
        editor = SpecDayEditor({'date': '01.01', 'name': '', 'desc': '', 'background': ''})
        editor.changed.connect(self.on_change)
        self.editors.append(editor)
        self.container_layout.insertWidget(self.container_layout.count() - 1, editor)
        self.changed.emit()

    def remove_day(self, index: int):
        """Remove a special day at index."""
        if 0 <= index < len(self.editors):
            editor = self.editors.pop(index)
            self.container_layout.removeWidget(editor)
            editor.deleteLater()
            self.changed.emit()

    def on_change(self):
        self.changed.emit()

    def get_spec_days(self) -> list:
        """Get all special days as list of dicts."""
        return [editor.get_spec_day() for editor in self.editors if editor.date_picker.get_date()]

    def set_spec_days(self, spec_days: list):
        """Set special days from list of dicts."""
        self.spec_days = spec_days
        self.load_spec_days()
