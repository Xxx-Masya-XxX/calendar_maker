from dataclasses import dataclass, field
from typing import Optional
from .day import Position, Size, Font, Background, Border


@dataclass
class WeekDay:
    """Model representing a weekday header (Mon, Tue, etc.)."""
    
    name: str = "Monday"
    short_name: str = "Mon"
    
    # Position and size
    position: Position = field(default_factory=Position)
    size: Size = field(default_factory=lambda: Size(300, 40))
    
    # Font settings
    font: Font = field(default_factory=Font)
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=Border)
    
    # Is weekend
    is_weekend: bool = False
    
    # Layout
    day_spacing: int = 0  # Space between weekday headers
