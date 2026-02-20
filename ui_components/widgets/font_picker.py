"""Font picker widget for Calendar Config Editor."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton, QFileDialog

from ui_components.constants import FONT_PRESETS


class FontPickerWidget(QWidget):
    """Widget for picking font file paths."""
    fontChanged = Signal(str)

    def __init__(self, value: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.addItems(FONT_PRESETS)
        self._combo.setCurrentText(value or "")
        self._browse = QPushButton("…")
        self._browse.setFixedWidth(32)
        self._browse.clicked.connect(self._pick)
        self._combo.currentTextChanged.connect(self.fontChanged)
        lay.addWidget(self._combo, 1)
        lay.addWidget(self._browse)

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать шрифт", "C:/Windows/Fonts", "Fonts (*.ttf *.otf)"
        )
        if path:
            self._combo.setCurrentText(path)

    def value(self) -> str:
        return self._combo.currentText()

    def set_value(self, v: str):
        self._combo.setCurrentText(v or "")
