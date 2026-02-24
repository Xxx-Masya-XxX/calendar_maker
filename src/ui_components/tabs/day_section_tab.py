"""Day section tab for Calendar Config Editor."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QSpinBox, QSplitter, QPushButton, QComboBox, QLineEdit,
)
from PySide6.QtGui import QPixmap

from ..constants import ALIGN_OPTIONS
from ..widgets import (
    ColorPickerWidget,
    ImagePickerWidget,
    FontPickerWidget,
    PreviewLabel,
)


class DaySectionTab(QWidget):
    """Tab for editing day_of_the_week / regular_day / spec_day / weekend sections."""
    changed = Signal()

    def __init__(self, data: dict, show_preview_fn=None, parent=None):
        super().__init__(parent)
        self._data = data
        self._preview_fn = show_preview_fn
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
                # img_preview.setPixmap(QPixmap(path) if path else QPixmap())
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

        if "width" in self._data:    add_spin("width", "Ширина (px)")
        if "height" in self._data:   add_spin("height", "Высота (px)")
        if "gap" in self._data:      add_spin("gap", "Отступ (gap)")
        if "padding" in self._data:  add_spin("padding", "Padding")
        if "padding_top" in self._data:    add_spin("padding_top", "Padding top")
        if "padding_right" in self._data:  add_spin("padding_right", "Padding right")
        if "padding_bottom" in self._data: add_spin("padding_bottom", "Padding bottom")
        if "padding_left" in self._data:   add_spin("padding_left", "Padding left")
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
