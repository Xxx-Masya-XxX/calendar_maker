"""Image preview widget."""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QImage


class ImagePreview(QWidget):
    """Image preview widget with file browser."""

    image_changed = Signal(str)  # file path

    def __init__(self, image_path: str = "", placeholder: str = "No image selected", parent=None):
        """
        Initialize image preview.

        Args:
            image_path: Initial image path
            placeholder: Placeholder text when no image
            parent: Parent widget
        """
        super().__init__(parent)
        self._image_path = image_path
        self._placeholder = placeholder
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Image preview label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 150)
        self.image_label.setMaximumSize(300, 200)
        self.image_label.setStyleSheet(
            "background-color: #f5f5f5; border: 2px dashed #ccc; border-radius: 5px;"
        )
        layout.addWidget(self.image_label)

        # Path label (create before update_image)
        self.path_label = QLabel()
        self.path_label.setStyleSheet("font-family: Consolas; font-size: 10px; color: #666;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)

        # Buttons
        btn_layout = QHBoxLayout()

        self.browse_btn = QPushButton("Select Image...")
        self.browse_btn.clicked.connect(self.browse_image)
        btn_layout.addWidget(self.browse_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_image)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Now update image (all widgets exist)
        self.update_image()

    def browse_image(self):
        """Open image file browser."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if path:
            self.set_image_path(path)

    def clear_image(self):
        """Clear selected image."""
        self._image_path = ""
        self.update_image()
        self.image_changed.emit("")

    def update_image(self):
        """Update image preview."""
        if self._image_path and Path(self._image_path).exists():
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                # Scale to fit
                scaled = pixmap.scaled(
                    self.image_label.size() - QSize(10, 10),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
                self.image_label.setStyleSheet(
                    "background-color: #fff; border: 1px solid #ccc; border-radius: 5px;"
                )
                self.path_label.setText(self._image_path)
                return

        # Show placeholder
        self.image_label.setText(self._placeholder)
        self.image_label.setStyleSheet(
            "background-color: #f5f5f5; border: 2px dashed #ccc; border-radius: 5px;"
        )
        self.path_label.setText(self._image_path if self._image_path else "No image selected")

    def resizeEvent(self, event):
        """Handle resize."""
        super().resizeEvent(event)
        self.update_image()

    def get_image_path(self) -> str:
        """Get current image path."""
        return self._image_path

    def set_image_path(self, path: str):
        """Set image path."""
        self._image_path = path
        self.update_image()
        self.image_changed.emit(path)
