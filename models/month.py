from dataclasses import dataclass, field
from typing import List, Optional
from .week import Week
from .weekday import WeekDay
from .day import Position, Size, Font, Background, Border


@dataclass
class Month:
    """Model representing a month in the calendar."""
    
    name: str = "January"
    number: int = 1
    year: int = 2026
    
    # Position and size
    position: Position = field(default_factory=Position)
    size: Size = field(default_factory=lambda: Size(2480, 3508))
    
    # Font settings
    font: Font = field(default_factory=Font)
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=Border)
    
    # Title settings
    title: str = ""
    title_position: Position = field(default_factory=lambda: Position(0, 0))
    title_size: Size = field(default_factory=lambda: Size(2480, 150))
    title_font: Font = field(default_factory=lambda: Font(font_type="Arial", font_size=48, font_color="#000000", align="center"))
    title_background: Background = field(default_factory=Background)
    title_border: Border = field(default_factory=Border)
    
    # Weeks in the month
    weeks: List[Week] = field(default_factory=list)
    
    # Weekday headers
    weekdays: List[WeekDay] = field(default_factory=list)
    
    # Layout settings
    weekday_header_height: int = 40
    week_spacing: int = 10  # Space between weeks
    day_spacing: int = 0  # Space between days
    margin: Position = field(default_factory=lambda: Position(50, 50))
    
    # Grid settings
    grid_columns: int = 7
    grid_rows: int = 6
    
    def add_week(self, week: Week) -> None:
        """Add a week to the month."""
        self.weeks.append(week)
    
    def get_weeks(self) -> List[Week]:
        """Get all weeks in the month."""
        return self.weeks
    
    def add_weekday(self, weekday: WeekDay) -> None:
        """Add a weekday header."""
        self.weekdays.append(weekday)
    
    def get_weekdays(self) -> List[WeekDay]:
        """Get all weekday headers."""
        return self.weekdays
