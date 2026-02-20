"""Date picker widget for special days."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QSpinBox, QComboBox, QLabel
from PySide6.QtCore import Signal


class DatePicker(QWidget):
    """Date picker widget with day and month selectors."""

    date_changed = Signal(str)  # DD.MM format

    # Russian month names
    MONTHS = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    def __init__(self, initial_date: str = "", parent=None):
        """
        Initialize date picker.

        Args:
            initial_date: Initial date in DD.MM format
            parent: Parent widget
        """
        super().__init__(parent)
        self._day = 1
        self._month = 1
        self.setup_ui()
        
        if initial_date:
            self.set_date(initial_date)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Day selector
        layout.addWidget(QLabel("Day:"))
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(self._day)
        self.day_spin.setFixedWidth(60)
        self.day_spin.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.day_spin)

        # Month selector
        layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        self.month_combo.addItems(self.MONTHS)
        self.month_combo.setCurrentIndex(self._month - 1)
        self.month_combo.currentIndexChanged.connect(self.on_value_changed)
        layout.addWidget(self.month_combo)

        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("font-family: Consolas; font-size: 12px; padding: 5px;")
        self.update_preview()
        layout.addWidget(self.preview_label)

    def on_value_changed(self):
        """Handle value change."""
        self._day = self.day_spin.value()
        self._month = self.month_combo.currentIndex() + 1
        self.update_preview()
        self.date_changed.emit(self.get_date())

    def update_preview(self):
        """Update date preview label."""
        date_str = self.get_date()
        self.preview_label.setText(f"→ {date_str}")

    def get_date(self) -> str:
        """Get date as DD.MM string."""
        return f"{self._day:02d}.{self._month:02d}"

    def set_date(self, date_str: str):
        """Set date from DD.MM string."""
        try:
            parts = date_str.strip().split('.')
            if len(parts) == 2:
                day = int(parts[0])
                month = int(parts[1])
                
                if 1 <= day <= 31 and 1 <= month <= 12:
                    self._day = day
                    self._month = month
                    self.day_spin.setValue(day)
                    self.month_combo.setCurrentIndex(month - 1)
                    self.update_preview()
        except (ValueError, IndexError):
            pass

    def get_day(self) -> int:
        """Get day."""
        return self._day

    def get_month(self) -> int:
        """Get month."""
        return self._month
