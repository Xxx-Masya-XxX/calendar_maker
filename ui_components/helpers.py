"""Helper functions for Calendar Config Editor UI."""

from PySide6.QtGui import QColor, QPixmap, QPainter, QPen


def color_from_list(lst: list) -> QColor:
    """Convert RGB list to QColor."""
    if lst and len(lst) >= 3:
        return QColor(lst[0], lst[1], lst[2])
    return QColor(0, 0, 0)


def list_from_color(c: QColor) -> list:
    """Convert QColor to RGB list."""
    return [c.red(), c.green(), c.blue()]


def color_swatch(color: QColor, size: int = 22) -> QPixmap:
    """Create a color swatch pixmap."""
    pm = QPixmap(size, size)
    pm.fill(color)
    p = QPainter(pm)
    p.setPen(QPen(QColor(180, 180, 180)))
    p.drawRect(0, 0, size - 1, size - 1)
    p.end()
    return pm
