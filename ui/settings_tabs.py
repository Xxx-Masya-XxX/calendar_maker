from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QFontComboBox, QLineEdit, QSpinBox, QComboBox, QLabel,
    QPushButton, QColorDialog, QGridLayout, QCheckBox,
    QFileDialog, QScrollArea, QListWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor
import os


class GeneralSettingsTab(QWidget):
    """General settings tab."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Calendar info group
        info_group = QGroupBox("Calendar Info / Информация о календаре")
        info_layout = QFormLayout()

        self.name_edit = QLineEdit("My Calendar 2026")
        self.name_edit.setPlaceholderText("Calendar name")
        info_layout.addRow("Name:", self.name_edit)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(2026)
        info_layout.addRow("Year:", self.year_spin)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Single Page (1 лист)", "single_page")
        self.type_combo.addItem("Multi Page (Многостраничный)", "multi_page")
        self.type_combo.addItem("Multi Page with Notes (С полями)", "multi_page_notes")
        info_layout.addRow("Type:", self.type_combo)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Render buttons
        render_group = QGroupBox("Render / Рендер")
        render_layout = QVBoxLayout()

        self.render_btn = QPushButton("Render Calendar / Рендерить календарь")
        self.render_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        render_layout.addWidget(self.render_btn)

        self.preview_btn = QPushButton("Generate Preview / Предпросмотр")
        self.preview_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        render_layout.addWidget(self.preview_btn)

        render_group.setLayout(render_layout)
        layout.addWidget(render_group)

        layout.addStretch()
        self.setLayout(layout)

    def reset(self):
        self.name_edit.setText("My Calendar 2026")
        self.year_spin.setValue(2026)
        self.type_combo.setCurrentIndex(0)


class LayoutSettingsTab(QWidget):
    """Layout settings tab."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()

        # Canvas settings
        canvas_group = QGroupBox("Canvas / Холст")
        canvas_layout = QFormLayout()

        self.canvas_width_spin = QSpinBox()
        self.canvas_width_spin.setRange(100, 10000)
        self.canvas_width_spin.setValue(2480)
        self.canvas_width_spin.setSuffix(" px")
        canvas_layout.addRow("Width:", self.canvas_width_spin)

        self.canvas_height_spin = QSpinBox()
        self.canvas_height_spin.setRange(100, 10000)
        self.canvas_height_spin.setValue(3508)
        self.canvas_height_spin.setSuffix(" px")
        canvas_layout.addRow("Height:", self.canvas_height_spin)

        self.canvas_dpi_spin = QSpinBox()
        self.canvas_dpi_spin.setRange(72, 600)
        self.canvas_dpi_spin.setValue(300)
        self.canvas_dpi_spin.setSuffix(" DPI")
        canvas_layout.addRow("DPI:", self.canvas_dpi_spin)

        canvas_group.setLayout(canvas_layout)
        container_layout.addWidget(canvas_group)

        # Single page layout
        single_page_group = QGroupBox("Single Page Layout / Одностраничный макет")
        single_page_layout = QGridLayout()

        self.single_cols_spin = QSpinBox()
        self.single_cols_spin.setRange(1, 6)
        self.single_cols_spin.setValue(3)
        single_page_layout.addWidget(QLabel("Columns:"), 0, 0)
        single_page_layout.addWidget(self.single_cols_spin, 0, 1)

        self.single_rows_spin = QSpinBox()
        self.single_rows_spin.setRange(1, 12)
        self.single_rows_spin.setValue(4)
        single_page_layout.addWidget(QLabel("Rows:"), 1, 0)
        single_page_layout.addWidget(self.single_rows_spin, 1, 1)

        self.single_margin_x_spin = QSpinBox()
        self.single_margin_x_spin.setRange(0, 500)
        self.single_margin_x_spin.setValue(40)
        single_page_layout.addWidget(QLabel("Margin X:"), 2, 0)
        single_page_layout.addWidget(self.single_margin_x_spin, 2, 1)

        self.single_margin_y_spin = QSpinBox()
        self.single_margin_y_spin.setRange(0, 500)
        self.single_margin_y_spin.setValue(40)
        single_page_layout.addWidget(QLabel("Margin Y:"), 3, 0)
        single_page_layout.addWidget(self.single_margin_y_spin, 3, 1)

        self.single_spacing_x_spin = QSpinBox()
        self.single_spacing_x_spin.setRange(0, 200)
        self.single_spacing_x_spin.setValue(20)
        single_page_layout.addWidget(QLabel("Spacing X:"), 4, 0)
        single_page_layout.addWidget(self.single_spacing_x_spin, 4, 1)

        self.single_spacing_y_spin = QSpinBox()
        self.single_spacing_y_spin.setRange(0, 200)
        self.single_spacing_y_spin.setValue(20)
        single_page_layout.addWidget(QLabel("Spacing Y:"), 5, 0)
        single_page_layout.addWidget(self.single_spacing_y_spin, 5, 1)

        single_page_group.setLayout(single_page_layout)
        container_layout.addWidget(single_page_group)

        # Multi page layout
        multi_page_group = QGroupBox("Multi Page Layout / Многостраничный макет")
        multi_page_layout = QFormLayout()

        self.multi_margin_x_spin = QSpinBox()
        self.multi_margin_x_spin.setRange(0, 500)
        self.multi_margin_x_spin.setValue(100)
        multi_page_layout.addRow("Margin X:", self.multi_margin_x_spin)

        self.multi_margin_y_spin = QSpinBox()
        self.multi_margin_y_spin.setRange(0, 500)
        self.multi_margin_y_spin.setValue(100)
        multi_page_layout.addRow("Margin Y:", self.multi_margin_y_spin)

        self.multi_header_height_spin = QSpinBox()
        self.multi_header_height_spin.setRange(50, 500)
        self.multi_header_height_spin.setValue(200)
        multi_page_layout.addRow("Header Height:", self.multi_header_height_spin)

        multi_page_group.setLayout(multi_page_layout)
        container_layout.addWidget(multi_page_group)

        # Notes settings
        notes_group = QGroupBox("Notes Section / Секция заметок")
        notes_layout = QFormLayout()

        self.notes_ratio_spin = QSpinBox()
        self.notes_ratio_spin.setRange(10, 80)
        self.notes_ratio_spin.setValue(35)
        self.notes_ratio_spin.setSuffix(" %")
        notes_layout.addRow("Area Ratio:", self.notes_ratio_spin)

        self.notes_line_spacing_spin = QSpinBox()
        self.notes_line_spacing_spin.setRange(20, 200)
        self.notes_line_spacing_spin.setValue(60)
        self.notes_line_spacing_spin.setSuffix(" px")
        notes_layout.addRow("Line Spacing:", self.notes_line_spacing_spin)

        notes_group.setLayout(notes_layout)
        container_layout.addWidget(notes_group)

        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll.setWidget(container)

        layout.addWidget(scroll)
        self.setLayout(layout)

    def reset(self):
        self.canvas_width_spin.setValue(2480)
        self.canvas_height_spin.setValue(3508)
        self.canvas_dpi_spin.setValue(300)
        self.single_cols_spin.setValue(3)
        self.single_rows_spin.setValue(4)
        self.single_margin_x_spin.setValue(40)
        self.single_margin_y_spin.setValue(40)
        self.single_spacing_x_spin.setValue(20)
        self.single_spacing_y_spin.setValue(20)
        self.multi_margin_x_spin.setValue(100)
        self.multi_margin_y_spin.setValue(100)
        self.multi_header_height_spin.setValue(200)
        self.notes_ratio_spin.setValue(35)
        self.notes_line_spacing_spin.setValue(60)


