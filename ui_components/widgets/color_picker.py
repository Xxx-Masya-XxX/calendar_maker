"""Color picker widget for Calendar Config Editor."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog

from ui_components.helpers import color_from_list, list_from_color, color_swatch


class ColorPickerWidget(QWidget):
    """Widget for picking RGB colors."""
    colorChanged = Signal(list)

    def __init__(self, value: list = None, parent=None):
        super().__init__(parent)
        self._color = color_from_list(value or [0, 0, 0])
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._swatch = QLabel()
        self._swatch.setFixedSize(22, 22)
        self._btn = QPushButton("Выбрать цвет")
        self._btn.setFixedHeight(24)
        self._val_label = QLabel()
        self._btn.clicked.connect(self._pick)
        lay.addWidget(self._swatch)
        lay.addWidget(self._btn)
        lay.addWidget(self._val_label)
        lay.addStretch()
        self._refresh()

    def _refresh(self):
        self._swatch.setPixmap(color_swatch(self._color))
        rgb = list_from_color(self._color)
        self._val_label.setText(f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")

    def _pick(self):
        c = QColorDialog.getColor(self._color, self, "Выбрать цвет")
        if c.isValid():
            self._color = c
            self._refresh()
            self.colorChanged.emit(list_from_color(self._color))

    def value(self) -> list:
        return list_from_color(self._color)

    def set_value(self, lst: list):
        self._color = color_from_list(lst)
        self._refresh()
