"""Special days tab for Calendar Config Editor."""

import copy
from PySide6.QtCore import Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QMessageBox,
)

from ..helpers import color_from_list
from ..widgets import ColorPickerWidget, ImagePickerWidget


class SpecDayItemDialog(QDialog):
    """Dialog for editing a single special day item."""

    def __init__(self, item: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Особый день")
        self.setMinimumWidth(460)
        self._data = item

        form = QFormLayout()

        self._date = QLabel(item.get("date", ""))
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


class SpecDaysTab(QWidget):
    """Tab for editing the spec_days list."""
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
        dlg = SpecDayItemDialog({
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
        dlg = SpecDayItemDialog(copy.deepcopy(self._data[idx]), self)
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
