"""Unified days tab for Calendar Config Editor."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QSpinBox, QSplitter, QPushButton, QComboBox, QLineEdit,
    QGroupBox, QScrollArea, QGridLayout,
)
from PySide6.QtGui import QPixmap

from ..constants import ALIGN_OPTIONS
from ..widgets import (
    ColorPickerWidget,
    ImagePickerWidget,
    FontPickerWidget,
    PreviewLabel,
)


class CommonDaySettingsWidget(QWidget):
    """Widget for editing common day settings (width, height, padding)."""
    changed = Signal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self._widgets = {}
        self._build()

    def _build(self):
        lay = QGridLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setHorizontalSpacing(12)
        lay.setVerticalSpacing(8)

        # Common settings that will be applied to all day types
        common_fields = [
            ("width", "Ширина (px)", 0, 0),
            ("height", "Высота (px)", 0, 1),
            ("padding", "Padding", 1, 0),
            ("padding_top", "Padding top", 2, 0),
            ("padding_right", "Padding right", 2, 1),
            ("padding_bottom", "Padding bottom", 3, 0),
            ("padding_left", "Padding left", 3, 1),
        ]

        def add_spin(key, label, row, col):
            # Get value from first available day section
            value = 0
            for day_key in ["regular_day", "weekend", "spec_day"]:
                if day_key in self._config and key in self._config[day_key]:
                    value = self._config[day_key][key]
                    break

            w = QSpinBox()
            w.setRange(0, 9999)
            w.setValue(value)
            w.setObjectName(f"common_{key}")
            w.valueChanged.connect(lambda v, k=key: self._on_change(k, v))
            lay.addWidget(QLabel(label), row, col * 2)
            lay.addWidget(w, row, col * 2 + 1)
            self._widgets[key] = w

        for key, label, row, col in common_fields:
            # Check if any day section has this field
            for day_key in ["regular_day", "weekend", "spec_day"]:
                if day_key in self._config and key in self._config[day_key]:
                    add_spin(key, label, row, col)
                    break

    def _on_change(self, key, value):
        """Apply common setting to all day sections that have this field."""
        for day_key in ["regular_day", "weekend", "spec_day"]:
            if day_key in self._config and key in self._config[day_key]:
                self._config[day_key][key] = value
        self.changed.emit()

    def get_data(self) -> dict:
        """Return empty dict - common settings are already applied to sections."""
        return {}


class DaySectionWidget(QWidget):
    """Widget for editing a single day section (regular_day, weekend, spec_day)."""
    changed = Signal()

    def __init__(self, key: str, data: dict, show_preview_fn=None, common_settings: dict = None, parent=None):
        super().__init__(parent)
        self._key = key
        self._data = data
        self._preview_fn = show_preview_fn
        self._common_settings = common_settings or {}
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # --- form ---
        form_w = QWidget()
        form = QFormLayout(form_w)
        form.setLabelAlignment(Qt.AlignRight)
        form.setHorizontalSpacing(12)

        self._widgets = {}

        def add_spin(key, label, mn=0, mx=9999):
            w = QSpinBox()
            w.setRange(mn, mx)
            w.setValue(self._data.get(key, 0))
            w.valueChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            self._widgets[key] = w

        def add_text(key, label):
            w = QLineEdit(str(self._data.get(key, "")))
            w.textChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            self._widgets[key] = w

        def add_color(key, label):
            w = ColorPickerWidget(self._data.get(key, [0, 0, 0]))
            w.colorChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            self._widgets[key] = w

        def add_image(key, label):
            w = ImagePickerWidget(self._data.get(key, ""))
            w.pathChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            # виджет с показом изображения
            img_preview = QLabel(self,)
            img_preview.setFixedSize(100, 100)
            img_preview.setStyleSheet("border: 1px solid #ccc;")
            img_preview.setAlignment(Qt.AlignCenter)
            form.addRow("Превью", img_preview)

            def update_preview(path):
                resize_preview(path)
            # надо уменишить размер изображения, если оно слишком большое
            def resize_preview(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        img_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    img_preview.setPixmap(pixmap)
                else:
                    img_preview.setPixmap(QPixmap())
            w.pathChanged.connect(update_preview)
            update_preview(self._data.get(key, ""))

            self._widgets[key] = w

        def add_font(key, label):
            w = FontPickerWidget(self._data.get(key, ""))
            w.fontChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            self._widgets[key] = w

        def add_combo(key, label, options):
            w = QComboBox()
            w.addItems(options)
            cur = self._data.get(key, options[0])
            if cur in options:
                w.setCurrentText(cur)
            w.currentTextChanged.connect(lambda v, k=key: self._on_change(k, v))
            form.addRow(label, w)
            self._widgets[key] = w

        def add_position(key, label):
            """Add X,Y position editor as two spinboxes side by side."""
            pos_container = QWidget()
            pos_lay = QHBoxLayout(pos_container)
            pos_lay.setContentsMargins(0, 0, 0, 0)
            pos_lay.setSpacing(6)

            pos_value = self._data.get(key, [0, 0])
            pos_x = pos_value[0] if len(pos_value) >= 1 else 0
            pos_y = pos_value[1] if len(pos_value) >= 2 else 0

            spin_x = QSpinBox()
            spin_x.setRange(0, 9999)
            spin_x.setValue(pos_x)
            spin_x.setSuffix(" X")

            spin_y = QSpinBox()
            spin_y.setRange(0, 9999)
            spin_y.setValue(pos_y)
            spin_y.setSuffix(" Y")

            def on_pos_change():
                new_pos = [spin_x.value(), spin_y.value()]
                self._data[key] = new_pos
                self.changed.emit()

            spin_x.valueChanged.connect(on_pos_change)
            spin_y.valueChanged.connect(on_pos_change)

            pos_lay.addWidget(spin_x)
            pos_lay.addWidget(spin_y)
            pos_lay.addStretch()

            form.addRow(label, pos_container)
            self._widgets[key] = (spin_x, spin_y)

        # Skip common settings - they are handled by CommonDaySettingsWidget
        if "text_size" in self._data:      add_spin("text_size", "Размер шрифта")
        if "month_text_height" in self._data: add_spin("month_text_height", "Высота текста месяца")
        if "text_position" in self._data:  add_position("text_position", "Позиция текста")
        if "text_color" in self._data:     add_color("text_color", "Цвет текста")
        if "text_font" in self._data:      add_font("text_font", "Шрифт")
        if "text_align" in self._data:     add_combo("text_align", "Выравнивание", ALIGN_OPTIONS)
        if "background" in self._data:     add_image("background", "Фон")

        # --- preview ---
        self._preview = PreviewLabel()
        btn_preview = QPushButton("Обновить превью")
        btn_preview.clicked.connect(self._update_preview)

        right_w = QWidget()
        right_lay = QVBoxLayout(right_w)
        right_lay.addWidget(QLabel("<b>Превью</b>"))
        right_lay.addWidget(self._preview)
        right_lay.addWidget(btn_preview)
        right_lay.addStretch()

        splitter.addWidget(form_w)
        splitter.addWidget(right_w)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter)

    def _on_change(self, key, value):
        self._data[key] = value
        self.changed.emit()

    def _update_preview(self):
        if self._preview_fn:
            pm = self._preview_fn(self._data)
            self._preview.set_pixmap(pm)

    def get_data(self) -> dict:
        return self._data


class DaysTab(QWidget):
    """Unified tab for editing all day sections (regular_day, weekend, spec_day)."""
    changed = Signal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config
        self._day_widgets: dict[str, DaySectionWidget] = {}
        self._common_settings_widget: CommonDaySettingsWidget | None = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container_lay = QVBoxLayout(container)
        container_lay.setSpacing(12)

        # Common settings group at the top
        common_group = QGroupBox("⚙ Общие настройки дней")
        self._common_settings_widget = CommonDaySettingsWidget(self._config)
        self._common_settings_widget.changed.connect(self._on_change)
        common_group.setLayout(QVBoxLayout())
        common_group.layout().addWidget(self._common_settings_widget)
        container_lay.addWidget(common_group)

        # Group boxes for each day type
        day_sections = [
            ("regular_day", "🗓 Обычный день"),
            ("weekend", "🌅 Выходной"),
            ("spec_day", "⭐ Особый день"),
        ]

        for key, title in day_sections:
            if key in self._config:
                group = QGroupBox(title)
                group_layout = QVBoxLayout(group)
                group_layout.setContentsMargins(8, 8, 8, 8)

                day_widget = DaySectionWidget(
                    key,
                    self._config[key],
                    show_preview_fn=get_day_preview,
                )
                day_widget.changed.connect(self._on_change)
                group_layout.addWidget(day_widget)
                container_lay.addWidget(group)
                self._day_widgets[key] = day_widget

        container_lay.addStretch()
        scroll.setWidget(container)
        lay.addWidget(scroll)

    def _on_change(self):
        self.changed.emit()

    def get_data(self) -> dict:
        result = {}
        for key, widget in self._day_widgets.items():
            result[key] = widget.get_data()
        return result


# Import preview function
from ..preview import get_day_preview
