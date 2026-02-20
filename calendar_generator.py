"""
Legacy entry point - redirects to src.calendar_generator.
This file is kept for backward compatibility.
"""

from src.calendar_generator import CalendarGenerator, main

__all__ = ['CalendarGenerator', 'main']

if __name__ == "__main__":
    main()