class StyleSettingsTab(QWidget):
    """Style settings tab with preview panels."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)

        # Left side - settings with scroll
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(10)

        # Font settings
        font_group = self._create_font_group()
        container_layout.addWidget(font_group)

        # Day settings
        day_group = self._create_day_group()
        container_layout.addWidget(day_group)

        # Month title positioning
        title_pos_group = self._create_title_pos_group()
        container_layout.addWidget(title_pos_group)

        # Background images
        bg_group = self._create_bg_group()
        container_layout.addWidget(bg_group)

        # Color settings
        color_group = self._create_color_group()
        container_layout.addWidget(color_group)

        # Weekday settings
        weekday_group = self._create_weekday_group()
        container_layout.addWidget(weekday_group)

        # Weekend settings
        weekend_group = self._create_weekend_group()
        container_layout.addWidget(weekend_group)

        # Notes settings
        notes_style_group = self._create_notes_style_group()
        container_layout.addWidget(notes_style_group)

        # Weekday names
        weekday_names_group = self._create_weekday_names_group()
        container_layout.addWidget(weekday_names_group)

        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll.setWidget(container)
        left_layout.addWidget(scroll)
        left_widget.setLayout(left_layout)

        # Right side - previews (fixed width)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Day preview
        day_preview_group = self._create_day_preview_group()
        right_layout.addWidget(day_preview_group)

        # Month preview
        month_preview_group = self._create_month_preview_group()
        right_layout.addWidget(month_preview_group)

        right_layout.addStretch()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(250)

        # Add both sides to main layout
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 0)

        self.setLayout(main_layout)

    def _create_font_group(self):
        """Create font settings group."""
        group = QGroupBox("Font / Шрифт")
        layout = QFormLayout()

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial", 12))
        layout.addRow("Font Family:", self.font_combo)

        self.month_font_size_spin = QSpinBox()
        self.month_font_size_spin.setRange(8, 72)
        self.month_font_size_spin.setValue(14)
        layout.addRow("Month Font Size:", self.month_font_size_spin)

        self.title_font_size_spin = QSpinBox()
        self.title_font_size_spin.setRange(24, 120)
        self.title_font_size_spin.setValue(48)
        layout.addRow("Title Font Size:", self.title_font_size_spin)

        group.setLayout(layout)
        return group

    def _create_day_group(self):
        """Create day settings group."""
        group = QGroupBox("Day Settings / Настройки дня")
        layout = QFormLayout()

        self.day_width_spin = QSpinBox()
        self.day_width_spin.setRange(50, 1000)
        self.day_width_spin.setValue(300)
        layout.addRow("Day Width:", self.day_width_spin)

        self.day_height_spin = QSpinBox()
        self.day_height_spin.setRange(50, 1000)
        self.day_height_spin.setValue(400)
        layout.addRow("Day Height:", self.day_height_spin)

        self.day_font_size_spin = QSpinBox()
        self.day_font_size_spin.setRange(8, 48)
        self.day_font_size_spin.setValue(14)
        layout.addRow("Day Font Size:", self.day_font_size_spin)

        self.day_border_width_spin = QSpinBox()
        self.day_border_width_spin.setRange(0, 10)
        self.day_border_width_spin.setValue(1)
        layout.addRow("Border Width:", self.day_border_width_spin)

        self.day_border_style_combo = QComboBox()
        self.day_border_style_combo.addItems(["Solid", "Dashed", "Dotted"])
        layout.addRow("Border Style:", self.day_border_style_combo)

        # Day number positioning
        self.day_num_pos_x_spin = QSpinBox()
        self.day_num_pos_x_spin.setRange(0, 500)
        self.day_num_pos_x_spin.setValue(10)
        layout.addRow("Number Pos X:", self.day_num_pos_x_spin)

        self.day_num_pos_y_spin = QSpinBox()
        self.day_num_pos_y_spin.setRange(0, 500)
        self.day_num_pos_y_spin.setValue(10)
        layout.addRow("Number Pos Y:", self.day_num_pos_y_spin)

        # Holiday text positioning
        self.holiday_pos_x_spin = QSpinBox()
        self.holiday_pos_x_spin.setRange(0, 500)
        self.holiday_pos_x_spin.setValue(10)
        layout.addRow("Holiday Pos X:", self.holiday_pos_x_spin)

        self.holiday_pos_y_spin = QSpinBox()
        self.holiday_pos_y_spin.setRange(0, 500)
        self.holiday_pos_y_spin.setValue(40)
        layout.addRow("Holiday Pos Y:", self.holiday_pos_y_spin)

        group.setLayout(layout)
        return group

    def _create_title_pos_group(self):
        """Create month title positioning group."""
        group = QGroupBox("Month Title Position / Позиция заголовка")
        layout = QFormLayout()

        self.title_pos_x_spin = QSpinBox()
        self.title_pos_x_spin.setRange(-1000, 5000)
        self.title_pos_x_spin.setValue(0)
        layout.addRow("Title Pos X:", self.title_pos_x_spin)

        self.title_pos_y_spin = QSpinBox()
        self.title_pos_y_spin.setRange(-1000, 5000)
        self.title_pos_y_spin.setValue(20)
        layout.addRow("Title Pos Y:", self.title_pos_y_spin)

        self.title_align_combo = QComboBox()
        self.title_align_combo.addItems(["left", "center", "right"])
        self.title_align_combo.setCurrentText("center")
        layout.addRow("Title Align:", self.title_align_combo)

        group.setLayout(layout)
        return group

    def _create_bg_group(self):
        """Create background images group."""
        group = QGroupBox("Background Images / Фоновые изображения")
        layout = QFormLayout()

        self.month_bg_image_edit = QLineEdit()
        self.month_bg_image_btn = QPushButton("Browse...")
        self.month_bg_image_btn.clicked.connect(lambda: self._browse_image(self.month_bg_image_edit))
        month_bg_layout = QHBoxLayout()
        month_bg_layout.addWidget(self.month_bg_image_edit)
        month_bg_layout.addWidget(self.month_bg_image_btn)
        layout.addRow("Month BG:", month_bg_layout)

        self.day_bg_image_edit = QLineEdit()
        self.day_bg_image_btn = QPushButton("Browse...")
        self.day_bg_image_btn.clicked.connect(lambda: self._browse_image(self.day_bg_image_edit))
        day_bg_layout = QHBoxLayout()
        day_bg_layout.addWidget(self.day_bg_image_edit)
        day_bg_layout.addWidget(self.day_bg_image_btn)
        layout.addRow("Day BG:", day_bg_layout)

        group.setLayout(layout)
        return group

    def _create_color_group(self):
        """Create color settings group."""
        group = QGroupBox("Colors / Цвета")
        layout = QGridLayout()

        # Month colors
        layout.addWidget(QLabel("Month:"), 0, 0)
        self.month_font_color_btn = self._create_color_btn("#000000")
        layout.addWidget(self.month_font_color_btn, 0, 1)
        self.month_bg_color_btn = self._create_color_btn("#FFFFFF")
        layout.addWidget(self.month_bg_color_btn, 0, 2)

        # Title colors
        layout.addWidget(QLabel("Title:"), 1, 0)
        self.title_font_color_btn = self._create_color_btn("#000000")
        layout.addWidget(self.title_font_color_btn, 1, 1)

        # Day colors
        layout.addWidget(QLabel("Day:"), 2, 0)
        self.day_font_color_btn = self._create_color_btn("#000000")
        layout.addWidget(self.day_font_color_btn, 2, 1)
        self.day_bg_color_btn = self._create_color_btn("#FFFFFF")
        layout.addWidget(self.day_bg_color_btn, 2, 2)

        # Day border
        layout.addWidget(QLabel("Day Border:"), 3, 0)
        self.day_border_color_btn = self._create_color_btn("#CCCCCC")
        layout.addWidget(self.day_border_color_btn, 3, 1)

        # Weekday colors
        layout.addWidget(QLabel("Weekday:"), 4, 0)
        self.weekday_bg_color_btn = self._create_color_btn("#F0F0F0")
        layout.addWidget(self.weekday_bg_color_btn, 4, 1)

        # Weekend colors
        layout.addWidget(QLabel("Weekend:"), 5, 0)
        self.weekend_bg_color_btn = self._create_color_btn("#FFF5F5")
        layout.addWidget(self.weekend_bg_color_btn, 5, 1)
        self.weekend_font_color_btn = self._create_color_btn("#FF0000")
        layout.addWidget(self.weekend_font_color_btn, 5, 2)

        # Notes colors
        layout.addWidget(QLabel("Notes:"), 6, 0)
        self.notes_bg_color_btn = self._create_color_btn("#F8F8F8")
        layout.addWidget(self.notes_bg_color_btn, 6, 1)

        group.setLayout(layout)
        return group

    def _create_weekday_group(self):
        """Create weekday header group."""
        group = QGroupBox("Weekday Header / Заголовок дня недели")
        layout = QFormLayout()

        self.weekday_height_spin = QSpinBox()
        self.weekday_height_spin.setRange(20, 100)
        self.weekday_height_spin.setValue(40)
        layout.addRow("Header Height:", self.weekday_height_spin)

        self.weekday_font_size_spin = QSpinBox()
        self.weekday_font_size_spin.setRange(8, 36)
        self.weekday_font_size_spin.setValue(14)
        layout.addRow("Font Size:", self.weekday_font_size_spin)

        group.setLayout(layout)
        return group

    def _create_weekend_group(self):
        """Create weekend settings group."""
        group = QGroupBox("Weekend / Выходные")
        layout = QVBoxLayout()

        self.highlight_weekends_check = QCheckBox("Highlight Weekends")
        self.highlight_weekends_check.setChecked(True)
        layout.addWidget(self.highlight_weekends_check)

        group.setLayout(layout)
        return group

    def _create_notes_style_group(self):
        """Create notes style group."""
        group = QGroupBox("Notes Style / Стиль заметок")
        layout = QFormLayout()

        self.notes_font_size_spin = QSpinBox()
        self.notes_font_size_spin.setRange(12, 72)
        self.notes_font_size_spin.setValue(32)
        layout.addRow("Title Font Size:", self.notes_font_size_spin)

        group.setLayout(layout)
        return group

    def _create_weekday_names_group(self):
        """Create weekday names group."""
        group = QGroupBox("Weekday Names / Названия дней недели")
        layout = QGridLayout()

        self.weekday_edits = []
        weekday_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, name in enumerate(weekday_short):
            edit = QLineEdit(name)
            self.weekday_edits.append(edit)
            layout.addWidget(QLabel(f"Day {i+1}:"), i // 3, (i % 3) * 2)
            layout.addWidget(edit, i // 3, (i % 3) * 2 + 1)

        group.setLayout(layout)
        return group

    def _create_day_preview_group(self):
        """Create day preview group."""
        group = QGroupBox("Day Preview / Предпросмотр дня")
        layout = QVBoxLayout()
        
        self.day_preview_label = QLabel()
        self.day_preview_label.setMinimumSize(200, 250)
        self.day_preview_label.setMaximumSize(200, 250)
        self.day_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.day_preview_label.setStyleSheet("QLabel { background-color: #F5F5F5; border: 1px solid #CCC; }")
        self.day_preview_label.setText("Day Preview")
        layout.addWidget(self.day_preview_label)
        
        self.update_day_preview_btn = QPushButton("Update Preview")
        self.update_day_preview_btn.clicked.connect(self.update_day_preview)
        layout.addWidget(self.update_day_preview_btn)

        group.setLayout(layout)
        return group

    def _create_month_preview_group(self):
        """Create month preview group."""
        group = QGroupBox("Month Preview / Предпросмотр месяца")
        layout = QVBoxLayout()
        
        self.month_preview_label = QLabel()
        self.month_preview_label.setMinimumSize(280, 150)
        self.month_preview_label.setMaximumSize(280, 150)
        self.month_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_preview_label.setStyleSheet("QLabel { background-color: #F5F5F5; border: 1px solid #CCC; }")
        self.month_preview_label.setText("Month Preview")
        layout.addWidget(self.month_preview_label)
        
        self.update_month_preview_btn = QPushButton("Update Preview")
        self.update_month_preview_btn.clicked.connect(self.update_month_preview)
        layout.addWidget(self.update_month_preview_btn)

        group.setLayout(layout)
        return group

    def _browse_image(self, line_edit: QLineEdit):
        """Open file dialog to select image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image / Выбрать изображение",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            assets_path = os.path.join(os.getcwd(), "assets")
            if file_path.startswith(assets_path):
                relative_path = os.path.relpath(file_path, assets_path)
            else:
                relative_path = file_path
            line_edit.setText(relative_path)

    def update_day_preview(self):
        """Update day preview."""
        from PIL import Image, ImageDraw, ImageFont
        import tempfile

        width = self.day_width_spin.value()
        height = self.day_height_spin.value()

        scale = min(180 / width, 230 / height)
        preview_width = int(width * scale)
        preview_height = int(height * scale)

        img = Image.new("RGB", (preview_width, preview_height), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, preview_width-1, preview_height-1], outline="#CCCCCC", width=1)

        font_size = max(8, int(self.day_font_size_spin.value() * scale))
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        draw.text((5, 5), "15", fill="#000000", font=font)
        draw.text((5, 25), "Holiday", fill="#FF0000", font=font)

        temp_path = os.path.join(tempfile.gettempdir(), "day_preview.png")
        img.save(temp_path)
        pixmap = QPixmap(temp_path)
        self.day_preview_label.setPixmap(pixmap)
        self.day_preview_label.setText("")

    def update_month_preview(self):
        """Update month preview."""
        from PIL import Image, ImageDraw, ImageFont
        import tempfile

        preview_width = 280
        preview_height = 130

        img = Image.new("RGB", (preview_width, preview_height), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        font_size = max(12, self.title_font_size_spin.value() // 3)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        align = self.title_align_combo.currentText()
        if align == "center":
            x = preview_width // 2
        elif align == "right":
            x = preview_width - 10
        else:
            x = 10

        draw.text((x, 10), "January 2026", fill="#000000", font=font)

        temp_path = os.path.join(tempfile.gettempdir(), "month_preview.png")
        img.save(temp_path)
        pixmap = QPixmap(temp_path)
        self.month_preview_label.setPixmap(pixmap)
        self.month_preview_label.setText("")

    def _create_color_btn(self, color: str) -> QPushButton:
        """Create a color picker button."""
        btn = QPushButton()
        btn.setFixedSize(60, 30)
        btn.setStyleSheet(f"background-color: {color}; border: 1px solid #999;")
        btn.clicked.connect(lambda checked, b=btn: self._choose_color(b))
        return btn

    def _choose_color(self, btn: QPushButton):
        """Open color dialog and update button color."""
        current_color = btn.styleSheet().split("#")[1].split(";")[0]
        color = QColorDialog.getColor(QColor(current_color))
        if color.isValid():
            hex_color = color.name()
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #999;")

    def get_weekday_names(self) -> list:
        """Get weekday names from edits."""
        return [edit.text() for edit in self.weekday_edits]

    def apply_config(self, config):
        """Apply configuration to this tab."""
        self.font_combo.setCurrentFont(QFont(config.month_font_type))
        self.month_font_size_spin.setValue(config.month_font_size)
        self.title_font_size_spin.setValue(config.month_title_font_size)
        self.day_width_spin.setValue(config.day_width)
        self.day_height_spin.setValue(config.day_height)
        self.day_font_size_spin.setValue(config.day_font_size)
        self.day_border_width_spin.setValue(config.day_border_width)
        self.day_border_style_combo.setCurrentText(config.day_border_style.capitalize())
        self.weekday_height_spin.setValue(config.weekday_header_height)
        self.weekday_font_size_spin.setValue(config.weekday_font_size)
        self.highlight_weekends_check.setChecked(config.highlight_weekends)
        self.notes_font_size_spin.setValue(config.notes_font_size)
        self.day_num_pos_x_spin.setValue(config.day_number_position_x)
        self.day_num_pos_y_spin.setValue(config.day_number_position_y)
        self.holiday_pos_x_spin.setValue(config.holiday_text_position_x)
        self.holiday_pos_y_spin.setValue(config.holiday_text_position_y)
        self.title_pos_x_spin.setValue(config.month_title_position_x)
        self.title_pos_y_spin.setValue(config.month_title_position_y)
        self.title_align_combo.setCurrentText(config.month_title_align)
        self.month_bg_image_edit.setText(config.month_background_image)
        self.day_bg_image_edit.setText(config.day_background_image)

        self._set_btn_color(self.month_font_color_btn, config.month_font_color)
        self._set_btn_color(self.month_bg_color_btn, config.month_background_color)
        self._set_btn_color(self.title_font_color_btn, config.month_title_font_color)
        self._set_btn_color(self.day_font_color_btn, config.day_font_color)
        self._set_btn_color(self.day_bg_color_btn, config.day_background_color)
        self._set_btn_color(self.day_border_color_btn, config.day_border_color)
        self._set_btn_color(self.weekday_bg_color_btn, config.weekday_background_color)
        self._set_btn_color(self.weekend_bg_color_btn, config.weekend_background_color)
        self._set_btn_color(self.weekend_font_color_btn, config.weekend_font_color)
        self._set_btn_color(self.notes_bg_color_btn, config.notes_background_color)

    def _set_btn_color(self, btn: QPushButton, color: str):
        """Set button color."""
        btn.setStyleSheet(f"background-color: {color}; border: 1px solid #999;")

    def reset(self):
        """Reset to defaults."""
        self.font_combo.setCurrentFont(QFont("Arial", 12))
        self.month_font_size_spin.setValue(14)
        self.title_font_size_spin.setValue(48)
        self.day_width_spin.setValue(300)
        self.day_height_spin.setValue(400)
        self.day_font_size_spin.setValue(14)
        self.day_border_width_spin.setValue(1)
        self.day_border_style_combo.setCurrentIndex(0)
        self.day_num_pos_x_spin.setValue(10)
        self.day_num_pos_y_spin.setValue(10)
        self.holiday_pos_x_spin.setValue(10)
        self.holiday_pos_y_spin.setValue(40)
        self.title_pos_x_spin.setValue(0)
        self.title_pos_y_spin.setValue(20)
        self.title_align_combo.setCurrentText("center")
        self.month_bg_image_edit.setText("")
        self.day_bg_image_edit.setText("")

        self._set_btn_color(self.month_font_color_btn, "#000000")
        self._set_btn_color(self.month_bg_color_btn, "#FFFFFF")
        self._set_btn_color(self.title_font_color_btn, "#000000")
        self._set_btn_color(self.day_font_color_btn, "#000000")
        self._set_btn_color(self.day_bg_color_btn, "#FFFFFF")
        self._set_btn_color(self.day_border_color_btn, "#CCCCCC")
        self._set_btn_color(self.weekday_bg_color_btn, "#F0F0F0")
        self._set_btn_color(self.weekend_bg_color_btn, "#FFF5F5")
        self._set_btn_color(self.weekend_font_color_btn, "#FF0000")
        self._set_btn_color(self.notes_bg_color_btn, "#F8F8F8")

        weekday_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, name in enumerate(weekday_short):
            self.weekday_edits[i].setText(name)


class HolidaysSettingsTab(QWidget):
    """Holidays and special days settings tab."""

    def __init__(self):
        super().__init__()
        self.holidays = []
        self.special_days = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Default holidays
        self.add_default_holidays_check = QCheckBox("Add Default Russian Holidays")
        self.add_default_holidays_check.setChecked(True)
        layout.addWidget(self.add_default_holidays_check)

        # Holidays list
        holidays_group = QGroupBox("Holidays / Праздники")
        holidays_layout = QVBoxLayout()

        self.holidays_list = QListWidget()
        self.holidays_list.setMaximumHeight(200)

        holidays_btn_layout = QHBoxLayout()
        self.add_holiday_btn = QPushButton("Add Holiday")
        self.remove_holiday_btn = QPushButton("Remove")
        self.add_holiday_btn.clicked.connect(self.on_add_holiday)
        self.remove_holiday_btn.clicked.connect(self.on_remove_holiday)

        holidays_btn_layout.addWidget(self.add_holiday_btn)
        holidays_btn_layout.addWidget(self.remove_holiday_btn)
        holidays_btn_layout.addStretch()

        holidays_layout.addWidget(self.holidays_list)
        holidays_layout.addLayout(holidays_btn_layout)
        holidays_group.setLayout(holidays_layout)
        layout.addWidget(holidays_group)

        # Special days list
        special_group = QGroupBox("Special Days / Особые дни")
        special_layout = QVBoxLayout()

        self.special_days_list = QListWidget()
        self.special_days_list.setMaximumHeight(200)

        special_btn_layout = QHBoxLayout()
        self.add_special_btn = QPushButton("Add Special Day")
        self.remove_special_btn = QPushButton("Remove")
        self.add_special_btn.clicked.connect(self.on_add_special_day)
        self.remove_special_btn.clicked.connect(self.on_remove_special_day)

        special_btn_layout.addWidget(self.add_special_btn)
        special_btn_layout.addWidget(self.remove_special_btn)
        special_btn_layout.addStretch()

        special_layout.addWidget(self.special_days_list)
        special_layout.addLayout(special_btn_layout)
        special_group.setLayout(special_layout)
        layout.addWidget(special_group)

        layout.addStretch()
        self.setLayout(layout)

    def on_add_holiday(self):
        from .settings_dialog import AddHolidayDialog
        dialog = AddHolidayDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.holidays.append(data)
            self.holidays_list.addItem(f"{data['name']} - {data['month']}/{data['day']}")

    def on_remove_holiday(self):
        row = self.holidays_list.currentRow()
        if row >= 0:
            self.holidays.pop(row)
            self.holidays_list.takeItem(row)

    def on_add_special_day(self):
        from .settings_dialog import AddSpecialDayDialog
        dialog = AddSpecialDayDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.special_days.append(data)
            self.special_days_list.addItem(f"{data['name']} - {data['month']}/{data['day']}")

    def on_remove_special_day(self):
        row = self.special_days_list.currentRow()
        if row >= 0:
            self.special_days.pop(row)
            self.special_days_list.takeItem(row)

    def get_holidays_data(self) -> list:
        return self.holidays

    def get_special_days_data(self) -> list:
        return self.special_days

    def set_holidays_data(self, data: list):
        self.holidays = data.copy() if data else []
        self.holidays_list.clear()
        for h in self.holidays:
            self.holidays_list.addItem(f"{h.get('name', 'Holiday')} - {h.get('month', 1)}/{h.get('day', 1)}")

    def set_special_days_data(self, data: list):
        self.special_days = data.copy() if data else []
        self.special_days_list.clear()
        for s in self.special_days:
            self.special_days_list.addItem(f"{s.get('name', 'Special')} - {s.get('month', 1)}/{s.get('day', 1)}")

    def reset(self):
        self.holidays = []
        self.special_days = []
        self.holidays_list.clear()
        self.special_days_list.clear()
        self.add_default_holidays_check.setChecked(True)
