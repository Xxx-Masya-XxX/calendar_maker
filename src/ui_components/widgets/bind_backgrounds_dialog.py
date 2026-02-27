"""Dialog for binding background images to special days."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QFileDialog, QMessageBox, QGroupBox, QProgressBar,
)

from ..widgets import PreviewLabel
from src.utils.background_binder import BackgroundBinder


class BindBackgroundsDialog(QDialog):
    """Dialog for binding generated backgrounds to special days."""

    def __init__(self, spec_days_data: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Привязка фонов к особым дням")
        self.setMinimumSize(700, 600)

        self._spec_days_data = spec_days_data
        self._binder = BackgroundBinder()
        self._bindings = {}  # date -> file path
        self._found_files = {}  # date -> file path

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "Выберите папку с сгенерированными изображениями.\n"
            "Файлы должны иметь формат: spec_DD.MM.png или bg_DD.MM.png"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888;")
        lay.addWidget(info_label)

        # Folder selection
        folder_layout = QHBoxLayout()
        self._folder_edit = QLabel("Папка не выбрана")
        self._folder_edit.setStyleSheet("color: #aaa;")
        btn_browse = QPushButton("📁 Выбрать папку")
        btn_browse.clicked.connect(self._browse_folder)
        folder_layout.addWidget(QLabel("Папка:"))
        folder_layout.addWidget(self._folder_edit, 1)
        folder_layout.addWidget(btn_browse)
        lay.addLayout(folder_layout)

        # Scan button
        self._btn_scan = QPushButton("🔍 Сканировать папку")
        self._btn_scan.clicked.connect(self._scan_folder)
        self._btn_scan.setEnabled(False)
        lay.addWidget(self._btn_scan)

        # Bindings list
        list_group = QGroupBox("Найдено соответствий:")
        list_layout = QVBoxLayout(list_group)

        self._bindings_list = QListWidget()
        self._bindings_list.setMaximumHeight(300)
        list_layout.addWidget(self._bindings_list)

        lay.addWidget(list_group)

        # Preview
        preview_group = QGroupBox("Предпросмотр:")
        preview_layout = QVBoxLayout(preview_group)

        self._preview_info = QLabel("Выберите элемент для предпросмотра")
        self._preview_info.setStyleSheet("color: #888;")
        preview_layout.addWidget(self._preview_info)

        self._preview = PreviewLabel()
        self._preview.setMinimumSize(200, 200)
        preview_layout.addWidget(self._preview)

        lay.addWidget(preview_group)

        # Stats
        self._stats_label = QLabel("")
        self._stats_label.setStyleSheet("color: #888; font-size: 11px;")
        lay.addWidget(self._stats_label)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btns.button(QDialogButtonBox.Ok).setText("✅ Применить привязку")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку с изображениями", ""
        )
        if folder:
            self._folder_edit.setText(folder)
            self._folder_edit.setStyleSheet("color: #c9c9d9;")
            self._btn_scan.setEnabled(True)

    def _scan_folder(self):
        """Scan folder for matching images."""
        folder = self._folder_edit.text()
        if not folder or not Path(folder).exists():
            QMessageBox.warning(self, "Ошибка", "Папка не существует")
            return

        print(f"[BindDialog] Scanning folder: {folder}")
        
        # Scan for files
        self._found_files = self._binder.scan_folder(folder)
        print(f"[BindDialog] Found files: {self._found_files}")

        # Find matches with spec days
        self._bindings = {}
        for entry in self._spec_days_data:
            date = entry.get('date', '')
            print(f"[BindDialog] Checking date: {date}")
            if date in self._found_files:
                self._bindings[date] = self._found_files[date]
                print(f"[BindDialog] Match found for {date}: {self._found_files[date]}")

        print(f"[BindDialog] Total bindings: {len(self._bindings)}")

        # Update list
        self._bindings_list.clear()
        for entry in self._spec_days_data:
            date = entry.get('date', '?')
            name = entry.get('name', '')
            bg_path = self._bindings.get(date)

            if bg_path:
                item_text = f"✓ {date} — {name} → {Path(bg_path).name}"
                item = QListWidgetItem(item_text)
                item.setForeground(Qt.green)
            else:
                item_text = f"✗ {date} — {name} (нет файла)"
                item = QListWidgetItem(item_text)
                item.setForeground(Qt.gray)

            item.setData(Qt.UserRole, {'date': date, 'name': name, 'background': bg_path})
            self._bindings_list.addItem(item)

        # Update stats
        total = len(self._spec_days_data)
        bound = len(self._bindings)
        self._stats_label.setText(f"Привязано: {bound} из {total} дней")

        # Connect selection to preview
        self._bindings_list.itemClicked.connect(self._show_preview)

    def _show_preview(self, item: QListWidgetItem):
        """Show preview for selected item."""
        data = item.data(Qt.UserRole)
        if not data:
            return

        date = data.get('date', '')
        name = data.get('name', '')
        bg_path = data.get('background')

        if bg_path and Path(bg_path).exists():
            self._preview_info.setText(f"{date} — {name}\n{Path(bg_path).name}")
            pixmap = QPixmap(bg_path)
            self._preview.set_pixmap(pixmap)
        else:
            self._preview_info.setText(f"{date} — {name}\nФайл не найден")
            self._preview.set_pixmap(None)

    def _on_accept(self):
        """Apply bindings."""
        if not self._bindings:
            reply = QMessageBox.question(
                self, "Нет привязок",
                "Не найдено совпадений. Всё равно продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.reject()
                return

        self.accept()

    def get_bindings(self) -> dict:
        """Return bindings dict."""
        return self._bindings

    def get_updated_spec_days(self) -> list:
        """Return updated spec_days list with bindings."""
        updated = []
        for entry in self._spec_days_data:
            new_entry = entry.copy()
            date = entry.get('date', '')
            if date in self._bindings:
                new_entry['background'] = self._bindings[date]
            updated.append(new_entry)
        return updated
