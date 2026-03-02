"""Widgets for Spec Days Generator."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QSpinBox, QRadioButton, QButtonGroup
)

from ...ui_components import ColorPickerWidget, FontPickerWidget


class AlignmentRadioGroup(QWidget):
    """Radio button group for alignment selection."""
    
    changed = Signal(str)
    
    def __init__(self, options: list, default: str = "center", orientation: str = "horizontal", parent=None):
        super().__init__(parent)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        
        for i, opt in enumerate(options):
            radio = QRadioButton(opt)
            self._group.addButton(radio, i)
            lay.addWidget(radio)
            if opt == default:
                radio.setChecked(True)
        
        self._group.buttonClicked.connect(lambda btn: self.changed.emit(btn.text()))
    
    def value(self) -> str:
        btn = self._group.checkedButton()
        return btn.text() if btn else "center"
    
    def set_value(self, value: str):
        for btn in self._group.buttons():
            if btn.text() == value:
                btn.setChecked(True)
                break


class TextPositionWidget(QWidget):
    """Widget for configuring text position (X, Y)."""
    
    changed = Signal()
    
    def __init__(self, x: int = 0, y: int = 0, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        
        lay.addWidget(QLabel("X:"))
        self._x_spin = QSpinBox()
        self._x_spin.setRange(-10000, 10000)
        self._x_spin.setValue(x)
        self._x_spin.setFixedWidth(80)
        self._x_spin.valueChanged.connect(self.changed)
        lay.addWidget(self._x_spin)
        
        lay.addWidget(QLabel("Y:"))
        self._y_spin = QSpinBox()
        self._y_spin.setRange(-10000, 10000)
        self._y_spin.setValue(y)
        self._y_spin.setFixedWidth(80)
        self._y_spin.valueChanged.connect(self.changed)
        lay.addWidget(self._y_spin)
        
        lay.addStretch()
    
    def x(self) -> int:
        return self._x_spin.value()
    
    def y(self) -> int:
        return self._y_spin.value()
    
    def set_x(self, x: int):
        self._x_spin.setValue(x)
    
    def set_y(self, y: int):
        self._y_spin.setValue(y)
    
    def set_value(self, x: int, y: int):
        self._x_spin.setValue(x)
        self._y_spin.setValue(y)


class TextSettingsWidget(QWidget):
    """Widget for configuring text settings (font, size, color, alignment)."""
    
    changed = Signal()
    
    def __init__(self, title: str = "Настройки текста", parent=None):
        super().__init__(parent)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox(title)
        group_lay = QVBoxLayout(group)
        
        # Position
        self._position = TextPositionWidget()
        self._position.changed.connect(self.changed)
        group_lay.addWidget(QLabel("Позиция:"))
        group_lay.addWidget(self._position)
        
        # Horizontal alignment
        group_lay.addWidget(QLabel("Горизонтальное выравнивание:"))
        self._h_align = AlignmentRadioGroup(["left", "center", "right"], "center")
        self._h_align.changed.connect(self.changed)
        group_lay.addWidget(self._h_align)
        
        # Vertical alignment
        group_lay.addWidget(QLabel("Вертикальное выравнивание:"))
        self._v_align = AlignmentRadioGroup(["top", "center", "bottom"], "center")
        self._v_align.changed.connect(self.changed)
        group_lay.addWidget(self._v_align)
        
        # Font size
        group_lay.addWidget(QLabel("Размер текста:"))
        self._font_size = QSpinBox()
        self._font_size.setRange(8, 500)
        self._font_size.setValue(24)
        self._font_size.setFixedWidth(80)
        self._font_size.valueChanged.connect(self.changed)
        group_lay.addWidget(self._font_size)
        
        # Font color
        group_lay.addWidget(QLabel("Цвет текста:"))
        self._color_picker = ColorPickerWidget([255, 255, 255])
        self._color_picker.colorChanged.connect(self.changed)
        group_lay.addWidget(self._color_picker)
        
        # Font family
        group_lay.addWidget(QLabel("Шрифт:"))
        self._font_picker = FontPickerWidget()
        self._font_picker.fontChanged.connect(self.changed)
        group_lay.addWidget(self._font_picker)
        
        main_lay.addWidget(group)
    
    def get_settings(self) -> dict:
        return {
            "x": self._position.x(),
            "y": self._position.y(),
            "h_align": self._h_align.value(),
            "v_align": self._v_align.value(),
            "font_size": self._font_size.value(),
            "color": self._color_picker.value(),
            "font": self._font_picker.value(),
        }
    
    def set_settings(self, settings: dict):
        self._position.set_value(settings.get("x", 0), settings.get("y", 0))
        self._h_align.set_value(settings.get("h_align", "center"))
        self._v_align.set_value(settings.get("v_align", "center"))
        self._font_size.setValue(settings.get("font_size", 24))
        self._color_picker.set_value(settings.get("color", [255, 255, 255]))
        self._font_picker.set_value(settings.get("font", ""))


class CanvasSettingsWidget(QWidget):
    """Widget for configuring canvas settings (width, height, background)."""
    
    changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Холст")
        group_lay = QVBoxLayout(group)
        
        # Width
        width_lay = QHBoxLayout()
        width_lay.addWidget(QLabel("Ширина:"))
        self._width_spin = QSpinBox()
        self._width_spin.setRange(100, 10000)
        self._width_spin.setValue(800)
        self._width_spin.setFixedWidth(80)
        self._width_spin.valueChanged.connect(self.changed)
        width_lay.addWidget(self._width_spin)
        width_lay.addStretch()
        group_lay.addLayout(width_lay)
        
        # Height
        height_lay = QHBoxLayout()
        height_lay.addWidget(QLabel("Высота:"))
        self._height_spin = QSpinBox()
        self._height_spin.setRange(100, 10000)
        self._height_spin.setValue(600)
        self._height_spin.setFixedWidth(80)
        self._height_spin.valueChanged.connect(self.changed)
        height_lay.addWidget(self._height_spin)
        height_lay.addStretch()
        group_lay.addLayout(height_lay)
        
        # Background image
        group_lay.addWidget(QLabel("Фоновое изображение:"))
        from ...ui_components import ImagePickerWidget
        self._bg_picker = ImagePickerWidget()
        self._bg_picker.pathChanged.connect(self.changed)
        group_lay.addWidget(self._bg_picker)
        
        main_lay.addWidget(group)
    
    def get_settings(self) -> dict:
        return {
            "width": self._width_spin.value(),
            "height": self._height_spin.value(),
            "background": self._bg_picker.value(),
        }
    
    def set_settings(self, settings: dict):
        self._width_spin.setValue(settings.get("width", 800))
        self._height_spin.setValue(settings.get("height", 600))
        self._bg_picker.set_value(settings.get("background", ""))
