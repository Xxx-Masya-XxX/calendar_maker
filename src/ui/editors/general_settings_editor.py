"""General settings editor."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Signal


class GeneralSettingsEditor(QWidget):
    """Editor for general application settings."""

    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Info label
        info = QLabel(
            "⚙️ Общие настройки календаря.\n"
            "Здесь можно настроить параметры по умолчанию для дней недели, месяцев и дней."
        )
        info.setStyleSheet("color: #666; padding: 10px; background: #f5f5f5; border-radius: 4px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Placeholder for future general settings
        # (currently most settings are in specific sections)
        layout.addStretch()

    def get_config(self) -> dict:
        """Get general settings (currently empty)."""
        return {}

    def set_config(self, config: dict):
        """Set general settings."""
        pass
