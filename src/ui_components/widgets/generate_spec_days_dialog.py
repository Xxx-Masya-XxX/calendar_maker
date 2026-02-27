"""Dialog for generating special day images."""

import cv2
import numpy as np
from typing import List
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox, QSpinBox, QComboBox,
    QSplitter, QScrollArea,
)

from ..helpers import color_from_list
from ..widgets import ColorPickerWidget, ImagePickerWidget, PreviewLabel, FontPickerWidget

from src.utils.spec_day_generator import SpecDayGenerator


def cv2_to_rgb(img: np.ndarray) -> np.ndarray:
    """Convert BGR image to RGB."""
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)


class GenerateSpecDaysDialog(QDialog):
    """Dialog for generating special day preview images."""

    def __init__(self, spec_days_data: list, day_config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генерация изображений спец дней")
        self.setMinimumSize(900, 750)
        self.resize(1000, 800)

        self._spec_days_data = spec_days_data
        self._day_config = day_config

        # Group data by date
        self._grouped_data = SpecDayGenerator.group_by_date(spec_days_data)
        self._unique_dates = list(self._grouped_data.keys())

        # Extract default values from config
        self._default_bg = day_config.get('background', '')
        self._default_color = day_config.get('text_color', [255, 0, 255])
        self._default_font = day_config.get('text_font', 'C:/Windows/Fonts/arial.ttf')
        self._default_size = day_config.get('text_size', 48)
        self._default_pos = day_config.get('text_position', [40, 40])
        self._default_align = day_config.get('text_align', 'center')
        self._default_width = day_config.get('width', 200)
        self._default_height = day_config.get('height', 200)
        
        # Name text defaults
        self._default_name_text = "{name}"
        self._default_name_font = self._default_font
        self._default_name_size = 28
        self._default_name_pos = [40, 100]
        self._default_name_color = [255, 255, 255]
        self._default_name_line_spacing = 5

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

        # Main splitter (left: dates, right: settings + preview)
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Date selection
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        select_label = QLabel("Выберите даты для генерации:")
        select_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(select_label)

        # Select all / Deselect all buttons
        select_btn_layout = QHBoxLayout()
        self._btn_select_all = QPushButton("Выбрать все")
        self._btn_deselect_all = QPushButton("Снять все")
        self._btn_select_all.clicked.connect(self._select_all)
        self._btn_deselect_all.clicked.connect(self._deselect_all)
        select_btn_layout.addWidget(self._btn_select_all)
        select_btn_layout.addWidget(self._btn_deselect_all)
        select_btn_layout.addStretch()
        left_layout.addLayout(select_btn_layout)

        # Date list with checkboxes
        self._date_list = QListWidget()
        self._date_list.setMaximumWidth(300)
        self._date_list.itemChanged.connect(self._on_date_selection_changed)
        self._date_list.currentRowChanged.connect(self._update_preview)
        left_layout.addWidget(self._date_list)

        # Stats label
        self._stats_label = QLabel("")
        self._stats_label.setStyleSheet("color: #888; font-size: 11px;")
        left_layout.addWidget(self._stats_label)

        splitter.addWidget(left_widget)

        # Right side: Settings + Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)
        scroll_content_layout.setContentsMargins(5, 5, 5, 5)
        scroll_content_layout.setSpacing(10)

        # Settings group
        settings_group = QGroupBox("Настройки генерации")
        settings_layout = QFormLayout()

        # Image dimensions
        self._img_width = QSpinBox()
        self._img_width.setRange(50, 2000)
        self._img_width.setValue(self._default_width)
        settings_layout.addRow("Ширина (px):", self._img_width)

        self._img_height = QSpinBox()
        self._img_height.setRange(50, 2000)
        self._img_height.setValue(self._default_height)
        settings_layout.addRow("Высота (px):", self._img_height)

        # Background image
        self._bg_picker = ImagePickerWidget(self._default_bg)
        settings_layout.addRow("Фон:", self._bg_picker)

        settings_group.setLayout(settings_layout)
        scroll_content_layout.addWidget(settings_group)
        
        # Connect settings changes to preview update
        self._img_width.valueChanged.connect(self._update_preview)
        self._img_height.valueChanged.connect(self._update_preview)
        self._bg_picker.pathChanged.connect(self._update_preview)

        # Day number settings group
        day_group = QGroupBox("Настройки числа дня")
        day_layout = QFormLayout()

        # Render day number checkbox
        self._render_day_number = QCheckBox("Отображать число дня")
        self._render_day_number.setChecked(True)
        day_layout.addRow(self._render_day_number)

        # Day text color
        self._day_color_picker = ColorPickerWidget(self._default_color)
        day_layout.addRow("Цвет числа:", self._day_color_picker)

        # Day font
        self._day_font_picker = FontPickerWidget(self._default_font)
        day_layout.addRow("Шрифт числа:", self._day_font_picker)

        # Day font size
        self._day_font_size = QSpinBox()
        self._day_font_size.setRange(10, 200)
        self._day_font_size.setValue(self._default_size)
        day_layout.addRow("Размер числа:", self._day_font_size)

        # Day text position X
        self._day_pos_x = QSpinBox()
        self._day_pos_x.setRange(0, 500)
        self._day_pos_x.setValue(self._default_pos[0] if len(self._default_pos) > 0 else 40)
        day_layout.addRow("Позиция X:", self._day_pos_x)

        # Day text position Y
        self._day_pos_y = QSpinBox()
        self._day_pos_y.setRange(0, 500)
        self._day_pos_y.setValue(self._default_pos[1] if len(self._default_pos) > 1 else 40)
        day_layout.addRow("Позиция Y:", self._day_pos_y)

        # Day text align
        self._day_text_align = QComboBox()
        self._day_text_align.addItems(["left", "center", "right"])
        self._day_text_align.setCurrentText(self._default_align)
        day_layout.addRow("Выравнивание:", self._day_text_align)

        day_group.setLayout(day_layout)
        scroll_content_layout.addWidget(day_group)
        
        # Connect day settings changes to preview update
        self._day_color_picker.colorChanged.connect(self._update_preview)
        self._day_font_picker.fontChanged.connect(self._update_preview)
        self._day_font_size.valueChanged.connect(self._update_preview)
        self._day_pos_x.valueChanged.connect(self._update_preview)
        self._day_pos_y.valueChanged.connect(self._update_preview)
        self._day_text_align.currentTextChanged.connect(self._update_preview)
        self._render_day_number.stateChanged.connect(self._update_preview)

        # Name text settings group
        name_group = QGroupBox("Настройки текста имён")
        name_layout = QFormLayout()

        # Name text template
        self._name_text_template = QLineEdit(self._default_name_text)
        self._name_text_template.setPlaceholderText("{name}")
        name_layout.addRow("Шаблон текста:", self._name_text_template)

        # Name text color
        self._name_color_picker = ColorPickerWidget(self._default_name_color)
        name_layout.addRow("Цвет текста:", self._name_color_picker)

        # Name font
        self._name_font_picker = FontPickerWidget(self._default_name_font)
        name_layout.addRow("Шрифт:", self._name_font_picker)

        # Name font size
        self._name_font_size = QSpinBox()
        self._name_font_size.setRange(10, 200)
        self._name_font_size.setValue(self._default_name_size)
        name_layout.addRow("Размер шрифта:", self._name_font_size)

        # Name text position X
        self._name_pos_x = QSpinBox()
        self._name_pos_x.setRange(0, 500)
        self._name_pos_x.setValue(self._default_name_pos[0] if len(self._default_name_pos) > 0 else 40)
        name_layout.addRow("Позиция X:", self._name_pos_x)

        # Name text position Y
        self._name_pos_y = QSpinBox()
        self._name_pos_y.setRange(0, 500)
        self._name_pos_y.setValue(self._default_name_pos[1] if len(self._default_name_pos) > 1 else 100)
        name_layout.addRow("Позиция Y:", self._name_pos_y)

        # Name text align
        self._name_align = QComboBox()
        self._name_align.addItems(["left", "center", "right"])
        self._name_align.setCurrentText("center")
        name_layout.addRow("Выравнивание:", self._name_align)

        # Name line spacing
        self._name_line_spacing = QSpinBox()
        self._name_line_spacing.setRange(0, 50)
        self._name_line_spacing.setValue(self._default_name_line_spacing)
        name_layout.addRow("Интервал строк:", self._name_line_spacing)

        name_group.setLayout(name_layout)
        scroll_content_layout.addWidget(name_group)
        
        # Connect name settings changes to preview update
        self._name_text_template.textChanged.connect(self._update_preview)
        self._name_color_picker.colorChanged.connect(self._update_preview)
        self._name_font_picker.fontChanged.connect(self._update_preview)
        self._name_font_size.valueChanged.connect(self._update_preview)
        self._name_pos_x.valueChanged.connect(self._update_preview)
        self._name_pos_y.valueChanged.connect(self._update_preview)
        self._name_align.currentTextChanged.connect(self._update_preview)
        self._name_line_spacing.valueChanged.connect(self._update_preview)

        # Preview group
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout(preview_group)

        # Preview toolbar
        preview_toolbar = QHBoxLayout()
        preview_toolbar.addStretch()

        self._btn_update_preview = QPushButton("🔄 Обновить")
        self._btn_update_preview.setMaximumWidth(120)
        self._btn_update_preview.clicked.connect(self._update_preview)
        preview_toolbar.addWidget(self._btn_update_preview)

        preview_layout.addLayout(preview_toolbar)

        # Info label
        self._preview_info = QLabel("Выберите дату для предпросмотра")
        self._preview_info.setStyleSheet("color: #888;")
        preview_layout.addWidget(self._preview_info)

        # Preview label
        self._preview = PreviewLabel()
        self._preview.setMinimumSize(300, 300)
        preview_layout.addWidget(self._preview)

        preview_group.setLayout(preview_layout)
        scroll_content_layout.addWidget(preview_group)

        scroll.setWidget(scroll_content)
        right_layout.addWidget(scroll)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        lay.addWidget(splitter)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btns.button(QDialogButtonBox.Save).setText("💾 Сгенерировать выбранные")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        
        # Filename pattern input
        filename_layout = QHBoxLayout()
        filename_label = QLabel("Шаблон имени файла:")
        self._filename_pattern = QLineEdit("spec_{date}.png")
        self._filename_pattern.setPlaceholderText("spec_{date}.png")
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self._filename_pattern)
        filename_layout.addStretch()
        
        lay.addLayout(filename_layout)
        lay.addWidget(btns)

        # Populate date list
        self._populate_date_list()
        self._update_stats()
        
        # Auto-select first date and update preview
        if self._date_list.count() > 0:
            self._date_list.setCurrentRow(0)
            # Delay preview update until dialog is shown
            QTimer.singleShot(100, self._update_preview)

    def _populate_date_list(self):
        """Populate date list with checkboxes."""
        self._date_list.clear()
        for date in sorted(self._unique_dates):
            entries = self._grouped_data.get(date, [])
            names = [e.get("name", "") for e in entries]
            
            # Show count of names if more than one
            if len(names) > 1:
                item_text = f"{date} ({len(names)} имён)"
            else:
                item_text = f"{date} ({names[0] if names else ''})"
            
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, date)
            self._date_list.addItem(item)

    def _select_all(self):
        """Select all dates."""
        for i in range(self._date_list.count()):
            item = self._date_list.item(i)
            item.setCheckState(Qt.Checked)
        self._update_stats()

    def _deselect_all(self):
        """Deselect all dates."""
        for i in range(self._date_list.count()):
            item = self._date_list.item(i)
            item.setCheckState(Qt.Unchecked)
        self._update_stats()

    def _on_date_selection_changed(self):
        """Handle date selection change."""
        self._update_stats()

    def _get_selected_dates(self) -> List[str]:
        """Get list of selected dates."""
        selected = []
        for i in range(self._date_list.count()):
            item = self._date_list.item(i)
            if item.checkState() == Qt.Checked:
                date = item.data(Qt.UserRole)
                if date:
                    selected.append(date)
        return selected

    def _update_stats(self):
        """Update statistics label."""
        total = len(self._unique_dates)
        selected = len(self._get_selected_dates())
        total_names = len(self._spec_days_data)
        self._stats_label.setText(f"Выбрано: {selected} из {total} дат (всего имён: {total_names})")

    def _get_current_settings(self) -> dict:
        """Get current settings from UI."""
        return {
            'width': self._img_width.value(),
            'height': self._img_height.value(),
            'background': self._bg_picker.value(),
            # Day number settings
            'render_day_number': self._render_day_number.isChecked(),
            'day_color': self._day_color_picker.value(),
            'day_font': self._day_font_picker.value(),
            'day_size': self._day_font_size.value(),
            'day_position': [self._day_pos_x.value(), self._day_pos_y.value()],
            'day_align': self._day_text_align.currentText(),
            # Name text settings
            'name_text': self._name_text_template.text() or "{name}",
            'name_color': self._name_color_picker.value(),
            'name_font': self._name_font_picker.value(),
            'name_size': self._name_font_size.value(),
            'name_position': [self._name_pos_x.value(), self._name_pos_y.value()],
            'name_align': self._name_align.currentText(),
            'name_line_spacing': self._name_line_spacing.value(),
        }

    def _update_preview(self):
        """Update preview based on selected date and current settings."""
        print("DEBUG: _update_preview called")
        try:
            # Get selected date from list
            current_row = self._date_list.currentRow()
            print(f"DEBUG: current_row = {current_row}")
            if current_row < 0:
                self._preview_info.setText("Выберите дату для предпросмотра")
                self._preview.set_pixmap(None)
                return

            current_item = self._date_list.item(current_row)
            date = current_item.data(Qt.UserRole)
            print(f"DEBUG: date = {date}")
            if not date:
                return

            settings = self._get_current_settings()
            print(f"DEBUG: settings = {settings}")

            # Parse date
            parts = date.split('.')
            day = int(parts[0])
            month = int(parts[1])
            print(f"DEBUG: day={day}, month={month}")

            # Get names for this date
            entries = self._grouped_data.get(date, [])
            names = [e.get("name", "") for e in entries]
            print(f"DEBUG: names = {names}")

            # Update info label
            if len(names) > 1:
                self._preview_info.setText(f"{date} — {len(names)} имён:")
            else:
                self._preview_info.setText(f"{date} — {names[0] if names else ''}")

            # Create generator
            generator = SpecDayGenerator(
                width=settings['width'],
                height=settings['height'],
                background=settings['background'],
                render_day_number=settings['render_day_number'],
                day_color=settings['day_color'],
                day_font=settings['day_font'],
                day_size=settings['day_size'],
                day_position=settings['day_position'],
                day_align=settings['day_align'],
                name_text=settings['name_text'],
                name_color=settings['name_color'],
                name_font=settings['name_font'],
                name_size=settings['name_size'],
                name_position=settings['name_position'],
                name_align=settings['name_align'],
                name_line_spacing=settings['name_line_spacing'],
            )

            print("DEBUG: Creating generator and generating image...")
            # Generate image
            day_img = generator.generate(day, month, names)
            print(f"DEBUG: Generated image shape: {day_img.shape}")

            # Convert to QPixmap
            h, w, ch = day_img.shape
            bgra = cv2_to_rgb(day_img)
            bytes_per_line = ch * w
            qimg = QPixmap.fromImage(
                QImage(bgra.data, w, h, bytes_per_line, QImage.Format_RGB888)
            )
            print(f"DEBUG: QPixmap created, isNull={qimg.isNull()}")
            self._preview.set_pixmap(qimg)
            print("DEBUG: Preview updated successfully")
            
        except Exception as e:
            error_msg = f"Ошибка: {e}"
            print(f"ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            self._preview_info.setText(error_msg)
            self._preview.set_pixmap(None)

    def _on_accept(self):
        """Generate all images."""
        selected_dates = self._get_selected_dates()
        if not selected_dates:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одну дату для генерации")
            return

        output_dir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения", ""
        )
        if not output_dir:
            return

        settings = self._get_current_settings()

        # Create generator
        generator = SpecDayGenerator(
            width=settings['width'],
            height=settings['height'],
            background=settings['background'],
            render_day_number=settings['render_day_number'],
            day_color=settings['day_color'],
            day_font=settings['day_font'],
            day_size=settings['day_size'],
            day_position=settings['day_position'],
            day_align=settings['day_align'],
            name_text=settings['name_text'],
            name_color=settings['name_color'],
            name_font=settings['name_font'],
            name_size=settings['name_size'],
            name_position=settings['name_position'],
            name_align=settings['name_align'],
            name_line_spacing=settings['name_line_spacing'],
        )

        # Generate batch
        generated_files = generator.generate_batch(
            self._spec_days_data,
            output_dir,
            selected_dates=selected_dates,
            filename_pattern=self._filename_pattern.text() or "spec_{date}.png"
        )

        QMessageBox.information(
            self,
            "Генерация завершена",
            f"Сгенерировано {len(generated_files)} изображений"
        )
        self.accept()
