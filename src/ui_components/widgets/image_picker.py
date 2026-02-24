"""Image picker widget for Calendar Config Editor."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


class ImagePickerWidget(QWidget):
    """Widget for picking image file paths."""
    pathChanged = Signal(str)

    def __init__(self, value: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._edit = QLineEdit(value or "")
        self._edit.setPlaceholderText("Путь к изображению…")
        self._btn = QPushButton("…")
        self._btn.setFixedWidth(32)
        self._btn.clicked.connect(self._pick)
        self._edit.textChanged.connect(self.pathChanged)
        lay.addWidget(self._edit)
        lay.addWidget(self._btn)

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self._edit.setText(path)

    def value(self) -> str:
        return self._edit.text()

    def set_value(self, v: str):
        self._edit.setText(v or "")
