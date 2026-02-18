from dataclasses import dataclass, field
from typing import Optional
from datetime import date
from .day import Position, Size, Font, Background, Border


@dataclass
class Holiday:
    """Model representing a holiday in the calendar."""
    
    name: str = "New Year"
    date_value: str = "2026-01-01"  # ISO format date string
    is_recurring: bool = True  # If True, occurs every year
    
    # Font settings
    font: Font = field(default_factory=lambda: Font(font_type="Arial", font_size=12, font_color="#FF0000"))
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=Border)
    
    # Icon or image for the holiday
    icon: Optional[str] = None  # Path to image in assets folder
    
    # Display settings
    show_on_calendar: bool = True
    display_position: str = "below_day_number"  # below_day_number, overlay
    
    @property
    def date(self) -> date:
        """Get date object from string."""
        return date.fromisoformat(self.date_value)
    
    @date.setter
    def date(self, value: date) -> None:
        """Set date from date object."""
        self.date_value = value.isoformat()
