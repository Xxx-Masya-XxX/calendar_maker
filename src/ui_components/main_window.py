"""Main window for Calendar Config Editor."""

import sys
import json
import copy
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QScrollArea, QFileDialog, QMessageBox,
)

from .tabs import DaySectionTab, SpecDaysTab, MonthsTab, DaysTab
from .preview import get_day_preview, get_month_preview
from ..calendar_generator import main 

# ---------------------------------------------------------------------------
# Stylesheet
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


# ---------------------------------------------------------------------------
# Default config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "settings.json"

try:
    DEFAULT_CONFIG = json.load(open(DEFAULT_CONFIG_PATH, encoding="utf-8"))
except Exception:
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


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._day_tab: DaysTab | None = None
        self._day_of_week_tab: DaySectionTab | None = None
        self._spec_days_tab: SpecDaysTab | None = None
        self._months_tab: MonthsTab | None = None
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
        render_btn = QPushButton("💾 Сгенерировать календарь")
        btn_load.clicked.connect(self._load_json)
        btn_save.clicked.connect(self._save_json)
        render_btn.clicked.connect(self._render_calendar)
        header.addWidget(btn_load)
        header.addWidget(btn_save)
        header.addWidget(render_btn)
        root.addLayout(header)

        # --- tabs ---
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.North)

        # day_of_the_week tab (отдельно, не входит в общую вкладку)
        if "day_of_the_week" in self._config:
            self._day_of_week_tab = DaySectionTab(
                self._config["day_of_the_week"],
                show_preview_fn=get_day_preview,
            )
            self._day_of_week_tab.changed.connect(self._on_changed)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(self._day_of_week_tab)
            self._tabs.addTab(scroll, "📆 День недели")

        # Unified days tab (regular_day, weekend, spec_day)
        self._day_tab = DaysTab(self._config)
        self._day_tab.changed.connect(self._on_changed)
        self._tabs.addTab(self._day_tab, "📅 Дни")

        # spec_days tab
        self._spec_days_tab = SpecDaysTab(self._config.get("spec_days", []))
        self._spec_days_tab.changed.connect(self._on_changed)
        self._tabs.addTab(self._spec_days_tab, "🎉 Особые дни")

        # months tab
        self._months_tab = MonthsTab(self._config.get("months", []))
        self._months_tab.changed.connect(self._on_changed)
        self._tabs.addTab(self._months_tab, "🗂 Месяцы")

        root.addWidget(self._tabs)

        # status bar
        self._status = QLabel("Готово.")
        self._status.setStyleSheet("color:#5a5a8a; font-size:11px;")
        root.addWidget(self._status)

    def _on_changed(self):
        self._status.setText("Есть несохранённые изменения.")

    def _collect_config(self) -> dict:
        cfg = copy.deepcopy(self._config)
        if self._day_of_week_tab:
            cfg["day_of_the_week"] = self._day_of_week_tab.get_data()
        if self._day_tab:
            cfg.update(self._day_tab.get_data())
        if self._spec_days_tab:
            cfg["spec_days"] = self._spec_days_tab.get_data()
        if self._months_tab:
            cfg["months"] = self._months_tab.get_data()
        return cfg
    def _render_calendar(self):
        cfg = self._collect_config()
        with open("temp_config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)
        main("temp_config.json")
        self._status.setText("Календарь сгенерирован.")
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
            self._build()
            self._status.setText(f"Загружено: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")
