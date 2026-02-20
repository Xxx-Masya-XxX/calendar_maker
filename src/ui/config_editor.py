"""Configuration editor widget with visual controls."""

import copy

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QSpinBox, QGroupBox, QHBoxLayout,
    QComboBox, QLabel
)
from PySide6.QtCore import Signal

from src.ui.widgets.color_picker import ColorPicker
from src.ui.widgets.font_picker import FontPicker


class ConfigEditor(QWidget):
    """Editor for one configuration section with visual controls."""

    changed = Signal()

    def __init__(self, title: str, config: dict, parent=None, show_dimensions: bool = True):
        super().__init__(parent)
        self.config = copy.deepcopy(config)
        self.show_dimensions = show_dimensions
        self.setup_ui(title)

    def setup_ui(self, title: str):
        layout = QVBoxLayout(self)

        group = QGroupBox(title)
        form = QFormLayout()

        # Width and Height (only for day sections)
        if self.show_dimensions:
            self.width_spin = QSpinBox()
            self.width_spin.setRange(50, 1000)
            self.width_spin.setValue(self.config.get('width', 200))
            self.width_spin.valueChanged.connect(self.on_change)
            form.addRow("Width:", self.width_spin)

            self.height_spin = QSpinBox()
            self.height_spin.setRange(50, 1000)
            self.height_spin.setValue(self.config.get('height', 200))
            self.height_spin.valueChanged.connect(self.on_change)
            form.addRow("Height:", self.height_spin)

        # Font size
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(8, 200)
        self.text_size_spin.setValue(self.config.get('text_size', 48))
        self.text_size_spin.valueChanged.connect(self.on_change)
        form.addRow("Font size:", self.text_size_spin)

        # Text position (only for day sections)
        if self.show_dimensions:
            self.text_position_x = QSpinBox()
            self.text_position_x.setRange(-500, 500)
            pos = self.config.get('text_position', [40, 40])
            self.text_position_x.setValue(pos[0])
            self.text_position_x.valueChanged.connect(self.on_change)

            self.text_position_y = QSpinBox()
            self.text_position_y.setRange(-500, 500)
            self.text_position_y.setValue(pos[1])
            self.text_position_y.valueChanged.connect(self.on_change)

            pos_layout = QHBoxLayout()
            pos_layout.addWidget(self.text_position_x)
            pos_layout.addWidget(QLabel(","))
            pos_layout.addWidget(self.text_position_y)
            pos_layout.addStretch()
            form.addRow("Text position (X, Y):", pos_layout)

        # Text color with visual picker
        color = self.config.get('text_color', [0, 0, 0])
        self.color_picker = ColorPicker(tuple(color))
        self.color_picker.color_changed.connect(self.on_change)
        form.addRow("Text color:", self.color_picker)

        # Alignment
        self.text_align_edit = QComboBox()
        self.text_align_edit.addItems(['left', 'center', 'right'])
        self.text_align_edit.setCurrentText(self.config.get('text_align', 'left'))
        self.text_align_edit.currentTextChanged.connect(self.on_change)
        form.addRow("Alignment:", self.text_align_edit)

        # Font picker with preview
        font_path = self.config.get('text_font', 'C:/Windows/Fonts/arial.ttf')
        font_size = self.config.get('text_size', 48)
        self.font_picker = FontPicker(font_path, font_size)
        self.font_picker.font_changed.connect(self.on_change)
        form.addRow("Font:", self.font_picker)

        # Gap (only for month section)
        if 'gap' in self.config:
            self.gap_spin = QSpinBox()
            self.gap_spin.setRange(0, 100)
            self.gap_spin.setValue(self.config.get('gap', 10))
            self.gap_spin.valueChanged.connect(self.on_change)
            form.addRow("Gap:", self.gap_spin)

        # Background image with preview
        from src.ui.widgets.image_preview import ImagePreview
        bg_path = self.config.get('background', '')
        self.bg_preview = ImagePreview(bg_path, "No background image")
        self.bg_preview.image_changed.connect(self.on_change)
        form.addRow("Background:", self.bg_preview)

        group.setLayout(form)
        layout.addWidget(group)

    def on_change(self):
        self.changed.emit()

    def get_config(self) -> dict:
        config = copy.deepcopy(self.config)
        
        if self.show_dimensions:
            config['width'] = self.width_spin.value()
            config['height'] = self.height_spin.value()
            config['text_position'] = [
                self.text_position_x.value(),
                self.text_position_y.value()
            ]

        config['text_size'] = self.text_size_spin.value()
        config['text_color'] = list(self.color_picker.get_color())
        config['text_align'] = self.text_align_edit.currentText()
        config['text_font'] = self.font_picker.get_font_path()
        config['background'] = self.bg_preview.get_image_path()

        if hasattr(self, 'gap_spin'):
            config['gap'] = self.gap_spin.value()

        return config
