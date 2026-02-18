from dataclasses import dataclass, field
from typing import Optional
from datetime import date
from .day import Position, Size, Font, Background, Border


@dataclass
class SpecialDay:
    """Model representing a special day (birthday, anniversary, etc.)."""
    
    name: str = "Birthday"
    date_value: str = "2026-01-01"  # ISO format date string
    description: str = ""
    is_recurring: bool = True
    
    # Font settings
    font: Font = field(default_factory=lambda: Font(font_type="Arial", font_size=12, font_color="#0000FF"))
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=lambda: Border(border_color="#0000FF", border_style="dashed"))
    
    # Icon or image for the special day
    icon: Optional[str] = None  # Path to image in assets folder
    
    # Priority (for rendering order)
    priority: int = 1
    
    # Display settings
    show_on_calendar: bool = True
    
    @property
    def date(self) -> date:
        """Get date object from string."""
        return date.fromisoformat(self.date_value)
    
    @date.setter
    def date(self, value: date) -> None:
        """Set date from date object."""
        self.date_value = value.isoformat()
