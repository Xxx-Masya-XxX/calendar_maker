"""Dialog for generating special day images."""

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox, QSpinBox, QComboBox,
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
        self.setMinimumSize(700, 650)

        self._spec_days_data = spec_days_data
        self._day_config = day_config

        # Extract default values from config
        self._default_bg = day_config.get('background', '')
        self._default_color = day_config.get('text_color', [255, 0, 255])
        self._default_font = day_config.get('text_font', 'C:/Windows/Fonts/arial.ttf')
        self._default_size = day_config.get('text_size', 48)
        self._default_pos = day_config.get('text_position', [40, 40])
        self._default_align = day_config.get('text_align', 'center')
        self._default_width = day_config.get('width', 200)
        self._default_height = day_config.get('height', 200)

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)

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

        # Text color
        self._color_picker = ColorPickerWidget(self._default_color)
        settings_layout.addRow("Цвет текста:", self._color_picker)

        # Font
        self._font_picker = FontPickerWidget(self._default_font)
        settings_layout.addRow("Шрифт:", self._font_picker)

        # Font size
        self._font_size = QSpinBox()
        self._font_size.setRange(10, 200)
        self._font_size.setValue(self._default_size)
        settings_layout.addRow("Размер шрифта:", self._font_size)

        # Text position X
        self._pos_x = QSpinBox()
        self._pos_x.setRange(0, 500)
        self._pos_x.setValue(self._default_pos[0] if len(self._default_pos) > 0 else 40)
        settings_layout.addRow("Позиция X:", self._pos_x)

        # Text position Y
        self._pos_y = QSpinBox()
        self._pos_y.setRange(0, 500)
        self._pos_y.setValue(self._default_pos[1] if len(self._default_pos) > 1 else 40)
        settings_layout.addRow("Позиция Y:", self._pos_y)

        # Text align
        self._text_align = QComboBox()
        self._text_align.addItems(["left", "center", "right"])
        self._text_align.setCurrentText(self._default_align)
        settings_layout.addRow("Выравнивание:", self._text_align)

        settings_group.setLayout(settings_layout)
        lay.addWidget(settings_group)

        # Preview group
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout(preview_group)

        # Selected day for preview
        self._preview_selector = QComboBox()
        self._preview_selector.currentIndexChanged.connect(self._update_preview)
        preview_layout.addWidget(self._preview_selector)

        # Preview label
        self._preview = PreviewLabel()
        self._preview.setMinimumSize(300, 300)
        preview_layout.addWidget(self._preview)

        lay.addWidget(preview_group)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        btns.button(QDialogButtonBox.Save).setText("💾 Сгенерировать все")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        # Populate selector
        self._populate_selector()

    def _populate_selector(self):
        """Populate preview selector with spec days."""
        self._preview_selector.clear()
        for item in self._spec_days_data:
            date = item.get("date", "?")
            name = item.get("name", "")
            self._preview_selector.addItem(f"{date} — {name}")

    def _get_current_settings(self) -> dict:
        """Get current settings from UI."""
        return {
            'width': self._img_width.value(),
            'height': self._img_height.value(),
            'background': self._bg_picker.value(),
            'text_color': self._color_picker.value(),
            'text_font': self._font_picker.value(),
            'text_size': self._font_size.value(),
            'text_position': [self._pos_x.value(), self._pos_y.value()],
            'text_align': self._text_align.currentText(),
        }

    def _update_preview(self):
        """Update preview based on selected item and current settings."""
        idx = self._preview_selector.currentIndex()
        if idx < 0 or len(self._spec_days_data) == 0:
            return

        settings = self._get_current_settings()

        # Get day and month from date
        item = self._spec_days_data[idx]
        date = item.get("date", "01.01")
        parts = date.split('.')
        day = int(parts[0])
        month = int(parts[1])

        # Create generator
        generator = SpecDayGenerator(
            width=settings['width'],
            height=settings['height'],
            background=settings['background'],
            text_color=settings['text_color'],
            text_font=settings['text_font'],
            text_size=settings['text_size'],
            text_position=settings['text_position'],
            text_align=settings['text_align'],
        )

        # Generate image
        day_img = generator.generate(day, month)

        # Convert to QPixmap
        h, w, ch = day_img.shape
        bgra = cv2_to_rgb(day_img)
        bytes_per_line = ch * w
        qimg = QPixmap.fromImage(
            QImage(bgra.data, w, h, bytes_per_line, QImage.Format_RGB888)
        )
        self._preview.set_pixmap(qimg)

    def _on_accept(self):
        """Generate all images."""
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
            text_color=settings['text_color'],
            text_font=settings['text_font'],
            text_size=settings['text_size'],
            text_position=settings['text_position'],
            text_align=settings['text_align'],
        )

        # Generate batch
        generated_files = generator.generate_batch(self._spec_days_data, output_dir)

        QMessageBox.information(
            self,
            "Генерация завершена",
            f"Сгенерировано {len(generated_files)} изображений"
        )
        self.accept()
