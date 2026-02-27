"""Special days tab for Calendar Config Editor."""

import copy
from PySide6.QtCore import Signal
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QMessageBox, QTextEdit, QSplitter, QGroupBox,
)

from ..helpers import color_from_list
from ..widgets import (
    ColorPickerWidget, ImagePickerWidget, FontPickerWidget,
    GenerateSpecDaysDialog, BindBackgroundsDialog
)

from src.utils.text_parser import parse_spec_days_text, validate_parsed_entries


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


class ImportTextDialog(QDialog):
    """Dialog for importing spec days from text format."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт из текста")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # Instructions
        info_label = QLabel(
            "Вставьте текст в формате:\n"
            "Январь:\n"
            "16.01 - Настя Чанкина\n"
            "19.01 - б.Фая Мацик\n\n"
            "Поддерживаются форматы с разделителем ' - ' и без него."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Text input
        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText("Вставьте ваш текст здесь...")
        layout.addWidget(self._text_edit)

        # Preview section
        preview_group = QGroupBox("Предпросмотр (будет добавлено):")
        preview_layout = QVBoxLayout(preview_group)
        
        self._preview_list = QListWidget()
        self._preview_list.setMaximumHeight(150)
        preview_layout.addWidget(self._preview_list)

        layout.addWidget(preview_group)

        # Buttons
        self._btn_preview = QPushButton("🔍 Предпросмотр")
        self._btn_preview.clicked.connect(self._update_preview)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self._btn_preview)
        btn_layout.addStretch()
        btn_layout.addWidget(btns)
        layout.addLayout(btn_layout)

        self._parsed_entries = []

    def _update_preview(self):
        """Update preview list with parsed entries."""
        text = self._text_edit.toPlainText()
        self._parsed_entries = parse_spec_days_text(text)
        
        self._preview_list.clear()
        warnings = validate_parsed_entries(self._parsed_entries)
        
        for entry in self._parsed_entries:
            date = entry.get("date", "?")
            name = entry.get("name", "")
            desc = entry.get("desc", "")
            self._preview_list.addItem(f"{date} — {name} ({desc})")
        
        if warnings:
            self._preview_list.addItem("---")
            for warning in warnings:
                self._preview_list.addItem(f"⚠ {warning}")

    def _on_accept(self):
        """Validate and accept."""
        text = self._text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Ошибка", "Введите текст для импорта")
            return
        
        self._parsed_entries = parse_spec_days_text(text)
        if not self._parsed_entries:
            QMessageBox.warning(self, "Ошибка", "Не удалось распознать ни одной записи")
            return
        
        self.accept()

    def get_entries(self) -> list:
        """Return parsed entries."""
        return self._parsed_entries


class SpecDaysTab(QWidget):
    """Tab for editing the spec_days list."""
    changed = Signal()

    def __init__(self, data: list, config: dict = None, parent=None):
        super().__init__(parent)
        self._data = data
        self._config = config or {}
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # toolbar
        tb = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_edit = QPushButton("✏ Изменить")
        btn_del = QPushButton("✕ Удалить")
        btn_import = QPushButton("📥 Импорт из текста")
        btn_generate = QPushButton("🖼 Генерировать изображения")
        btn_bind_bg = QPushButton("🔗 Привязать фоны")
        btn_add.clicked.connect(self._add)
        btn_edit.clicked.connect(self._edit)
        btn_del.clicked.connect(self._delete)
        btn_import.clicked.connect(self._import)
        btn_generate.clicked.connect(self._generate)
        btn_bind_bg.clicked.connect(self._bind_backgrounds)
        tb.addWidget(btn_add)
        tb.addWidget(btn_edit)
        tb.addWidget(btn_del)
        tb.addWidget(btn_import)
        tb.addWidget(btn_generate)
        tb.addWidget(btn_bind_bg)
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

    def _import(self):
        """Import spec days from text format."""
        dlg = ImportTextDialog(self)
        if dlg.exec() == QDialog.Accepted:
            entries = dlg.get_entries()
            self._data.extend(entries)
            self._refresh_list()
            self.changed.emit()
            QMessageBox.information(
                self,
                "Импорт завершен",
                f"Добавлено {len(entries)} записей"
            )

    def _generate(self):
        """Generate spec day images."""
        if not self._data:
            QMessageBox.warning(self, "Ошибка", "Список особых дней пуст")
            return

        # Get spec_day config from stored config or use defaults
        day_config = self._config.get('spec_day', {
            'width': 200,
            'height': 200,
            'text_color': [255, 0, 255],
            'text_position': [40, 40],
            'text_size': 48,
            'text_align': 'center',
            'text_font': 'C:/Windows/Fonts/arial.ttf',
            'background': 'assets/img/test.jpg',
        })

        dlg = GenerateSpecDaysDialog(self._data, day_config, self)
        if dlg.exec() == QDialog.Accepted:
            pass  # Generation already handled in dialog

    def _bind_backgrounds(self):
        """Bind generated background images to special days."""
        if not self._data:
            QMessageBox.warning(self, "Ошибка", "Список особых дней пуст")
            return

        dlg = BindBackgroundsDialog(self._data, self)
        if dlg.exec() == QDialog.Accepted:
            # Update spec_days with new bindings
            updated_days = dlg.get_updated_spec_days()
            bindings = dlg.get_bindings()
            
            if bindings:
                self._data.clear()
                self._data.extend(updated_days)
                self._refresh_list()
                self.changed.emit()
                QMessageBox.information(
                    self,
                    "Привязка завершена",
                    f"Привязано {len(bindings)} фонов к особым дням"
                )
            else:
                QMessageBox.information(
                    self,
                    "Привязка завершена",
                    "Не найдено файлов для привязки"
                )

    def get_data(self) -> list:
        return self._data
