"""
Calendar Config Editor — PySide6 UI
====================================
Preview hook functions — replace these with your actual implementations.
Each function receives the relevant config dict and should return a QPixmap.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# PREVIEW HOOK FUNCTIONS — replace bodies with your actual render logic
# ---------------------------------------------------------------------------

def get_day_preview(config: dict) -> "QPixmap | None":
    """Return a QPixmap preview for a regular/weekend/spec day cell config."""
    return None  # Replace with actual render


def get_month_preview(config: dict) -> "QPixmap | None":
    """Return a QPixmap preview for a month page config."""
    return None  # Replace with actual render


# ---------------------------------------------------------------------------

import sys
import json
import copy
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import (
    QColor, QFont, QPixmap, QPainter, QIcon, QBrush, QPen,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTabWidget,
    QScrollArea, QFrame, QFileDialog, QColorDialog, QComboBox,
    QGroupBox, QSizePolicy, QSplitter, QListWidget, QListWidgetItem,
    QMessageBox, QDialog, QDialogButtonBox, QToolButton, QGridLayout,
    QInputDialog,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DAYS_OF_WEEK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

FONT_PRESETS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/mistral.ttf",
    "C:/Windows/Fonts/times.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/georgia.ttf",
]

ALIGN_OPTIONS = ["left", "center", "right"]
WIDTH_POS_OPTIONS = ["left", "center", "right"]
HEIGHT_POS_OPTIONS = ["top", "center", "bottom"]


def color_from_list(lst: list) -> QColor:
    if lst and len(lst) >= 3:
        return QColor(lst[0], lst[1], lst[2])
    return QColor(0, 0, 0)


def list_from_color(c: QColor) -> list:
    return [c.red(), c.green(), c.blue()]


def color_swatch(color: QColor, size: int = 22) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(color)
    p = QPainter(pm)
    p.setPen(QPen(QColor(180, 180, 180)))
    p.drawRect(0, 0, size - 1, size - 1)
    p.end()
    return pm


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------

class ColorPickerWidget(QWidget):
    colorChanged = Signal(list)

    def __init__(self, value: list = None, parent=None):
        super().__init__(parent)
        self._color = color_from_list(value or [0, 0, 0])
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._swatch = QLabel()
        self._swatch.setFixedSize(22, 22)
        self._btn = QPushButton("Выбрать цвет")
        self._btn.setFixedHeight(24)
        self._val_label = QLabel()
        self._btn.clicked.connect(self._pick)
        lay.addWidget(self._swatch)
        lay.addWidget(self._btn)
        lay.addWidget(self._val_label)
        lay.addStretch()
        self._refresh()

    def _refresh(self):
        self._swatch.setPixmap(color_swatch(self._color))
        rgb = list_from_color(self._color)
        self._val_label.setText(f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})")

    def _pick(self):
        c = QColorDialog.getColor(self._color, self, "Выбрать цвет")
        if c.isValid():
            self._color = c
            self._refresh()
            self.colorChanged.emit(list_from_color(self._color))

    def value(self) -> list:
        return list_from_color(self._color)

    def set_value(self, lst: list):
        self._color = color_from_list(lst)
        self._refresh()


class ImagePickerWidget(QWidget):
    pathChanged = Signal(str)

    def __init__(self, value: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._edit = QLineEdit(value or "")
        self._edit.setPlaceholderText("Путь к изображению…")
        self._btn = QPushButton("…")
        self._btn.setFixedWidth(32)
        self._btn.clicked.connect(self._pick)
        self._edit.textChanged.connect(self.pathChanged)
        lay.addWidget(self._edit)
        lay.addWidget(self._btn)

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self._edit.setText(path)

    def value(self) -> str:
        return self._edit.text()

    def set_value(self, v: str):
        self._edit.setText(v or "")


class FontPickerWidget(QWidget):
    fontChanged = Signal(str)

    def __init__(self, value: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._combo = QComboBox()
        self._combo.setEditable(True)
        self._combo.addItems(FONT_PRESETS)
        self._combo.setCurrentText(value or "")
        self._browse = QPushButton("…")
        self._browse.setFixedWidth(32)
        self._browse.clicked.connect(self._pick)
        self._combo.currentTextChanged.connect(self.fontChanged)
        lay.addWidget(self._combo, 1)
        lay.addWidget(self._browse)

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать шрифт", "C:/Windows/Fonts", "Fonts (*.ttf *.otf)"
        )
        if path:
            self._combo.setCurrentText(path)

    def value(self) -> str:
        return self._combo.currentText()

    def set_value(self, v: str):
        self._combo.setCurrentText(v or "")


class PreviewLabel(QLabel):
    """Shows preview pixmap or placeholder."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 160)
        self.setMaximumHeight(320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setStyleSheet(
            "background:#1e1e2e; border:1px solid #3a3a5c; border-radius:6px; color:#888;"
        )
        self.setText("Превью\nнедоступно")

    def set_pixmap(self, pm: QPixmap | None):
        if pm and not pm.isNull():
            self.setPixmap(pm.scaled(self.width() - 8, self.height() - 8,
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setText("")
        else:
            self.setPixmap(QPixmap())
            self.setText("Превью\nнедоступно")


# ---------------------------------------------------------------------------
# Generic section editors
# ---------------------------------------------------------------------------

class DaySectionEditor(QWidget):
    """Editor for day_of_the_week / regular_day / spec_day / weekend sections."""
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


# ---------------------------------------------------------------------------
# Spec Days editor
# ---------------------------------------------------------------------------

class SpecDayItemEditor(QDialog):
    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Особый день")
        self.setMinimumWidth(460)
        self._data = item

        form = QFormLayout()

        self._date = QLineEdit(item.get("date", ""))
        self._name = QLineEdit(item.get("name", ""))
        self._desc = QLineEdit(item.get("desc", ""))
        self._color = ColorPickerWidget(item.get("text_color", [255, 0, 0]))
        self._bg = ImagePickerWidget(item.get("background", ""))

        form.addRow("Дата (дд.мм):", self._date)
        form.addRow("Название:", self._name)
        form.addRow("Описание:", self._desc)
        form.addRow("Цвет текста:", self._color)
        form.addRow("Фон:", self._bg)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btns)

    def get_data(self) -> dict:
        return {
            "date": self._date.text(),
            "name": self._name.text(),
            "desc": self._desc.text(),
            "text_color": self._color.value(),
            "background": self._bg.value(),
        }


class SpecDaysEditor(QWidget):
    changed = Signal()

    def __init__(self, data: list, parent=None):
        super().__init__(parent)
        self._data = data
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # toolbar
        tb = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_edit = QPushButton("✏ Изменить")
        btn_del = QPushButton("✕ Удалить")
        btn_add.clicked.connect(self._add)
        btn_edit.clicked.connect(self._edit)
        btn_del.clicked.connect(self._delete)
        tb.addWidget(btn_add)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_del)
        tb.addStretch()

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._edit)
        self._refresh_list()

        lay.addLayout(tb)
        lay.addWidget(self._list)

    def _refresh_list(self):
        self._list.clear()
        for item in self._data:
            date = item.get("date", "?")
            name = item.get("name", "")
            li = QListWidgetItem(f"  {date}  —  {name}")
            c = color_from_list(item.get("text_color", [0, 0, 0]))
            li.setForeground(QBrush(c))
            self._list.addItem(li)

    def _add(self):
        dlg = SpecDayItemEditor({
            "date": "01.01", "name": "", "desc": "",
            "text_color": [255, 0, 0], "background": ""
        }, self)
        if dlg.exec():
            entry = dlg.get_data()
            if not entry["background"]:
                del entry["background"]
            self._data.append(entry)
            self._refresh_list()
            self.changed.emit()

    def _edit(self):
        idx = self._list.currentRow()
        if idx < 0:
            return
        dlg = SpecDayItemEditor(copy.deepcopy(self._data[idx]), self)
        if dlg.exec():
            entry = dlg.get_data()
            if not entry["background"]:
                del entry["background"]
            self._data[idx] = entry
            self._refresh_list()
            self.changed.emit()

    def _delete(self):
        idx = self._list.currentRow()
        if idx < 0:
            return
        reply = QMessageBox.question(self, "Удалить?", "Удалить этот особый день?")
        if reply == QMessageBox.Yes:
            self._data.pop(idx)
            self._refresh_list()
            self.changed.emit()

    def get_data(self) -> list:
        return self._data


