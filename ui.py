#!/usr/bin/env python3
"""
Calendar Config Editor — Entry Point
=====================================
Run this file to launch the calendar configuration editor UI.

Usage:
    python new_ui.py              # Load default config from settings.json
    python new_ui.py config.json  # Load config from specified file
"""

import sys
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.ui_components import MainWindow, STYLESHEET, DEFAULT_CONFIG


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Load config from command line argument or use default
    config = DEFAULT_CONFIG
    if len(sys.argv) > 1:
        try:
            config_path = Path(sys.argv[1])
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: could not load {sys.argv[1]}: {e}")

    win = MainWindow(config)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
