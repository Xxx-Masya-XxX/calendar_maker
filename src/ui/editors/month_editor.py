"""Month editor with support for all month-specific parameters."""


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QSpinBox, QLabel, QScrollArea, QComboBox
)
from PySide6.QtCore import Signal

from src.ui.widgets.color_picker import ColorPicker
from src.ui.widgets.font_picker import FontPicker
from src.ui.widgets.image_preview import ImagePreview


class MonthConfigWidget(QWidget):
    """Widget for editing a single month configuration."""

    changed = Signal()

    def __init__(self, month_name: str, month_index: int, config: dict = None, parent=None):
        super().__init__(parent)
        self.month_name = month_name
        self.month_index = month_index
        self.config = config or {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Group box
        group = QGroupBox(f"{self.month_name}")
        group.setCheckable(True)
        group.setChecked(bool(self.config))
        group.toggled.connect(self.on_change)
        
        form = QFormLayout()
        form.setSpacing(5)

        # Background image
        bg_path = self.config.get('background', '')
        self.bg_preview = ImagePreview(bg_path, "Нет фона")
        self.bg_preview.image_changed.connect(self.on_change)
        form.addRow("Фон:", self.bg_preview)

        # Text color
        color = self.config.get('text_color', [0, 0, 0])
        self.color_picker = ColorPicker(tuple(color))
        self.color_picker.color_changed.connect(self.on_change)
        form.addRow("Цвет текста:", self.color_picker)

        # Font
        font_path = self.config.get('text_font', '')
        font_size = self.config.get('text_size', 98)
        self.font_picker = FontPicker(font_path, font_size)
        self.font_picker.font_changed.connect(self.on_change)
        form.addRow("Шрифт:", self.font_picker)

        # Font size
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(8, 200)
        self.text_size_spin.setValue(font_size)
        self.text_size_spin.valueChanged.connect(self.on_change)
        form.addRow("Размер шрифта:", self.text_size_spin)

        # Min width
        self.min_width_spin = QSpinBox()
        self.min_width_spin.setRange(0, 5000)
        self.min_width_spin.setValue(self.config.get('min_width', 0))
        self.min_width_spin.valueChanged.connect(self.on_change)
        form.addRow("Мин. ширина:", self.min_width_spin)

        # Min height
        self.min_height_spin = QSpinBox()
        self.min_height_spin.setRange(0, 5000)
        self.min_height_spin.setValue(self.config.get('min_height', 0))
        self.min_height_spin.valueChanged.connect(self.on_change)
        form.addRow("Мин. высота:", self.min_height_spin)

        # Padding top
        self.padding_top_spin = QSpinBox()
        self.padding_top_spin.setRange(0, 2000)
        self.padding_top_spin.setValue(self.config.get('padding_top', 0))
        self.padding_top_spin.valueChanged.connect(self.on_change)
        form.addRow("Отступ сверху:", self.padding_top_spin)

        # Padding right
        self.padding_right_spin = QSpinBox()
        self.padding_right_spin.setRange(0, 2000)
        self.padding_right_spin.setValue(self.config.get('padding_right', 0))
        self.padding_right_spin.valueChanged.connect(self.on_change)
        form.addRow("Отступ справа:", self.padding_right_spin)

        # Padding bottom
        self.padding_bottom_spin = QSpinBox()
        self.padding_bottom_spin.setRange(0, 2000)
        self.padding_bottom_spin.setValue(self.config.get('padding_bottom', 0))
        self.padding_bottom_spin.valueChanged.connect(self.on_change)
        form.addRow("Отступ снизу:", self.padding_bottom_spin)

        # Padding left
        self.padding_left_spin = QSpinBox()
        self.padding_left_spin.setRange(0, 2000)
        self.padding_left_spin.setValue(self.config.get('padding_left', 0))
        self.padding_left_spin.valueChanged.connect(self.on_change)
        form.addRow("Отступ слева:", self.padding_left_spin)

        # Width position
        self.width_pos_combo = QComboBox()
        self.width_pos_combo.addItems(['center', 'left', 'right'])
        width_pos = self.config.get('width_pos', 'center')
        self.width_pos_combo.setCurrentText(width_pos)
        self.width_pos_combo.currentTextChanged.connect(self.on_change)
        form.addRow("Позиция (гор.):", self.width_pos_combo)

        # Height position
        self.height_pos_combo = QComboBox()
        self.height_pos_combo.addItems(['center', 'top', 'bottom'])
        height_pos = self.config.get('height_pos', 'center')
        self.height_pos_combo.setCurrentText(height_pos)
        self.height_pos_combo.currentTextChanged.connect(self.on_change)
        form.addRow("Позиция (верт.):", self.height_pos_combo)

        group.setLayout(form)
        layout.addWidget(group)

    def on_change(self):
        self.changed.emit()

    def get_config(self) -> dict:
        """Get month configuration."""
        if not self.config and not self.bg_preview.get_image_path():
            return {}
        
        return {
            'name': self.month_name,
            'background': self.bg_preview.get_image_path(),
            'text_color': list(self.color_picker.get_color()),
            'text_font': self.font_picker.get_font_path(),
            'text_size': self.text_size_spin.value(),
            'min_width': self.min_width_spin.value(),
            'min_height': self.min_height_spin.value(),
            'padding_top': self.padding_top_spin.value(),
            'padding_right': self.padding_right_spin.value(),
            'padding_bottom': self.padding_bottom_spin.value(),
            'padding_left': self.padding_left_spin.value(),
            'width_pos': self.width_pos_combo.currentText(),
            'height_pos': self.height_pos_combo.currentText(),
        }

    def set_config(self, config: dict):
        """Set month configuration."""
        self.config = config or {}
        
        if config:
            self.bg_preview.set_image_path(config.get('background', ''))
            self.color_picker.set_color(tuple(config.get('text_color', [0, 0, 0])))
            self.font_picker.set_font(
                config.get('text_font', ''),
                config.get('text_size', 98)
            )
            self.text_size_spin.setValue(config.get('text_size', 98))
            self.min_width_spin.setValue(config.get('min_width', 0))
            self.min_height_spin.setValue(config.get('min_height', 0))
            self.padding_top_spin.setValue(config.get('padding_top', 0))
            self.padding_right_spin.setValue(config.get('padding_right', 0))
            self.padding_bottom_spin.setValue(config.get('padding_bottom', 0))
            self.padding_left_spin.setValue(config.get('padding_left', 0))
            self.width_pos_combo.setCurrentText(config.get('width_pos', 'center'))
            self.height_pos_combo.setCurrentText(config.get('height_pos', 'center'))


class MonthEditor(QWidget):
    """Editor for month settings with individual month configurations."""

    changed = Signal()

    MONTH_NAMES = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_config = {}
        self.months_list = []
        self.month_widgets = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Base settings group
        base_group = QGroupBox("Базовые настройки месяцев (по умолчанию)")
        base_layout = QVBoxLayout(base_group)

        # Base settings form
        base_form = QFormLayout()
        base_form.setSpacing(5)

        # Background
        bg_path = self.base_config.get('background', '')
        self.base_bg_preview = ImagePreview(bg_path, "Нет фона")
        self.base_bg_preview.image_changed.connect(self.on_change)
        base_form.addRow("Фон по умолчанию:", self.base_bg_preview)

        # Gap
        self.gap_spin = QSpinBox()
        self.gap_spin.setRange(0, 100)
        self.gap_spin.setValue(self.base_config.get('gap', 10))
        self.gap_spin.valueChanged.connect(self.on_change)
        base_form.addRow("Отступ между днями:", self.gap_spin)

        # Text color
        color = self.base_config.get('text_color', [0, 0, 0])
        self.base_color_picker = ColorPicker(tuple(color))
        self.base_color_picker.color_changed.connect(self.on_change)
        base_form.addRow("Цвет текста:", self.base_color_picker)

        # Font
        font_path = self.base_config.get('text_font', '')
        font_size = self.base_config.get('text_size', 98)
        self.base_font_picker = FontPicker(font_path, font_size)
        self.base_font_picker.font_changed.connect(self.on_change)
        base_form.addRow("Шрифт:", self.base_font_picker)

        # Text size
        self.base_text_size_spin = QSpinBox()
        self.base_text_size_spin.setRange(8, 200)
        self.base_text_size_spin.setValue(font_size)
        self.base_text_size_spin.valueChanged.connect(self.on_change)
        base_form.addRow("Размер шрифта:", self.base_text_size_spin)

        # Padding
        self.base_padding_spin = QSpinBox()
        self.base_padding_spin.setRange(0, 2000)
        self.base_padding_spin.setValue(self.base_config.get('padding', 0))
        self.base_padding_spin.valueChanged.connect(self.on_change)
        base_form.addRow("Общий отступ (padding):", self.base_padding_spin)

        base_layout.addLayout(base_form)
        layout.addWidget(base_group)

        # Individual months section
        months_label = QLabel("Индивидуальные настройки для каждого месяца:")
        months_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(months_label)

        # Scroll area for months
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.months_container = QWidget()
        self.months_layout = QVBoxLayout(self.months_container)
        self.months_layout.setSpacing(5)

        # Create month widgets
        self.create_month_widgets()

        scroll.setWidget(self.months_container)
        layout.addWidget(scroll)

    def create_month_widgets(self):
        """Create widgets for each month."""
        # Clear existing
        while self.months_layout.count():
            item = self.months_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.month_widgets = []

        # Create widget for each month
        for i, month_name in enumerate(self.MONTH_NAMES):
            config = self.months_list[i] if i < len(self.months_list) else {}
            widget = MonthConfigWidget(month_name, i, config)
            widget.changed.connect(self.on_change)
            self.month_widgets.append(widget)
            self.months_layout.addWidget(widget)

        self.months_layout.addStretch()

    def on_change(self):
        self.changed.emit()

    def get_month_config(self) -> dict:
        """Get base month configuration."""
        return {
            'background': self.base_bg_preview.get_image_path(),
            'gap': self.gap_spin.value(),
            'text_color': list(self.base_color_picker.get_color()),
            'text_font': self.base_font_picker.get_font_path(),
            'text_size': self.base_text_size_spin.value(),
            'padding': self.base_padding_spin.value(),
        }

    def get_months_list(self) -> list:
        """Get list of individual month configurations."""
        return [widget.get_config() for widget in self.month_widgets]

    def set_config(self, base_config: dict, months_list: list):
        """Set month configurations."""
        self.base_config = base_config or {}
        self.months_list = months_list or []

        # Update base settings
        self.base_bg_preview.set_image_path(self.base_config.get('background', ''))
        self.gap_spin.setValue(self.base_config.get('gap', 10))
        self.base_color_picker.set_color(tuple(self.base_config.get('text_color', [0, 0, 0])))
        self.base_font_picker.set_font(
            self.base_config.get('text_font', ''),
            self.base_config.get('text_size', 98)
        )
        self.base_text_size_spin.setValue(self.base_config.get('text_size', 98))
        self.base_padding_spin.setValue(self.base_config.get('padding', 0))

        # Recreate month widgets
        self.create_month_widgets()
