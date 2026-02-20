"""Preview label widget for Calendar Config Editor."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy


class PreviewLabel(QLabel):
    """Shows preview pixmap or placeholder."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 160)
        self.setMaximumHeight(320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet(
            "background:#1e1e2e; border:1px solid #3a3a5c; border-radius:6px; color:#888;"
        )
        self.setText("Превью\nнедоступно")

    def set_pixmap(self, pm: QPixmap | None):
        if pm and not pm.isNull():
            self.setPixmap(pm.scaled(self.width() - 8, self.height() - 8,
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setText("")
        else:
            self.setPixmap(QPixmap())
            self.setText("Превью\nнедоступно")
