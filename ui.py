"""
Legacy entry point - redirects to src.ui.main_window.
This file is kept for backward compatibility.
"""

from src.ui.main_window import CalendarMakerUI, main

__all__ = ['CalendarMakerUI', 'main']

if __name__ == "__main__":
    main()
