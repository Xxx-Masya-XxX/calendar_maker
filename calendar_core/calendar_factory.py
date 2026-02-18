from typing import Optional
from renderers import BaseRenderer, SinglePageRenderer, MultiPageRenderer, MultiPageNotesRenderer
from config import CalendarConfig, CalendarType


class CalendarFactory:
    """Factory for creating calendar renderers based on type."""
    
    @staticmethod
    def create_renderer(calendar_type: str) -> BaseRenderer:
        """Create a renderer based on calendar type."""
        if calendar_type == CalendarType.SINGLE_PAGE.value:
            return SinglePageRenderer()
        elif calendar_type == CalendarType.MULTI_PAGE.value:
            return MultiPageRenderer()
        elif calendar_type == CalendarType.MULTI_PAGE_NOTES.value:
            return MultiPageNotesRenderer()
        else:
            raise ValueError(f"Unknown calendar type: {calendar_type}")
    
    @staticmethod
    def get_calendar_type_enum(calendar_type: str) -> CalendarType:
        """Get CalendarType enum from string."""
        return CalendarType(calendar_type)
