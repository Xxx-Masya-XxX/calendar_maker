"""Months tab for Calendar Config Editor."""

import copy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QMessageBox, QSpinBox, QComboBox, QSplitter,
)

from ..constants import FONT_PRESETS, WIDTH_POS_OPTIONS, HEIGHT_POS_OPTIONS
from ..helpers import color_from_list
from ..widgets import (
    ColorPickerWidget,
    ImagePickerWidget,
    FontPickerWidget,
    PreviewLabel,
)
from ..preview import get_month_preview


class MonthItemDialog(QDialog):
    """Dialog for editing a single month item."""

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка месяца")
        self.setMinimumWidth(520)
        self._data = item

        form = QFormLayout()

        self._name = QLineEdit(item.get("name", ""))
        self._bg = ImagePickerWidget(item.get("background", ""))
        self._color = ColorPickerWidget(item.get("text_color", [0, 0, 0]))
        self._font = FontPickerWidget(item.get("text_font", ""))

        self._min_w = QSpinBox()
        self._min_w.setRange(0, 9999)
        self._min_w.setValue(item.get("min_width", 2000))
        self._min_h = QSpinBox()
        self._min_h.setRange(0, 9999)
        self._min_h.setValue(item.get("min_height", 3000))

        self._width_pos = QComboBox()
        self._width_pos.addItems(WIDTH_POS_OPTIONS)
        self._width_pos.setCurrentText(item.get("width_pos", "center"))
        self._height_pos = QComboBox()
        self._height_pos.addItems(HEIGHT_POS_OPTIONS)
        self._height_pos.setCurrentText(item.get("height_pos", "center"))

        self._pad_top = QSpinBox()
        self._pad_top.setRange(0, 9999)
        self._pad_top.setValue(item.get("padding_top", 0))

        form.addRow("Название:", self._name)
        form.addRow("Фон:", self._bg)
        form.addRow("Цвет текста:", self._color)
        form.addRow("Шрифт:", self._font)
        form.addRow("Мин. ширина:", self._min_w)
        form.addRow("Мин. высота:", self._min_h)
        form.addRow("Позиция по X:", self._width_pos)
        form.addRow("Позиция по Y:", self._height_pos)
        form.addRow("Padding top:", self._pad_top)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btns)

    def get_data(self) -> dict:
        d = {
            "name": self._name.text(),
            "text_color": self._color.value(),
            "text_font": self._font.value(),
            "min_width": self._min_w.value(),
            "min_height": self._min_h.value(),
            "width_pos": self._width_pos.currentText(),
            "height_pos": self._height_pos.currentText(),
        }
        bg = self._bg.value()
        if bg:
            d["background"] = bg
        pt = self._pad_top.value()
        if pt:
            d["padding_top"] = pt
        return d


class MonthsTab(QWidget):
    """Tab for editing the months list."""
    changed = Signal()

    def __init__(self, data: list, parent=None):
        super().__init__(parent)
        self._data = data
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        tb = QHBoxLayout()
        btn_add = QPushButton("+ Добавить месяц")
        btn_edit = QPushButton("✏ Изменить")
        btn_del = QPushButton("✕ Удалить")
        btn_up = QPushButton("↑")
        btn_down = QPushButton("↓")
        for b in [btn_add, btn_edit, btn_del, btn_up, btn_down]:
            tb.addWidget(b)
        tb.addStretch()

        btn_add.clicked.connect(self._add)
        btn_edit.clicked.connect(self._edit)
        btn_del.clicked.connect(self._delete)
        btn_up.clicked.connect(self._move_up)
        btn_down.clicked.connect(self._move_down)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._edit)
        self._refresh_list()

        # preview area
        self._preview = PreviewLabel()
        self._preview.setMaximumHeight(200)
        self._list.currentRowChanged.connect(self._on_select)
        btn_preview = QPushButton("Обновить превью")
        btn_preview.clicked.connect(self._update_preview)

        lay.addLayout(tb)

        split = QSplitter(Qt.Horizontal)
        split.addWidget(self._list)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.addWidget(QLabel("<b>Превью месяца</b>"))
        rl.addWidget(self._preview)
        rl.addWidget(btn_preview)
        rl.addStretch()
        split.addWidget(right)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 1)

        lay.addWidget(split)

    def _refresh_list(self):
        cur = self._list.currentRow()
        self._list.clear()
        for i, item in enumerate(self._data):
            name = item.get("name", f"Месяц {i+1}")
            bg = "🖼 " if item.get("background") else "   "
            li = QListWidgetItem(f"  {i+1:02d}.  {bg}{name}")
            c = color_from_list(item.get("text_color", [0, 0, 0]))
            self._list.addItem(li)
        if 0 <= cur < self._list.count():
            self._list.setCurrentRow(cur)

    def _on_select(self, idx):
        self._update_preview()

    def _update_preview(self):
        idx = self._list.currentRow()
        if idx < 0 or idx >= len(self._data):
            self._preview.set_pixmap(None)
            return
        pm = get_month_preview(self._data[idx])
        self._preview.set_pixmap(pm)

    def _add(self):
        dlg = MonthItemDialog({
            "name": "Новый месяц", "text_color": [0, 0, 0],
            "text_font": FONT_PRESETS[0], "min_width": 2000, "min_height": 3000,
            "width_pos": "center", "height_pos": "center"
        }, self)
        if dlg.exec():
            self._data.append(dlg.get_data())
            self._refresh_list()
            self.changed.emit()

    def _edit(self):
        idx = self._list.currentRow()
        if idx < 0:
            return
        dlg = MonthItemDialog(copy.deepcopy(self._data[idx]), self)
        if dlg.exec():
            self._data[idx] = dlg.get_data()
            self._refresh_list()
            self.changed.emit()

    def _delete(self):
        idx = self._list.currentRow()
        if idx < 0:
            return
        reply = QMessageBox.question(self, "Удалить?", "Удалить этот месяц?")
        if reply == QMessageBox.Yes:
            self._data.pop(idx)
            self._refresh_list()
            self.changed.emit()

    def _move_up(self):
        idx = self._list.currentRow()
        if idx <= 0:
            return
        self._data.insert(idx - 1, self._data.pop(idx))
        self._refresh_list()
        self._list.setCurrentRow(idx - 1)
        self.changed.emit()

    def _move_down(self):
        idx = self._list.currentRow()
        if idx < 0 or idx >= len(self._data) - 1:
            return
        self._data.insert(idx + 1, self._data.pop(idx))
        self._refresh_list()
        self._list.setCurrentRow(idx + 1)
        self.changed.emit()

    def get_data(self) -> list:
        return self._data
