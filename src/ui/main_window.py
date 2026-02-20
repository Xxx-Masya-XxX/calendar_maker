"""Main application window."""

import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QFileDialog, QLabel, QScrollArea,
    QSplitter, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from src.ui.config_editor import ConfigEditor
from src.ui.spec_days_editor import SpecDaysEditor
from src.ui.preview_thread import PreviewThread


class CalendarMakerUI(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config_path = Path('settings.json')
        self.config = {}
        self.preview_thread = None
        self.editors = {}

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.setWindowTitle("Calendar Maker - Configuration Editor")
        # self.setMinimumSize(1400, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # Splitter for panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Tabs for sections
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Create editors (will be populated after config load)
        self.create_editors()

        # Connect signals
        for editor in self.editors.values():
            editor.changed.connect(self.on_config_changed)

        left_layout.addWidget(self.tabs)

        # Action buttons
        btn_layout = QHBoxLayout()

        load_btn = QPushButton("Load Config")
        load_btn.clicked.connect(self.load_config_dialog)
        btn_layout.addWidget(load_btn)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(save_btn)

        preview_btn = QPushButton("Update Preview")
        preview_btn.clicked.connect(self.update_preview)
        btn_layout.addWidget(preview_btn)

        left_layout.addLayout(btn_layout)

        # Right panel - preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Preview title
        preview_title = QLabel("Preview (January 2026)")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        right_layout.addWidget(preview_title)

        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        # self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.preview_label.setText("Click 'Update Preview' to generate")

        # Scroll area for preview
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.preview_label)

        right_layout.addWidget(scroll)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_editors(self):
        """Create editors with current config."""
        # Clear existing tabs
        while self.tabs.count():
            self.tabs.removeTab(0)

        # Disconnect old signals
        for editor in self.editors.values():
            editor.changed.disconnect(self.on_config_changed)

        self.editors = {}

        # Create editors for each section
        self.editors['day_of_week'] = ConfigEditor(
            "Day of Week",
            self.config.get('day_of_the_week', {}),
            show_dimensions=True
        )
        self.editors['month'] = ConfigEditor(
            "Month (Header)",
            self.config.get('month', {}),
            show_dimensions=False
        )
        self.editors['regular_day'] = ConfigEditor(
            "Regular Day",
            self.config.get('regular_day', {}),
            show_dimensions=True
        )
        self.editors['spec_day'] = ConfigEditor(
            "Special Day",
            self.config.get('spec_day', {}),
            show_dimensions=True
        )
        self.editors['weekend'] = ConfigEditor(
            "Weekend Day",
            self.config.get('weekend', {}),
            show_dimensions=True
        )
        self.editors['spec_days'] = SpecDaysEditor(
            self.config.get('spec_days', [])
        )

        # Add tabs
        self.tabs.addTab(self.editors['day_of_week'], "Day of Week")
        self.tabs.addTab(self.editors['month'], "Month")
        self.tabs.addTab(self.editors['regular_day'], "Regular Day")
        self.tabs.addTab(self.editors['spec_day'], "Special Day")
        self.tabs.addTab(self.editors['weekend'], "Weekend")
        self.tabs.addTab(self.editors['spec_days'], "Special Days")

        # Connect signals
        for editor in self.editors.values():
            editor.changed.connect(self.on_config_changed)

    def load_config(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.create_editors()
                self.status_bar.showMessage(f"Loaded: {self.config_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load config:\n{e}")

    def load_config_dialog(self):
        """Dialog for loading configuration."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json);;All Files (*)"
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

            self.status_bar.showMessage(f"Saved: {self.config_path}")
            QMessageBox.information(self, "Saved", "Configuration saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")

    def get_config(self) -> dict:
        """Get current configuration from editors."""
        return {
            'day_of_the_week': self.editors['day_of_week'].get_config(),
            'month': self.editors['month'].get_config(),
            'regular_day': self.editors['regular_day'].get_config(),
            'spec_day': self.editors['spec_day'].get_config(),
            'weekend': self.editors['weekend'].get_config(),
            'spec_days': self.editors['spec_days'].get_spec_days()
        }

    def on_config_changed(self):
        """Called when configuration changes."""
        self.status_bar.showMessage("Configuration changed. Don't forget to save!")

    def update_preview(self):
        """Update preview."""
        self.status_bar.showMessage("Generating preview...")
        self.preview_label.setText("Generating...")

        config = self.get_config()

        self.preview_thread = PreviewThread(config, 2026, 1)
        self.preview_thread.finished.connect(self.on_preview_finished)
        self.preview_thread.error.connect(self.on_preview_error)
        self.preview_thread.start()

    def on_preview_finished(self, pixmap: QPixmap):
        """Handle successful preview generation."""
        # Scale preview
        scaled = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.status_bar.showMessage("Preview updated")

    def on_preview_error(self, error: str):
        """Handle preview generation error."""
        self.preview_label.setText(f"Error:\n{error}")
        self.status_bar.showMessage(f"Error: {error}")
        QMessageBox.critical(self, "Error", f"Preview generation error:\n{error}")


def main():
    app = QApplication(sys.argv)

    # Set style
    app.setStyle("Fusion")

    window = CalendarMakerUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
