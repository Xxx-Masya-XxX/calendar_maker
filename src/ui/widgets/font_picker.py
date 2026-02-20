"""Font picker widget with preview."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QLineEdit, QSpinBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QFontDatabase


class FontPicker(QWidget):
    """Font picker widget with file browser and preview."""

    font_changed = Signal(str, int)  # font_path, size

    def __init__(self, font_path: str = "", font_size: int = 48, parent=None):
        """
        Initialize font picker.

        Args:
            font_path: Initial font file path
            font_size: Initial font size
            parent: Parent widget
        """
        super().__init__(parent)
        self._font_path = font_path
        self._font_size = font_size
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Font Settings")
        form = QFormLayout()

        # Font file path
        self.font_edit = QLineEdit()
        self.font_edit.setText(self._font_path)
        self.font_edit.textChanged.connect(self.on_font_changed)
        self.font_edit.setPlaceholderText("Select font file...")

        browse_btn = QPushButton("...")
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.browse_font)

        font_layout = QHBoxLayout()
        font_layout.addWidget(self.font_edit)
        font_layout.addWidget(browse_btn)
        form.addRow("Font File:", font_layout)

        # Font size
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(self._font_size)
        self.size_spin.valueChanged.connect(self.on_size_changed)
        form.addRow("Size:", self.size_spin)

        group.setLayout(form)
        layout.addWidget(group)

        # Preview label
        self.preview_label = QLabel("Preview: АаБбCc123")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 10px;")
        self.preview_label.setMinimumHeight(60)
        self.update_preview()
        layout.addWidget(self.preview_label)

    def browse_font(self):
        """Open font file browser."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Font", "", 
            "TrueType Fonts (*.ttf);;OpenType Fonts (*.otf);;All Files (*)"
        )
        if path:
            self.font_edit.setText(path.replace('\\', '/'))

    def on_font_changed(self, path: str):
        """Handle font path change."""
        self._font_path = path
        self.update_preview()
        self.font_changed.emit(self._font_path, self._font_size)

    def on_size_changed(self, size: int):
        """Handle font size change."""
        self._font_size = size
        self.update_preview()
        self.font_changed.emit(self._font_path, self._font_size)

    def update_preview(self):
        """Update font preview."""
        if self._font_path and Path(self._font_path).exists():
            # Try to load custom font
            font_id = QFontDatabase.addApplicationFont(self._font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    font = QFont(families[0], self._font_size)
                    self.preview_label.setFont(font)
                    return
        
        # Use default font
        font = QFont("Arial", self._font_size)
        self.preview_label.setFont(font)

    def get_font_path(self) -> str:
        """Get current font path."""
        return self._font_path

    def get_font_size(self) -> int:
        """Get current font size."""
        return self._font_size

    def set_font(self, path: str, size: int):
        """Set font from path and size."""
        self._font_path = path
        self._font_size = size
        self.font_edit.setText(path)
        self.size_spin.setValue(size)
        self.update_preview()
