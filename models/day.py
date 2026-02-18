from dataclasses import dataclass, field
from typing import Optional, Tuple
from enum import Enum


class TextAlign(Enum):
    """Text alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class BorderStyle(Enum):
    """Border style options."""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


@dataclass
class Position:
    """Position coordinates."""
    x: int = 0
    y: int = 0


@dataclass
class Size:
    """Size dimensions."""
    width: int = 100
    height: int = 100


@dataclass
class Font:
    """Font settings."""
    font_type: str = "Arial"
    font_size: int = 12
    font_color: str = "#000000"
    align: str = "left"  # left, center, right


@dataclass
class Background:
    """Background settings."""
    background_color: str = "#FFFFFF"
    background_image: Optional[str] = None  # Path to image in assets folder
    opacity: int = 255  # 0-255


@dataclass
class Border:
    """Border settings."""
    border_color: str = "#000000"
    border_width: int = 1
    border_style: str = "solid"  # solid, dashed, dotted
    border_image: Optional[str] = None


@dataclass
class Day:
    """Model representing a single day in the calendar."""
    
    # Position and size
    position: Position = field(default_factory=Position)
    size: Size = field(default_factory=lambda: Size(300, 400))
    
    # Font settings
    font: Font = field(default_factory=Font)
    
    # Background settings
    background: Background = field(default_factory=Background)
    
    # Border settings
    border: Border = field(default_factory=Border)
    
    # Holiday settings
    is_holiday: bool = False
    holiday_name: str = ""
    holiday_name_position: Position = field(default_factory=lambda: Position(10, 50))
    holiday_font: Font = field(default_factory=lambda: Font(font_size=10, font_color="#FF0000"))
    holiday_background: Background = field(default_factory=Background)
    
    # Day properties
    day_number: int = 1
    is_current_month: bool = True
    
    # Notes area (for multi-page with notes calendar type)
    has_notes_area: bool = False
    notes_position: Position = field(default_factory=lambda: Position(10, 100))
    notes_size: Size = field(default_factory=lambda: Size(280, 200))
    notes_background: Background = field(default_factory=lambda: Background(background_color="#F5F5F5"))
    notes_font: Font = field(default_factory=lambda: Font(font_size=10))
    
    # Weekend override
    is_weekend: bool = False
    weekend_background: Background = field(default_factory=lambda: Background(background_color="#FFF5F5"))
    weekend_font_color: str = "#FF0000"
