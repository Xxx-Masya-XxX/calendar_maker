"""Main application window - Modern UI."""

import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QScrollArea,
    QMessageBox, QStatusBar, QFrame, QStackedWidget, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from src.ui.editors.month_editor import MonthEditor
from src.ui.editors.day_editor import DayEditor
from src.ui.editors.spec_days_editor import SpecDaysEditor
from src.ui.editors.general_settings_editor import GeneralSettingsEditor
from src.ui.preview_widget import PreviewWidget
from src.ui.preview_thread import PreviewThread


class NavigationButton(QPushButton):
    """Styled navigation button."""
    
    def __init__(self, text: str, icon: str = None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)


class CalendarMakerUI(QMainWindow):
    """Main application window with modern UI."""

    config_changed = Signal()

    def __init__(self):
        super().__init__()
        self.config_path = Path('settings.json')
        self.config = {}
        self.preview_thread = None
        self.editors = {}
        self.current_section = 'general'

        self.setup_ui()
        self.load_config()

    def closeEvent(self, event):
        """Handle application close."""
        # Stop preview thread if running
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait()
        event.accept()

    def setup_ui(self):
        self.setWindowTitle("Calendar Maker - Редактор конфигурации")
        self.setMinimumSize(1400, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar - navigation
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Center - editor area
        editor_container = self.create_editor_area()
        main_layout.addWidget(editor_container)

        # Right - preview
        preview_panel = self.create_preview_panel()
        main_layout.addWidget(preview_panel)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

        # Apply stylesheet
        self.apply_styles()

    def create_sidebar(self) -> QWidget:
        """Create left sidebar with navigation."""
        sidebar = QFrame()
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Logo/title
        title = QLabel("Calendar Maker")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Navigation buttons
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)

        self.nav_buttons = {}
        sections = [
            ('general', 'Общие настройки'),
            ('month', 'Месяцы'),
            ('day_of_week', 'Дни недели'),
            ('regular_day', 'Обычный день'),
            ('weekend', 'Выходной'),
            ('spec_day', 'Специальный день'),
            ('spec_days', 'Список праздников'),
        ]

        for section_id, text in sections:
            btn = NavigationButton(text)
            btn.clicked.connect(lambda checked, s=section_id: self.switch_section(s))
            nav_layout.addWidget(btn)
            self.nav_buttons[section_id] = btn

        nav_layout.addStretch()
        layout.addWidget(nav_widget)

        # Action buttons at bottom
        action_widget = QWidget()
        action_layout = QVBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 10, 5, 10)
        action_layout.setSpacing(5)

        load_btn = QPushButton("Загрузить")
        load_btn.clicked.connect(self.load_config_dialog)
        action_layout.addWidget(load_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_config)
        action_layout.addWidget(save_btn)

        preview_btn = QPushButton("Обновить превью")
        preview_btn.clicked.connect(self.update_preview)
        action_layout.addWidget(preview_btn)

        layout.addWidget(action_widget)

        return sidebar

    def create_editor_area(self) -> QWidget:
        """Create center editor area."""
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Section title
        self.section_title = QLabel("Общие настройки")
        self.section_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.section_title)

        # Stacked widget for different sections
        self.editor_stack = QStackedWidget()

        # Create editors
        self.editors['general'] = GeneralSettingsEditor()
        self.editors['month'] = MonthEditor()
        self.editors['day_of_week'] = DayEditor("День недели", show_header_options=True)
        self.editors['regular_day'] = DayEditor("Обычный день")
        self.editors['weekend'] = DayEditor("Выходной день")
        self.editors['spec_day'] = DayEditor("Специальный день")
        self.editors['spec_days'] = SpecDaysEditor()

        for editor in self.editors.values():
            editor.changed.connect(self.on_config_changed)
            self.editor_stack.addWidget(editor)

        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setWidget(self.editor_stack)

        layout.addWidget(scroll)

        return container

    def create_preview_panel(self) -> QWidget:
        """Create right preview panel."""
        panel = QFrame()
        panel.setFixedWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Предпросмотр")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Preview widget
        self.preview = PreviewWidget()
        self.preview.setMinimumSize(300, 300)
        layout.addWidget(self.preview)

        # Month selector
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Месяц:"))
        
        self.month_selector = QComboBox()
        self.month_selector.addItems([
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ])
        self.month_selector.currentIndexChanged.connect(self.update_preview)
        month_layout.addWidget(self.month_selector)

        self.year_selector = QSpinBox()
        self.year_selector.setRange(2000, 2100)
        self.year_selector.setValue(2026)
        self.year_selector.valueChanged.connect(self.update_preview)
        month_layout.addWidget(self.year_selector)

        layout.addLayout(month_layout)

        # Info label
        self.preview_info = QLabel("Нажмите 'Обновить превью' для генерации")
        self.preview_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_info)

        layout.addStretch()

        return panel

    def switch_section(self, section_id: str):
        """Switch to different editor section."""
        self.current_section = section_id

        # Update navigation buttons
        for btn_id, btn in self.nav_buttons.items():
            btn.setChecked(btn_id == section_id)

        # Update editor stack
        section_titles = {
            'general': 'Общие настройки',
            'month': 'Настройки месяцев',
            'day_of_week': 'Дни недели',
            'regular_day': 'Обычный день',
            'weekend': 'Выходной день',
            'spec_day': 'Специальный день',
            'spec_days': 'Список праздников',
        }
        self.section_title.setText(section_titles.get(section_id, ''))
        self.editor_stack.setCurrentWidget(self.editors[section_id])

    def apply_styles(self):
        """Apply application-wide styles."""
        pass

    def get_button_style(self, color: str) -> str:
        """Get styled button CSS."""
        return ""

    def load_config(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.populate_editors()
                self.status_bar.showMessage(f"Загружено: {self.config_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить конфиг:\n{e}")

    def load_config_dialog(self):
        """Dialog for loading configuration."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить конфигурацию", "", "JSON Files (*.json);;All Files (*)"
        )
        if path:
            self.config_path = Path(path)
            self.load_config()

    def save_config(self):
        """Save configuration."""
        self.config = self.get_config()

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            self.status_bar.showMessage(f"Сохранено: {self.config_path}")
            QMessageBox.information(self, "Успех", "Конфигурация успешно сохранена!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфиг:\n{e}")

    def get_config(self) -> dict:
        """Get current configuration from editors."""
        config = {
            'day_of_the_week': self.editors['day_of_week'].get_config(),
            'month': self.editors['month'].get_month_config(),
            'months': self.editors['month'].get_months_list(),
            'regular_day': self.editors['regular_day'].get_config(),
            'spec_day': self.editors['spec_day'].get_config(),
            'weekend': self.editors['weekend'].get_config(),
            'spec_days': self.editors['spec_days'].get_spec_days()
        }
        
        # Add general settings if exists
        if 'general' in self.editors:
            general = self.editors['general'].get_config()
            if general:
                config.update(general)
        
        return config

    def populate_editors(self):
        """Populate editors with loaded config."""
        self.editors['general'].set_config(self.config.get('general', {}))
        self.editors['month'].set_config(
            self.config.get('month', {}),
            self.config.get('months', [])
        )
        self.editors['day_of_week'].set_config(self.config.get('day_of_the_week', {}))
        self.editors['regular_day'].set_config(self.config.get('regular_day', {}))
        self.editors['weekend'].set_config(self.config.get('weekend', {}))
        self.editors['spec_day'].set_config(self.config.get('spec_day', {}))
        self.editors['spec_days'].set_spec_days(self.config.get('spec_days', []))

    def on_config_changed(self):
        """Called when configuration changes."""
        self.status_bar.showMessage("Конфигурация изменена. Не забудьте сохранить!")
        self.config_changed.emit()

    def update_preview(self):
        """Update preview."""
        self.preview_info.setText("Генерация...")
        self.preview.clear()

        # Stop previous thread if running
        if self.preview_thread and self.preview_thread.isRunning():
            self.preview_thread.quit()
            self.preview_thread.wait()

        config = self.get_config()
        month = self.month_selector.currentIndex() + 1
        year = self.year_selector.value()

        self.preview_thread = PreviewThread(config, year, month)
        self.preview_thread.finished.connect(self.on_preview_finished)
        self.preview_thread.error.connect(self.on_preview_error)
        self.preview_thread.start()

    def on_preview_finished(self, pixmap: QPixmap):
        """Handle successful preview generation."""
        self.preview.set_image(pixmap)
        month_name = self.month_selector.currentText()
        year = self.year_selector.value()
        self.preview_info.setText(f"Предпросмотр: {month_name} {year}")
        self.status_bar.showMessage("Превью обновлено")

    def on_preview_error(self, error: str):
        """Handle preview generation error."""
        self.preview_info.setText(f"Ошибка:\n{error}")
        self.status_bar.showMessage(f"Ошибка: {error}")
        QMessageBox.critical(self, "Ошибка", f"Ошибка генерации превью:\n{error}")


def main():
    app = QApplication(sys.argv)

    window = CalendarMakerUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