# ---------------------------------------------------------------------------
# Months editor
# ---------------------------------------------------------------------------

class MonthItemEditor(QDialog):
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

        self._min_w = QSpinBox(); self._min_w.setRange(0, 9999); self._min_w.setValue(item.get("min_width", 2000))
        self._min_h = QSpinBox(); self._min_h.setRange(0, 9999); self._min_h.setValue(item.get("min_height", 3000))

        self._width_pos = QComboBox(); self._width_pos.addItems(WIDTH_POS_OPTIONS)
        self._width_pos.setCurrentText(item.get("width_pos", "center"))
        self._height_pos = QComboBox(); self._height_pos.addItems(HEIGHT_POS_OPTIONS)
        self._height_pos.setCurrentText(item.get("height_pos", "center"))

        self._pad_top = QSpinBox(); self._pad_top.setRange(0, 9999); self._pad_top.setValue(item.get("padding_top", 0))

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
        if bg: d["background"] = bg
        pt = self._pad_top.value()
        if pt: d["padding_top"] = pt
        return d


class MonthsEditor(QWidget):
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
        dlg = MonthItemEditor({
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
        if idx < 0: return
        dlg = MonthItemEditor(copy.deepcopy(self._data[idx]), self)
        if dlg.exec():
            self._data[idx] = dlg.get_data()
            self._refresh_list()
            self.changed.emit()

    def _delete(self):
        idx = self._list.currentRow()
        if idx < 0: return
        reply = QMessageBox.question(self, "Удалить?", "Удалить этот месяц?")
        if reply == QMessageBox.Yes:
            self._data.pop(idx)
            self._refresh_list()
            self.changed.emit()

    def _move_up(self):
        idx = self._list.currentRow()
        if idx <= 0: return
        self._data.insert(idx - 1, self._data.pop(idx))
        self._refresh_list()
        self._list.setCurrentRow(idx - 1)
        self.changed.emit()

    def _move_down(self):
        idx = self._list.currentRow()
        if idx < 0 or idx >= len(self._data) - 1: return
        self._data.insert(idx + 1, self._data.pop(idx))
        self._refresh_list()
        self._list.setCurrentRow(idx + 1)
        self.changed.emit()

    def get_data(self) -> list:
        return self._data


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

STYLESHEET = """
QMainWindow, QDialog {
    background: #16161e;
}
QWidget {
    background: #16161e;
    color: #c9c9d9;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #2e2e48;
    border-radius: 6px;
    background: #1c1c2a;
}
QTabBar::tab {
    background: #1c1c2a;
    color: #888;
    padding: 8px 18px;
    border: 1px solid transparent;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    min-width: 100px;
}
QTabBar::tab:selected {
    background: #2a2a42;
    color: #e0d9ff;
    border-color: #3a3a60;
}
QTabBar::tab:hover:!selected {
    background: #222236;
    color: #bbb;
}
QPushButton {
    background: #2a2a42;
    color: #c9c9d9;
    border: 1px solid #3a3a5c;
    border-radius: 5px;
    padding: 5px 14px;
    min-height: 26px;
}
QPushButton:hover {
    background: #35355a;
    border-color: #5a5aaa;
    color: #e0d9ff;
}
QPushButton:pressed {
    background: #22223a;
}
QLineEdit, QSpinBox, QComboBox {
    background: #22223a;
    border: 1px solid #3a3a5c;
    border-radius: 4px;
    padding: 4px 8px;
    color: #d0d0e8;
    selection-background-color: #5555aa;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #7070cc;
}
QListWidget {
    background: #1a1a2e;
    border: 1px solid #2e2e48;
    border-radius: 5px;
    outline: none;
}
QListWidget::item {
    padding: 8px 6px;
    border-bottom: 1px solid #22223a;
}
QListWidget::item:selected {
    background: #2e2e55;
    color: #e0d9ff;
}
QListWidget::item:hover:!selected {
    background: #22223a;
}
QGroupBox {
    border: 1px solid #2e2e48;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    color: #9090c0;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QScrollBar:vertical {
    background: #16161e;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #3a3a5c;
    border-radius: 4px;
    min-height: 20px;
}
QSplitter::handle {
    background: #2e2e48;
    width: 2px;
}
QLabel[class="section-title"] {
    font-size: 15px;
    font-weight: bold;
    color: #a0a0d0;
    padding: 4px 0;
}
QFormLayout > QLabel {
    color: #8888b0;
}
QMessageBox {
    background: #1c1c2a;
}
"""


class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self.setWindowTitle("Редактор конфигурации календаря")
        self.setMinimumSize(920, 680)
        self.resize(1120, 750)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        # --- header ---
        header = QHBoxLayout()
        title = QLabel("📅  Конфигурация календаря")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#b0b0e0;")
        header.addWidget(title)
        header.addStretch()
        btn_load = QPushButton("📂 Открыть JSON")
        btn_save = QPushButton("💾 Сохранить JSON")
        btn_load.clicked.connect(self._load_json)
        btn_save.clicked.connect(self._save_json)
        header.addWidget(btn_load)
        header.addWidget(btn_save)
        root.addLayout(header)

        # --- tabs ---
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.North)

        sections = [
            ("day_of_the_week", "📆 День недели"),
            ("regular_day",     "🗓 Обычный день"),
            ("weekend",         "🌅 Выходной"),
            ("spec_day",        "⭐ Особый день"),
            ("month",           "📖 Месяц (шаблон)"),
        ]

        self._day_editors: dict[str, DaySectionEditor] = {}
        for key, label in sections:
            if key in self._config:
                ed = DaySectionEditor(
                    self._config[key],
                    show_preview_fn=get_day_preview if key != "month" else get_month_preview,
                )
                ed.changed.connect(self._on_changed)
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(ed)
                self._tabs.addTab(scroll, label)
                self._day_editors[key] = ed

        # spec_days
        self._spec_days_ed = SpecDaysEditor(self._config.get("spec_days", []))
        self._spec_days_ed.changed.connect(self._on_changed)
        self._tabs.addTab(self._spec_days_ed, "🎉 Особые дни")

        # months
        self._months_ed = MonthsEditor(self._config.get("months", []))
        self._months_ed.changed.connect(self._on_changed)
        self._tabs.addTab(self._months_ed, "🗂 Месяцы")

        root.addWidget(self._tabs)

        # status bar
        self._status = QLabel("Готово.")
        self._status.setStyleSheet("color:#5a5a8a; font-size:11px;")
        root.addWidget(self._status)

    def _on_changed(self):
        self._status.setText("Есть несохранённые изменения.")

    def _collect_config(self) -> dict:
        cfg = copy.deepcopy(self._config)
        for key, ed in self._day_editors.items():
            cfg[key] = ed.get_data()
        cfg["spec_days"] = self._spec_days_ed.get_data()
        cfg["months"] = self._months_ed.get_data()
        return cfg

    def _save_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить конфигурацию", "calendar_config.json",
            "JSON files (*.json)"
        )
        if not path:
            return
        cfg = self._collect_config()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
        self._status.setText(f"Сохранено: {path}")

    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть конфигурацию", "", "JSON files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                new_cfg = json.load(f)
            # rebuild UI
            self._config = new_cfg
            old_tabs = self._tabs
            self._build()
            self._status.setText(f"Загружено: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "day_of_the_week": {
        "width": 200, "height": 50, "text_color": [0, 0, 0],
        "text_position": [40, 40], "text_size": 48, "text_align": "center",
        "text_font": "C:/Windows/Fonts/arial.ttf",
        "background": "assets/img/day_background.png"
    },
    "month": {
        "gap": 30, "text_color": [0, 0, 0], "text_position": [40, 40],
        "text_size": 98, "text_font": "C:/Windows/Fonts/mistral.ttf",
        "text_align": "center", "month_text_height": 200,
        "padding_top": 80, "padding_right": 80, "padding_bottom": 80, "padding_left": 80,
        "background": "assets/img/test_bg (1).jpg"
    },
    "regular_day": {
        "width": 200, "height": 200, "text_color": [0, 0, 0],
        "text_position": [40, 40], "text_size": 48, "text_align": "center",
        "padding": 20, "text_font": "C:/Windows/Fonts/arial.ttf",
        "background": "assets/img/day_background.png"
    },
    "spec_day": {
        "width": 200, "height": 200, "text_color": [255, 0, 255],
        "text_position": [40, 40], "text_size": 48, "text_align": "center",
        "padding": 20, "text_font": "C:/Windows/Fonts/arial.ttf",
        "background": "assets/img/test.jpg"
    },
    "weekend": {
        "width": 200, "height": 200, "text_color": [255, 0, 0],
        "text_position": [40, 40], "text_size": 48, "padding": 20,
        "text_align": "center", "text_font": "C:/Windows/Fonts/arial.ttf",
        "background": "assets/img/day_weekend_background.png"
    },
    "spec_days": [
        {"date": "07.12", "desc": "", "name": "День рождения Макс", "background": "assets/img/spec_day1.png", "text_color": [255, 0, 0]},
        {"date": "08.03", "desc": "", "name": "Международный женский день", "background": "assets/img/spec_day2.png", "text_color": [255, 0, 0]},
        {"date": "23.02", "desc": "", "name": "День защитника Отечества", "background": "assets/img/d(6).jpg", "text_color": [255, 0, 0]},
        {"date": "14.02", "desc": "", "name": "День святого Валентина", "text_color": [255, 0, 0]}
    ],
    "months": [
        {"name": "Январь", "background": "assets/img/test_bg (2).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "center"},
        {"name": "February", "background": "assets/img/test_bg (1).jpg", "text_color": [255, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "bottom"},
        {"name": "Март", "background": "assets/img/test_bg (1).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "top", "padding_top": 800},
        {"name": "Апрель", "background": "assets/img/test_bg (2).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "right", "height_pos": "center"},
        {"name": "Май", "background": "assets/img/test_bg (1).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "right", "height_pos": "bottom"},
        {"name": "Июнь", "background": "assets/img/test_bg (1).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "right", "height_pos": "top"},
        {"name": "Июль", "background": "assets/img/test_bg (2).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "left", "height_pos": "center"},
        {"name": "Август", "background": "assets/img/test_bg (1).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "left", "height_pos": "bottom"},
        {"name": "Сентябрь", "background": "assets/img/test.jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/mistral.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "left", "height_pos": "top"},
        {"name": "Октябрь", "background": "assets/img/test_bg (2).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/arial.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "top"},
        {"name": "Ноябрь", "background": "assets/img/test_bg (1).jpg", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/arial.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "top"},
        {"name": "Декабрь", "text_color": [0, 0, 0], "text_font": "C:/Windows/Fonts/arial.ttf", "min_width": 2000, "min_height": 3000, "width_pos": "center", "height_pos": "top"}
    ]
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Optionally load from file passed as argument
    config = DEFAULT_CONFIG
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: could not load {sys.argv[1]}: {e}")

    win = MainWindow(config)
    win.show()
    sys.exit(app.exec())