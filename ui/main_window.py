from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QStatusBar, QTabWidget,
    QMessageBox, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from .calendar_widget import CalendarWidget
from .settings_tabs import GeneralSettingsTab, LayoutSettingsTab, StyleSettingsTab, HolidaysSettingsTab


class MainWindow(QMainWindow):
    """Main window of the Calendar Maker application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar Maker / Создатель календарей")
        self.setMinimumSize(1200, 800)
        self.config_path = None
        self.init_ui()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Settings tabs
        self.general_tab = GeneralSettingsTab()
        self.layout_tab = LayoutSettingsTab()
        self.style_tab = StyleSettingsTab()
        self.holidays_tab = HolidaysSettingsTab()
        
        self.tabs.addTab(self.general_tab, "General / Общие")
        self.tabs.addTab(self.layout_tab, "Layout / Макет")
        self.tabs.addTab(self.style_tab, "Style / Стиль")
        self.tabs.addTab(self.holidays_tab, "Holidays / Праздники")
        
        # Calendar preview widget
        self.calendar_widget = CalendarWidget()

        # Splitter for settings and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.calendar_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready / Готов")

        # Connect render buttons
        self.general_tab.render_btn.clicked.connect(self.on_render)
        self.general_tab.preview_btn.clicked.connect(self.on_preview)
        
        # Connect preview update buttons
        self.style_tab.update_day_preview_btn.clicked.connect(self.style_tab.update_day_preview)
        self.style_tab.update_month_preview_btn.clicked.connect(self.style_tab.update_month_preview)

        # Menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File / Файл")
        
        new_action = QAction("New / Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Config / Открыть конфиг", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Config / Сохранить конфиг", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        render_action = QAction("Render Calendar / Рендерить календарь", self)
        render_action.setShortcut("Ctrl+R")
        render_action.triggered.connect(self.on_render)
        file_menu.addAction(render_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit / Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit / Правка")
        
        reset_action = QAction("Reset Settings / Сброс настроек", self)
        reset_action.setShortcut("Ctrl+Z")
        reset_action.triggered.connect(self.on_reset)
        edit_menu.addAction(reset_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help / Помощь")
        
        about_action = QAction("About / О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def get_config(self):
        """Get current configuration from all tabs."""
        from config import CalendarConfig

        config = CalendarConfig()

        # General settings
        config.name = self.general_tab.name_edit.text()
        config.year = self.general_tab.year_spin.value()
        config.calendar_type = self.general_tab.type_combo.currentData()

        # Canvas settings
        config.canvas.width = self.layout_tab.canvas_width_spin.value()
        config.canvas.height = self.layout_tab.canvas_height_spin.value()
        config.canvas.dpi = self.layout_tab.canvas_dpi_spin.value()

        # Layout settings
        config.layout.single_page_columns = self.layout_tab.single_cols_spin.value()
        config.layout.single_page_rows = self.layout_tab.single_rows_spin.value()
        config.layout.single_page_margin_x = self.layout_tab.single_margin_x_spin.value()
        config.layout.single_page_margin_y = self.layout_tab.single_margin_y_spin.value()
        config.layout.single_page_spacing_x = self.layout_tab.single_spacing_x_spin.value()
        config.layout.single_page_spacing_y = self.layout_tab.single_spacing_y_spin.value()
        config.layout.multi_page_margin_x = self.layout_tab.multi_margin_x_spin.value()
        config.layout.multi_page_margin_y = self.layout_tab.multi_margin_y_spin.value()
        config.layout.multi_page_header_height = self.layout_tab.multi_header_height_spin.value()
        config.layout.notes_area_ratio = self.layout_tab.notes_ratio_spin.value() / 100.0
        config.layout.notes_line_spacing = self.layout_tab.notes_line_spacing_spin.value()

        # Style settings
        config.month_font_type = self.style_tab.font_combo.currentFont().family()
        config.month_font_size = self.style_tab.month_font_size_spin.value()
        config.month_font_color = self._get_btn_color(self.style_tab.month_font_color_btn)
        config.month_title_font_size = self.style_tab.title_font_size_spin.value()
        config.month_title_font_color = self._get_btn_color(self.style_tab.title_font_color_btn)
        config.month_background_color = self._get_btn_color(self.style_tab.month_bg_color_btn)
        config.month_background_image = self.style_tab.month_bg_image_edit.text()
        config.day_width = self.style_tab.day_width_spin.value()
        config.day_height = self.style_tab.day_height_spin.value()
        config.day_font_size = self.style_tab.day_font_size_spin.value()
        config.day_font_color = self._get_btn_color(self.style_tab.day_font_color_btn)
        config.day_background_color = self._get_btn_color(self.style_tab.day_bg_color_btn)
        config.day_background_image = self.style_tab.day_bg_image_edit.text()
        config.day_border_color = self._get_btn_color(self.style_tab.day_border_color_btn)
        config.day_border_width = self.style_tab.day_border_width_spin.value()
        config.day_border_style = self.style_tab.day_border_style_combo.currentText().lower()
        config.weekday_header_height = self.style_tab.weekday_height_spin.value()
        config.weekday_font_size = self.style_tab.weekday_font_size_spin.value()
        config.weekday_background_color = self._get_btn_color(self.style_tab.weekday_bg_color_btn)
        config.highlight_weekends = self.style_tab.highlight_weekends_check.isChecked()
        config.weekend_background_color = self._get_btn_color(self.style_tab.weekend_bg_color_btn)
        config.weekend_font_color = self._get_btn_color(self.style_tab.weekend_font_color_btn)
        config.notes_background_color = self._get_btn_color(self.style_tab.notes_bg_color_btn)
        config.notes_font_size = self.style_tab.notes_font_size_spin.value()
        
        # Positioning
        config.day_number_position_x = self.style_tab.day_num_pos_x_spin.value()
        config.day_number_position_y = self.style_tab.day_num_pos_y_spin.value()
        config.holiday_text_position_x = self.style_tab.holiday_pos_x_spin.value()
        config.holiday_text_position_y = self.style_tab.holiday_pos_y_spin.value()
        config.month_title_position_x = self.style_tab.title_pos_x_spin.value()
        config.month_title_position_y = self.style_tab.title_pos_y_spin.value()
        config.month_title_align = self.style_tab.title_align_combo.currentText()

        # Holidays
        config.add_default_holidays = self.holidays_tab.add_default_holidays_check.isChecked()
        config.holidays = self.holidays_tab.get_holidays_data()
        config.special_days = self.holidays_tab.get_special_days_data()

        # Weekday names
        config.weekday_names = self.style_tab.get_weekday_names()

        return config
    
    def _get_btn_color(self, btn) -> str:
        """Get color from button stylesheet."""
        try:
            return btn.styleSheet().split("#")[1].split(";")[0]
        except:
            return "#000000"
    
    def set_config(self, config):
        """Apply configuration to all tabs."""
        # General settings
        self.general_tab.name_edit.setText(config.name)
        self.general_tab.year_spin.setValue(config.year)
        self.general_tab.type_combo.setCurrentIndex(
            self.general_tab.type_combo.findData(config.calendar_type)
        )
        
        # Canvas settings
        self.layout_tab.canvas_width_spin.setValue(config.canvas.width)
        self.layout_tab.canvas_height_spin.setValue(config.canvas.height)
        self.layout_tab.canvas_dpi_spin.setValue(config.canvas.dpi)
        
        # Layout settings
        self.layout_tab.single_cols_spin.setValue(config.layout.single_page_columns)
        self.layout_tab.single_rows_spin.setValue(config.layout.single_page_rows)
        self.layout_tab.single_margin_x_spin.setValue(config.layout.single_page_margin_x)
        self.layout_tab.single_margin_y_spin.setValue(config.layout.single_page_margin_y)
        self.layout_tab.single_spacing_x_spin.setValue(config.layout.single_page_spacing_x)
        self.layout_tab.single_spacing_y_spin.setValue(config.layout.single_page_spacing_y)
        self.layout_tab.multi_margin_x_spin.setValue(config.layout.multi_page_margin_x)
        self.layout_tab.multi_margin_y_spin.setValue(config.layout.multi_page_margin_y)
        self.layout_tab.multi_header_height_spin.setValue(config.layout.multi_page_header_height)
        self.layout_tab.notes_ratio_spin.setValue(int(config.layout.notes_area_ratio * 100))
        self.layout_tab.notes_line_spacing_spin.setValue(config.layout.notes_line_spacing)
        
        # Style settings
        self.style_tab.apply_config(config)
        
        # Holidays
        self.holidays_tab.add_default_holidays_check.setChecked(config.add_default_holidays)
        self.holidays_tab.set_holidays_data(config.holidays)
        self.holidays_tab.set_special_days_data(config.special_days)
    
    def on_new(self):
        """Create new configuration."""
        reply = QMessageBox.question(
            self,
            "New Configuration",
            "Are you sure you want to create a new configuration? Unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.general_tab.reset()
            self.layout_tab.reset()
            self.style_tab.reset()
            self.holidays_tab.reset()
            self.config_path = None
            self.statusBar.showMessage("New configuration created / Новый конфиг создан")
    
    def on_open_config(self):
        """Open configuration from JSON file."""
        from PySide6.QtWidgets import QFileDialog
        from config import CalendarConfig
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Configuration / Открыть конфиг",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                config = CalendarConfig.from_json(file_path)
                self.set_config(config)
                self.config_path = file_path
                self.statusBar.showMessage(f"Configuration loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration:\n{e}")
    
    def on_save_config(self):
        """Save configuration to JSON file."""
        from PySide6.QtWidgets import QFileDialog
        
        config = self.get_config()
        
        if self.config_path:
            config.to_json(self.config_path)
            self.statusBar.showMessage(f"Configuration saved: {self.config_path}")
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Configuration / Сохранить конфиг",
                "calendar_config.json",
                "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                config.to_json(file_path)
                self.config_path = file_path
                self.statusBar.showMessage(f"Configuration saved: {file_path}")
    
    def on_render(self):
        """Render calendar with current settings."""
        from PySide6.QtWidgets import QFileDialog
        from config import CalendarConfig
        from calendar_core import CalendarBuilder, CalendarFactory

        config = self.get_config()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Render Calendar / Рендерить календарь",
            f"{config.name}.png",
            "PNG Files (*.png);;All Files (*)"
        )
        if file_path:
            try:
                # Build calendar
                builder = CalendarBuilder(config)
                builder.build_all_months()

                # Create renderer
                renderer = CalendarFactory.create_renderer(config.calendar_type)
                renderer.set_config(config)
                renderer.set_months(builder.months)
                renderer.set_holidays(builder.holidays)

                # Save
                renderer.save(file_path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Calendar rendered successfully:\n{file_path}"
                )
                self.statusBar.showMessage(f"Calendar rendered: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to render calendar:\n{e}")
    
    def on_preview(self):
        """Generate preview."""
        self.calendar_widget.on_preview()

    def on_reset(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.general_tab.reset()
            self.layout_tab.reset()
            self.style_tab.reset()
            self.holidays_tab.reset()
            self.config_path = None
            self.statusBar.showMessage("Settings reset to defaults / Настройки сброшены")
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About Calendar Maker",
            "Calendar Maker v0.2.0\n\n"
            "A tool for creating custom calendars with JSON configuration.\n\n"
            "Features:\n"
            "- Single page calendar\n"
            "- Multi-page calendar\n"
            "- Multi-page calendar with notes\n"
            "- Full JSON configuration\n"
            "- Customizable styles and layouts\n\n"
            "Created with Python, Pillow, and PySide6"
        )
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Quit",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
