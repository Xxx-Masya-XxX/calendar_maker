"""Color picker widget with visual preview."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QColorDialog
from PySide6.QtGui import QColor, QPixmap, QPainter, QCursor
from PySide6.QtCore import Signal, QSize, Qt


class ColorPicker(QWidget):
    """Color picker widget with visual color preview."""

    color_changed = Signal(tuple)  # BGR tuple

    def __init__(self, initial_color: tuple = (0, 0, 0), parent=None):
        """
        Initialize color picker.

        Args:
            initial_color: Initial color as BGR tuple
            parent: Parent widget
        """
        super().__init__(parent)
        self._color = initial_color
        self.setup_ui()
        self.update_color_display()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Color preview button
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(40, 25)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self.choose_color)
        layout.addWidget(self.color_btn)

        # RGB values label
        self.label = QLabel()
        self.update_label()
        layout.addWidget(self.label)

        # Edit button
        edit_btn = QPushButton("Select...")
        edit_btn.clicked.connect(self.choose_color)
        layout.addWidget(edit_btn)

    def update_color_display(self):
        """Update color button appearance."""
        # Convert BGR to RGB for Qt
        r, g, b = self._color[2], self._color[1], self._color[0]
        qcolor = QColor(r, g, b)
        
        # Create pixmap with color
        pixmap = QPixmap(40, 25)
        pixmap.fill(qcolor)
        
        # Add border
        painter = QPainter(pixmap)
        painter.setPen(QColor(128, 128, 128))
        painter.drawRect(0, 0, 39, 24)
        painter.end()
        
        self.color_btn.setIcon(pixmap)
        self.color_btn.setIconSize(QSize(40, 25))
        self.update_label()

    def update_label(self):
        """Update color values label."""
        self.label.setText(f"BGR({self._color[0]}, {self._color[1]}, {self._color[2]})")
        self.label.setStyleSheet("font-family: Consolas; font-size: 11px;")

    def choose_color(self):
        """Open color dialog."""
        # Convert BGR to RGB for Qt
        r, g, b = self._color[2], self._color[1], self._color[0]
        initial = QColor(r, g, b)
        
        color = QColorDialog.getColor(initial, self, "Select Color")
        
        if color.isValid():
            # Convert RGB to BGR
            self._color = (color.blue(), color.green(), color.red())
            self.update_color_display()
            self.color_changed.emit(self._color)

    def get_color(self) -> tuple:
        """Get current color as BGR tuple."""
        return self._color

    def set_color(self, color: tuple):
        """Set color from BGR tuple."""
        if len(color) == 3:
            self._color = tuple(int(c) for c in color)
            self.update_color_display()
