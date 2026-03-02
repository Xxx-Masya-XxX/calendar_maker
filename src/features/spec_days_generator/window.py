"""Main window for Spec Days Generator."""

import json
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QFileDialog, QScrollArea, QSplitter,
    QPlainTextEdit, QMessageBox, QFileDialog as QFDialog
)
from PySide6.QtGui import QPixmap, QImage

import cv2
import numpy as np

from .widgets import TextSettingsWidget, CanvasSettingsWidget
from .generator import generate_spec_day_image, save_spec_day_image


class SpecDaysGeneratorWindow(QWidget):
    """Window for generating spec days images."""
    
    # Signal emitted when generation is complete
    generationComplete = Signal(list)
    
    def __init__(self, spec_days_data: list = None, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Генератор спец дней")
        self.resize(1400, 900)
        
        self._spec_days = spec_days_data or []
        self._current_index = 0
        self._generated_images = {}
        
        self._init_ui()
        self._load_spec_days_list()
    
    def _init_ui(self):
        """Initialize the UI."""
        main_lay = QVBoxLayout(self)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Spec days list and text editor
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Center panel - Settings
        center_panel = self._create_center_panel()
        splitter.addWidget(center_panel)
        
        # Right panel - Preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes
        splitter.setSizes([300, 500, 500])
        
        main_lay.addWidget(splitter)
        
        # Bottom panel - Generate button
        bottom_lay = QHBoxLayout()
        
        self._output_dir_label = QLabel("Выходная папка: не выбрана")
        bottom_lay.addWidget(self._output_dir_label, 1)
        
        self._browse_btn = QPushButton("Обзор...")
        self._browse_btn.setFixedWidth(100)
        self._browse_btn.clicked.connect(self._browse_output_dir)
        bottom_lay.addWidget(self._browse_btn)
        
        self._generate_btn = QPushButton("Сгенерировать все")
        self._generate_btn.setFixedWidth(150)
        self._generate_btn.clicked.connect(self._generate_all)
        self._generate_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        bottom_lay.addWidget(self._generate_btn)
        
        main_lay.addLayout(bottom_lay)
        
        self._output_dir = ""
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with spec days list and text editor."""
        panel = QWidget()
        lay = QVBoxLayout(panel)
        
        # Spec days list
        list_group = QGroupBox("Список спец дней")
        list_lay = QVBoxLayout(list_group)
        
        self._spec_days_list = QPlainTextEdit()
        self._spec_days_list.setPlaceholderText("Загрузите данные из JSON или введите вручную...")
        self._spec_days_list.setMaximumHeight(200)
        list_lay.addWidget(self._spec_days_list)
        
        load_btn_lay = QHBoxLayout()
        self._load_json_btn = QPushButton("Загрузить JSON")
        self._load_json_btn.clicked.connect(self._load_json)
        load_btn_lay.addWidget(self._load_json_btn)
        
        self._parse_text_btn = QPushButton("Парсить текст")
        self._parse_text_btn.clicked.connect(self._parse_text)
        load_btn_lay.addWidget(self._parse_text_btn)
        
        list_lay.addLayout(load_btn_lay)
        lay.addWidget(list_group)
        
        # Navigation
        nav_group = QGroupBox("Навигация")
        nav_lay = QHBoxLayout(nav_group)
        
        self._prev_btn = QPushButton("← Пред.")
        self._prev_btn.clicked.connect(self._prev_item)
        nav_lay.addWidget(self._prev_btn)
        
        self._item_label = QLabel("0 / 0")
        self._item_label.setAlignment(Qt.AlignCenter)
        nav_lay.addWidget(self._item_label, 1)
        
        self._next_btn = QPushButton("След. →")
        self._next_btn.clicked.connect(self._next_item)
        nav_lay.addWidget(self._next_btn)
        
        lay.addWidget(nav_group)
        
        # Description editor
        desc_group = QGroupBox("Редактирование текста desc")
        desc_lay = QVBoxLayout(desc_group)
        
        self._desc_edit = QPlainTextEdit()
        self._desc_edit.setPlaceholderText("Текст описания (имена)...")
        self._desc_edit.textChanged.connect(self._on_desc_changed)
        desc_lay.addWidget(self._desc_edit)
        
        lay.addWidget(desc_group)
        
        lay.addStretch()
        
        return panel
    
    def _create_center_panel(self) -> QWidget:
        """Create center panel with settings."""
        panel = QWidget()
        lay = QVBoxLayout(panel)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        settings_widget = QWidget()
        settings_lay = QVBoxLayout(settings_widget)
        
        # Date text settings
        self._date_settings = TextSettingsWidget("Текст числа дня")
        self._date_settings.changed.connect(self._on_settings_changed)
        settings_lay.addWidget(self._date_settings)
        
        # Description text settings
        self._desc_settings = TextSettingsWidget("Текст desc")
        self._desc_settings.changed.connect(self._on_settings_changed)
        settings_lay.addWidget(self._desc_settings)
        
        # Canvas settings
        self._canvas_settings = CanvasSettingsWidget()
        self._canvas_settings.changed.connect(self._on_settings_changed)
        settings_lay.addWidget(self._canvas_settings)
        
        settings_lay.addStretch()
        scroll.setWidget(settings_widget)
        
        lay.addWidget(scroll)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with preview."""
        panel = QWidget()
        lay = QVBoxLayout(panel)
        
        preview_group = QGroupBox("Превью")
        preview_lay = QVBoxLayout(preview_group)
        
        self._preview_label = QLabel()
        self._preview_label.setMinimumSize(400, 300)
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        preview_lay.addWidget(self._preview_label)
        
        refresh_btn_lay = QHBoxLayout()
        self._refresh_preview_btn = QPushButton("Обновить превью")
        self._refresh_preview_btn.clicked.connect(self._update_preview)
        refresh_btn_lay.addWidget(self._refresh_preview_btn)
        refresh_btn_lay.addStretch()
        preview_lay.addLayout(refresh_btn_lay)
        
        lay.addWidget(preview_group)
        
        return panel
    
    def _load_spec_days_list(self):
        """Load spec days data into the list widget."""
        self._spec_days_list.setPlainText(json.dumps(self._spec_days, indent=2, ensure_ascii=False))
        self._update_item_count()
        self._current_index = 0
        self._update_current_item()
    
    def _load_json(self):
        """Load spec days from JSON file."""
        path, _ = QFDialog.getOpenFileName(
            self, "Загрузить JSON", "", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    self._spec_days = json.load(f)
                self._load_spec_days_list()
                self._update_preview()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить JSON: {e}")
    
    def _parse_text(self):
        """Parse text from the text widget."""
        try:
            from ...utils.text_parser import parse_spec_days_text
            text = self._spec_days_list.toPlainText()
            self._spec_days = parse_spec_days_text(text)
            self._spec_days_list.setPlainText(json.dumps(self._spec_days, indent=2, ensure_ascii=False))
            self._update_item_count()
            self._current_index = 0
            self._update_current_item()
            self._update_preview()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось парсить текст: {e}")
    
    def _update_item_count(self):
        """Update the item count label."""
        total = len(self._spec_days)
        self._item_label.setText(f"{min(self._current_index + 1, max(1, total))} / {total}")
    
    def _prev_item(self):
        """Go to previous item."""
        if self._current_index > 0:
            self._current_index -= 1
            self._update_current_item()
            self._update_preview()
    
    def _next_item(self):
        """Go to next item."""
        if self._current_index < len(self._spec_days) - 1:
            self._current_index += 1
            self._update_current_item()
            self._update_preview()
    
    def _update_current_item(self):
        """Update the current item display."""
        self._update_item_count()
        
        if self._spec_days and 0 <= self._current_index < len(self._spec_days):
            item = self._spec_days[self._current_index]
            desc = item.get("desc", "")
            self._desc_edit.setPlainText(desc)
    
    def _on_desc_changed(self):
        """Handle description text change."""
        if self._spec_days and 0 <= self._current_index < len(self._spec_days):
            self._spec_days[self._current_index]["desc"] = self._desc_edit.toPlainText()
            self._update_preview()
    
    def _on_settings_changed(self):
        """Handle settings change."""
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview image."""
        if not self._spec_days or self._current_index >= len(self._spec_days):
            self._preview_label.setText("Нет данных для превью")
            self._preview_label.setPixmap(QPixmap())
            return
        
        item = self._spec_days[self._current_index]
        date_text = item.get("date", "")
        desc_text = item.get("desc", "")
        
        date_settings = self._date_settings.get_settings()
        desc_settings = self._desc_settings.get_settings()
        canvas_settings = self._canvas_settings.get_settings()
        
        try:
            image = generate_spec_day_image(
                date_text,
                desc_text,
                date_settings,
                desc_settings,
                canvas_settings
            )
            
            # Convert BGR to RGB for Qt
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image_rgb.shape
            
            # Scale image to fit preview area
            preview_size = self._preview_label.size()
            scale_x = preview_size.width() / width
            scale_y = preview_size.height() / height
            scale = min(scale_x, scale_y, 1.0)
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_resized = cv2.resize(image_rgb, (new_width, new_height))
            
            # Convert to QImage
            bytes_per_line = 3 * new_width
            qimage = QImage(image_resized.data, new_width, new_height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            self._preview_label.setPixmap(pixmap)
            self._preview_label.setText("")
        except Exception as e:
            self._preview_label.setText(f"Ошибка превью: {e}")
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        dir_path = QFDialog.getExistingDirectory(
            self, "Выбрать папку для вывода", ""
        )
        if dir_path:
            self._output_dir = dir_path
            self._output_dir_label.setText(f"Выходная папка: {dir_path}")
    
    def _generate_all(self):
        """Generate all spec days images."""
        if not self._output_dir:
            QMessageBox.warning(self, "Предупреждение", "Выберите папку для вывода!")
            return
        
        if not self._spec_days:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для генерации!")
            return
        
        date_settings = self._date_settings.get_settings()
        desc_settings = self._desc_settings.get_settings()
        canvas_settings = self._canvas_settings.get_settings()
        
        try:
            from .generator import generate_all_spec_days
            paths = generate_all_spec_days(
                self._spec_days,
                date_settings,
                desc_settings,
                canvas_settings,
                self._output_dir
            )
            
            QMessageBox.information(
                self,
                "Готово",
                f"Сгенерировано {len(paths)} изображений!\n\n"
                f"Папка: {self._output_dir}"
            )
            
            self.generationComplete.emit(paths)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации: {e}")
    
    def set_spec_days(self, spec_days: list):
        """Set spec days data from outside."""
        self._spec_days = spec_days
        self._load_spec_days_list()
        self._update_preview()
