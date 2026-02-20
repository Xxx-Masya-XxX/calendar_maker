"""Day editor for day of week, regular day, weekend, and special day."""


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QSpinBox, QLabel, QComboBox
)
from PySide6.QtCore import Signal

from src.ui.widgets.color_picker import ColorPicker
from src.ui.widgets.font_picker import FontPicker
from src.ui.widgets.image_preview import ImagePreview


class DayEditor(QWidget):
    """Editor for day configuration (day of week, regular day, weekend, special day)."""

    changed = Signal()

    def __init__(self, title: str, show_header_options: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.show_header_options = show_header_options
        self.config = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Group box
        group = QGroupBox(f"{self.title}")
        form = QFormLayout()
        form.setSpacing(5)

        # Width and Height
        self.width_spin = QSpinBox()
        self.width_spin.setRange(50, 1000)
        self.width_spin.setValue(200)
        self.width_spin.valueChanged.connect(self.on_change)
        form.addRow("Ширина:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 1000)
        self.height_spin.setValue(200)
        self.height_spin.valueChanged.connect(self.on_change)
        form.addRow("Высота:", self.height_spin)

        # Font size
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(8, 200)
        self.text_size_spin.setValue(48)
        self.text_size_spin.valueChanged.connect(self.on_change)
        form.addRow("Размер шрифта:", self.text_size_spin)

        # Text position X
        self.text_pos_x_spin = QSpinBox()
        self.text_pos_x_spin.setRange(-500, 500)
        self.text_pos_x_spin.setValue(40)
        self.text_pos_x_spin.valueChanged.connect(self.on_change)
        form.addRow("Позиция X:", self.text_pos_x_spin)

        # Text position Y
        self.text_pos_y_spin = QSpinBox()
        self.text_pos_y_spin.setRange(-500, 500)
        self.text_pos_y_spin.setValue(40)
        self.text_pos_y_spin.valueChanged.connect(self.on_change)
        form.addRow("Позиция Y:", self.text_pos_y_spin)

        # Text color
        self.color_picker = ColorPicker((0, 0, 0))
        self.color_picker.color_changed.connect(self.on_change)
        form.addRow("Цвет текста:", self.color_picker)

        # Alignment
        self.align_combo = QComboBox()
        self.align_combo.addItems(['left', 'center', 'right'])
        self.align_combo.setCurrentText('center')
        self.align_combo.currentTextChanged.connect(self.on_change)
        form.addRow("Выравнивание:", self.align_combo)

        # Font
        self.font_picker = FontPicker('', 48)
        self.font_picker.font_changed.connect(self.on_change)
        form.addRow("Шрифт:", self.font_picker)

        # Background image
        self.bg_preview = ImagePreview('', "Нет фона")
        self.bg_preview.image_changed.connect(self.on_change)
        form.addRow("Фон:", self.bg_preview)

        # Gap (for day of week)
        if self.show_header_options:
            self.gap_spin = QSpinBox()
            self.gap_spin.setRange(0, 100)
            self.gap_spin.setValue(10)
            self.gap_spin.valueChanged.connect(self.on_change)
            form.addRow("Отступ (gap):", self.gap_spin)

        group.setLayout(form)
        layout.addWidget(group)

        # Info label
        if self.show_header_options:
            info = QLabel(
                "Эти настройки используются для заголовка с днями недели.\n"
                "Выходные дни (суббота, воскресенье) автоматически окрашиваются в красный цвет."
            )
            info.setWordWrap(True)
            layout.addWidget(info)

    def on_change(self):
        self.changed.emit()

    def get_config(self) -> dict:
        """Get day configuration."""
        config = {
            'width': self.width_spin.value(),
            'height': self.height_spin.value(),
            'text_size': self.text_size_spin.value(),
            'text_position': [self.text_pos_x_spin.value(), self.text_pos_y_spin.value()],
            'text_color': list(self.color_picker.get_color()),
            'text_align': self.align_combo.currentText(),
            'text_font': self.font_picker.get_font_path(),
            'background': self.bg_preview.get_image_path(),
        }

        if self.show_header_options and hasattr(self, 'gap_spin'):
            config['gap'] = self.gap_spin.value()

        return config

    def set_config(self, config: dict):
        """Set day configuration."""
        self.config = config or {}

        self.width_spin.setValue(self.config.get('width', 200))
        self.height_spin.setValue(self.config.get('height', 200))
        self.text_size_spin.setValue(self.config.get('text_size', 48))

        pos = self.config.get('text_position', [40, 40])
        self.text_pos_x_spin.setValue(pos[0])
        self.text_pos_y_spin.setValue(pos[1])

        self.color_picker.set_color(tuple(self.config.get('text_color', [0, 0, 0])))
        self.align_combo.setCurrentText(self.config.get('text_align', 'center'))
        self.font_picker.set_font(
            self.config.get('text_font', ''),
            self.config.get('text_size', 48)
        )
        self.bg_preview.set_image_path(self.config.get('background', ''))

        if self.show_header_options and hasattr(self, 'gap_spin'):
            self.gap_spin.setValue(self.config.get('gap', 10))
