from dataclasses import dataclass, field
from typing import List, Optional
from .day import Day, Position, Size, Font, Background, Border


@dataclass
class Week:
    """Model representing a week in the calendar."""
    
    # Position and size
    position: Position = field(default_factory=Position)
    size: Size = field(default_factory=lambda: Size(2100, 400))
    
    # Font settings
    font: Font = field(default_factory=Font)
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=Border)
    
    # Days in the week
    days: List[Day] = field(default_factory=list)
    
    # Week number
    week_number: int = 1
    
    # Layout settings
    day_spacing: int = 0  # Space between days
    show_week_number: bool = False
    week_number_position: Position = field(default_factory=lambda: Position(5, 5))
    week_number_font: Font = field(default_factory=lambda: Font(font_size=10))
    
    def add_day(self, day: Day) -> None:
        """Add a day to the week."""
        self.days.append(day)
    
    def get_days(self) -> List[Day]:
        """Get all days in the week."""
        return self.days
