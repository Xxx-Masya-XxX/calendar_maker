"""
Legacy entry point - redirects to src.ui.main_window.
This file is kept for backward compatibility.
"""

import warnings
warnings.warn(
    "ui.py is deprecated. Please use run_ui.py instead.",
    DeprecationWarning,
    stacklevel=2
)

from src.ui.main_window import CalendarMakerUI, main

__all__ = ['CalendarMakerUI', 'main']

if __name__ == "__main__":
    main()
