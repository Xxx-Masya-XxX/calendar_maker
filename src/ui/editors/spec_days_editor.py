"""Special days editor with improved UI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QLabel, QLineEdit, QGroupBox,
    QFormLayout
)
from PySide6.QtCore import Signal

from src.ui.widgets.date_picker import DatePicker
from src.ui.widgets.color_picker import ColorPicker
from src.ui.widgets.image_preview import ImagePreview


class SpecDayEditor(QWidget):
    """Editor for a single special day."""

    changed = Signal()
    delete_requested = Signal(int)  # index

    def __init__(self, spec_day: dict = None, index: int = 0, parent=None):
        super().__init__(parent)
        self.spec_day = spec_day or {}
        self.index = index
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Group box with header
        self.group = QGroupBox(f"Праздник #{self.index + 1}")
        self.group.setCheckable(True)
        self.group.setChecked(True)
        self.group.toggled.connect(self.on_change)
        
        form = QFormLayout()
        form.setSpacing(5)

        # Date picker
        date = self.spec_day.get('date', '01.01')
        self.date_picker = DatePicker(date)
        self.date_picker.date_changed.connect(self.on_change)
        form.addRow("Дата:", self.date_picker)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: День рождения")
        self.name_edit.setText(self.spec_day.get('name', ''))
        self.name_edit.textChanged.connect(self.on_change)
        form.addRow("Название:", self.name_edit)

        # Description
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Описание (необязательно)")
        self.desc_edit.setText(self.spec_day.get('desc', ''))
        self.desc_edit.textChanged.connect(self.on_change)
        form.addRow("Описание:", self.desc_edit)

        # Text color
        color = self.spec_day.get('text_color', [255, 0, 0])
        self.color_picker = ColorPicker(tuple(color))
        self.color_picker.color_changed.connect(self.on_change)
        form.addRow("Цвет текста:", self.color_picker)

        # Background image
        bg_path = self.spec_day.get('background', '')
        self.bg_preview = ImagePreview(bg_path, "Нет фона")
        self.bg_preview.image_changed.connect(self.on_change)
        form.addRow("Фон:", self.bg_preview)

        self.group.setLayout(form)
        layout.addWidget(self.group)

        # Delete button
        delete_btn = QPushButton("Удалить праздник")
        delete_btn.clicked.connect(self.delete_clicked)
        layout.addWidget(delete_btn)

    def on_change(self):
        self.changed.emit()

    def delete_clicked(self):
        """Emit signal for deletion."""
        self.delete_requested.emit(self.index)

    def get_spec_day(self) -> dict:
        return {
            'date': self.date_picker.get_date(),
            'name': self.name_edit.text(),
            'desc': self.desc_edit.text(),
            'text_color': list(self.color_picker.get_color()),
            'background': self.bg_preview.get_image_path(),
        }

    def set_spec_day(self, spec_day: dict):
        self.spec_day = spec_day
        self.date_picker.set_date(spec_day.get('date', '01.01'))
        self.name_edit.setText(spec_day.get('name', ''))
        self.desc_edit.setText(spec_day.get('desc', ''))
        self.color_picker.set_color(tuple(spec_day.get('text_color', [255, 0, 0])))
        self.bg_preview.set_image_path(spec_day.get('background', ''))


class SpecDaysEditor(QWidget):
    """Editor for special days list."""

    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spec_days = []
        self.editors = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Специальные дни (праздники, события)")
        title.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(title)

        add_btn = QPushButton("Добавить праздник")
        add_btn.clicked.connect(self.add_day)
        header_layout.addWidget(add_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Info label
        info = QLabel(
            "Специальные дни используются для особых дат (дни рождения, праздники).\n"
            "Для каждого специального дня можно настроить фон и цвет текста."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Scroll area for special day editors
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        # Container for editors
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(10)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def add_day(self, spec_day: dict = None):
        """Add a new special day."""
        editor = SpecDayEditor(spec_day or {'date': '01.01', 'name': '', 'desc': '', 'background': ''}, len(self.editors))
        editor.changed.connect(self.on_change)
        editor.delete_requested.connect(self.remove_day)
        self.editors.append(editor)
        self.container_layout.addWidget(editor)
        self.changed.emit()

    def remove_day(self, index: int):
        """Remove a special day at index."""
        if 0 <= index < len(self.editors):
            editor = self.editors.pop(index)
            self.container_layout.removeWidget(editor)
            editor.deleteLater()
            self.reindex_editors()
            self.changed.emit()

    def reindex_editors(self):
        """Update editor indices and refresh UI."""
        for i, editor in enumerate(self.editors):
            editor.index = i
            editor.group.setTitle(f"🎉 Праздник #{i + 1}")

    def on_change(self):
        # Check if any editor was marked for deletion
        self.changed.emit()

    def get_spec_days(self) -> list:
        """Get all special days as list of dicts."""
        return [
            editor.get_spec_day() 
            for editor in self.editors 
            if editor.date_picker.get_date()
        ]

    def set_spec_days(self, spec_days: list):
        """Set special days from list of dicts."""
        self.spec_days = spec_days or []
        
        # Clear existing editors
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.editors = []

        # Create editors for each special day
        for i, spec_day in enumerate(self.spec_days):
            editor = SpecDayEditor(spec_day, i)
            editor.changed.connect(self.on_change)
            self.editors.append(editor)
            self.container_layout.addWidget(editor)

        self.container_layout.addStretch()
