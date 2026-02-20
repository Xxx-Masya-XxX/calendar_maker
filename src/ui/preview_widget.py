"""Preview widget for calendar."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class PreviewWidget(QWidget):
    """Widget for displaying calendar preview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 300)
        self.image_label.setText("Нет изображения")

        layout.addWidget(self.image_label)

    def set_image(self, pixmap: QPixmap):
        """Set preview image."""
        if pixmap and not pixmap.isNull():
            # Scale to fit while keeping aspect ratio
            label_size = self.image_label.size()
            scaled = pixmap.scaled(
                label_size.width() - 20,
                label_size.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")

    def clear(self):
        """Clear preview."""
        self.image_label.clear()
        self.image_label.setText("Нет изображения")
