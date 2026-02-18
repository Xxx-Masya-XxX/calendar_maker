from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any
import json
from datetime import date
from enum import Enum


class CalendarType(Enum):
    """Enum for calendar types."""
    SINGLE_PAGE = "single_page"
    MULTI_PAGE = "multi_page"
    MULTI_PAGE_NOTES = "multi_page_notes"


def enum_encoder(obj: Any) -> Any:
    """JSON encoder for Enum types."""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, date):
        return obj.isoformat()
    return obj


@dataclass
class CanvasSettings:
    """Canvas/image settings."""
    width: int = 2480
    height: int = 3508
    dpi: int = 300
    background_color: str = "#FFFFFF"


@dataclass
class LayoutSettings:
    """Global layout settings."""
    # Single page layout
    single_page_columns: int = 3
    single_page_rows: int = 4
    single_page_margin_x: int = 40
    single_page_margin_y: int = 40
    single_page_spacing_x: int = 20
    single_page_spacing_y: int = 20
    
    # Multi page layout
    multi_page_margin_x: int = 100
    multi_page_margin_y: int = 100
    multi_page_header_height: int = 200
    
    # Notes section
    notes_area_ratio: float = 0.35
    notes_line_spacing: int = 60


@dataclass
class CalendarConfig:
    """Main calendar configuration that gets saved to JSON."""
    
    # Basic settings
    name: str = "My Calendar"
    year: int = 2026
    calendar_type: str = "single_page"  # single_page, multi_page, multi_page_notes
    
    # Canvas settings
    canvas: CanvasSettings = field(default_factory=CanvasSettings)
    
    # Layout settings
    layout: LayoutSettings = field(default_factory=LayoutSettings)
    
    # Month settings (template for all months)
    month_font_type: str = "Arial"
    month_font_size: int = 14
    month_font_color: str = "#000000"
    month_title_font_size: int = 48
    month_title_font_color: str = "#000000"
    month_background_color: str = "#FFFFFF"
    month_background_image: str = ""  # Path to image in assets folder
    month_border_color: str = "#000000"
    month_border_width: int = 0
    
    # Month title positioning
    month_title_position_x: int = 0
    month_title_position_y: int = 20
    month_title_align: str = "center"  # left, center, right
    
    # Day settings (template for all days)
    day_width: int = 300
    day_height: int = 400
    day_font_size: int = 14
    day_font_color: str = "#000000"
    day_background_color: str = "#FFFFFF"
    day_background_image: str = ""  # Path to image in assets folder
    day_border_color: str = "#000000"
    day_border_width: int = 1
    day_border_style: str = "solid"
    day_number_align: str = "left"
    
    # Day number positioning (relative to day cell)
    day_number_position_x: int = 10
    day_number_position_y: int = 10
    
    # Holiday text positioning (relative to day cell)
    holiday_text_position_x: int = 10
    holiday_text_position_y: int = 40
    
    # Weekday header settings
    weekday_header_height: int = 40
    weekday_font_size: int = 14
    weekday_font_color: str = "#000000"
    weekday_background_color: str = "#FFFFFF"
    weekday_names: List[str] = field(default_factory=lambda: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    
    # Weekend settings
    highlight_weekends: bool = True
    weekend_background_color: str = "#FFF5F5"
    weekend_font_color: str = "#FF0000"
    weekend_days: List[int] = field(default_factory=lambda: [5, 6])  # Saturday=5, Sunday=6
    
    # Holiday settings
    add_default_holidays: bool = True
    holidays: List[dict] = field(default_factory=list)
    
    # Special days
    special_days: List[dict] = field(default_factory=list)
    
    # Assets paths
    assets_folder: str = "assets"
    
    # Notes section settings (for multi_page_notes type)
    notes_title: str = "Notes / Заметки"
    notes_background_color: str = "#F8F8F8"
    notes_font_size: int = 32
    notes_line_color: str = "#DDDDDD"
    
    @classmethod
    def from_json(cls, json_path: str) -> "CalendarConfig":
        """Load configuration from JSON file."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict) -> "CalendarConfig":
        """Create config from dictionary."""
        config = cls()
        
        # Basic settings
        config.name = data.get("name", config.name)
        config.year = data.get("year", config.year)
        config.calendar_type = data.get("calendar_type", config.calendar_type)
        
        # Canvas settings
        if "canvas" in data:
            canvas_data = data["canvas"]
            config.canvas.width = canvas_data.get("width", config.canvas.width)
            config.canvas.height = canvas_data.get("height", config.canvas.height)
            config.canvas.dpi = canvas_data.get("dpi", config.canvas.dpi)
            config.canvas.background_color = canvas_data.get("background_color", config.canvas.background_color)
        
        # Layout settings
        if "layout" in data:
            layout_data = data["layout"]
            config.layout.single_page_columns = layout_data.get("single_page_columns", config.layout.single_page_columns)
            config.layout.single_page_rows = layout_data.get("single_page_rows", config.layout.single_page_rows)
            config.layout.single_page_margin_x = layout_data.get("single_page_margin_x", config.layout.single_page_margin_x)
            config.layout.single_page_margin_y = layout_data.get("single_page_margin_y", config.layout.single_page_margin_y)
            config.layout.single_page_spacing_x = layout_data.get("single_page_spacing_x", config.layout.single_page_spacing_x)
            config.layout.single_page_spacing_y = layout_data.get("single_page_spacing_y", config.layout.single_page_spacing_y)
            config.layout.multi_page_margin_x = layout_data.get("multi_page_margin_x", config.layout.multi_page_margin_x)
            config.layout.multi_page_margin_y = layout_data.get("multi_page_margin_y", config.layout.multi_page_margin_y)
            config.layout.multi_page_header_height = layout_data.get("multi_page_header_height", config.layout.multi_page_header_height)
            config.layout.notes_area_ratio = layout_data.get("notes_area_ratio", config.layout.notes_area_ratio)
            config.layout.notes_line_spacing = layout_data.get("notes_line_spacing", config.layout.notes_line_spacing)
        
        # Month settings
        config.month_font_type = data.get("month_font_type", config.month_font_type)
        config.month_font_size = data.get("month_font_size", config.month_font_size)
        config.month_font_color = data.get("month_font_color", config.month_font_color)
        config.month_title_font_size = data.get("month_title_font_size", config.month_title_font_size)
        config.month_title_font_color = data.get("month_title_font_color", config.month_title_font_color)
        config.month_background_color = data.get("month_background_color", config.month_background_color)
        config.month_background_image = data.get("month_background_image", config.month_background_image)
        config.month_border_color = data.get("month_border_color", config.month_border_color)
        config.month_border_width = data.get("month_border_width", config.month_border_width)
        config.month_title_position_x = data.get("month_title_position_x", config.month_title_position_x)
        config.month_title_position_y = data.get("month_title_position_y", config.month_title_position_y)
        config.month_title_align = data.get("month_title_align", config.month_title_align)
        
        # Day settings
        config.day_width = data.get("day_width", config.day_width)
        config.day_height = data.get("day_height", config.day_height)
        config.day_font_size = data.get("day_font_size", config.day_font_size)
        config.day_font_color = data.get("day_font_color", config.day_font_color)
        config.day_background_color = data.get("day_background_color", config.day_background_color)
        config.day_background_image = data.get("day_background_image", config.day_background_image)
        config.day_border_color = data.get("day_border_color", config.day_border_color)
        config.day_border_width = data.get("day_border_width", config.day_border_width)
        config.day_border_style = data.get("day_border_style", config.day_border_style)
        config.day_number_align = data.get("day_number_align", config.day_number_align)
        config.day_number_position_x = data.get("day_number_position_x", config.day_number_position_x)
        config.day_number_position_y = data.get("day_number_position_y", config.day_number_position_y)
        config.holiday_text_position_x = data.get("holiday_text_position_x", config.holiday_text_position_x)
        config.holiday_text_position_y = data.get("holiday_text_position_y", config.holiday_text_position_y)
        
        # Weekday settings
        config.weekday_header_height = data.get("weekday_header_height", config.weekday_header_height)
        config.weekday_font_size = data.get("weekday_font_size", config.weekday_font_size)
        config.weekday_font_color = data.get("weekday_font_color", config.weekday_font_color)
        config.weekday_background_color = data.get("weekday_background_color", config.weekday_background_color)
        if "weekday_names" in data:
            config.weekday_names = data["weekday_names"]
        
        # Weekend settings
        config.highlight_weekends = data.get("highlight_weekends", config.highlight_weekends)
        config.weekend_background_color = data.get("weekend_background_color", config.weekend_background_color)
        config.weekend_font_color = data.get("weekend_font_color", config.weekend_font_color)
        if "weekend_days" in data:
            config.weekend_days = data["weekend_days"]
        
        # Holiday settings
        config.add_default_holidays = data.get("add_default_holidays", config.add_default_holidays)
        if "holidays" in data:
            config.holidays = data["holidays"]
        
        # Special days
        if "special_days" in data:
            config.special_days = data["special_days"]
        
        # Assets
        config.assets_folder = data.get("assets_folder", config.assets_folder)
        
        # Notes settings
        config.notes_title = data.get("notes_title", config.notes_title)
        config.notes_background_color = data.get("notes_background_color", config.notes_background_color)
        config.notes_font_size = data.get("notes_font_size", config.notes_font_size)
        config.notes_line_color = data.get("notes_line_color", config.notes_line_color)
        
        return config
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "year": self.year,
            "calendar_type": self.calendar_type,
            "canvas": {
                "width": self.canvas.width,
                "height": self.canvas.height,
                "dpi": self.canvas.dpi,
                "background_color": self.canvas.background_color,
            },
            "layout": {
                "single_page_columns": self.layout.single_page_columns,
                "single_page_rows": self.layout.single_page_rows,
                "single_page_margin_x": self.layout.single_page_margin_x,
                "single_page_margin_y": self.layout.single_page_margin_y,
                "single_page_spacing_x": self.layout.single_page_spacing_x,
                "single_page_spacing_y": self.layout.single_page_spacing_y,
                "multi_page_margin_x": self.layout.multi_page_margin_x,
                "multi_page_margin_y": self.layout.multi_page_margin_y,
                "multi_page_header_height": self.layout.multi_page_header_height,
                "notes_area_ratio": self.layout.notes_area_ratio,
                "notes_line_spacing": self.layout.notes_line_spacing,
            },
            "month_font_type": self.month_font_type,
            "month_font_size": self.month_font_size,
            "month_font_color": self.month_font_color,
            "month_title_font_size": self.month_title_font_size,
            "month_title_font_color": self.month_title_font_color,
            "month_background_color": self.month_background_color,
            "month_background_image": self.month_background_image,
            "month_border_color": self.month_border_color,
            "month_border_width": self.month_border_width,
            "month_title_position_x": self.month_title_position_x,
            "month_title_position_y": self.month_title_position_y,
            "month_title_align": self.month_title_align,
            "day_width": self.day_width,
            "day_height": self.day_height,
            "day_font_size": self.day_font_size,
            "day_font_color": self.day_font_color,
            "day_background_color": self.day_background_color,
            "day_background_image": self.day_background_image,
            "day_border_color": self.day_border_color,
            "day_border_width": self.day_border_width,
            "day_border_style": self.day_border_style,
            "day_number_align": self.day_number_align,
            "day_number_position_x": self.day_number_position_x,
            "day_number_position_y": self.day_number_position_y,
            "holiday_text_position_x": self.holiday_text_position_x,
            "holiday_text_position_y": self.holiday_text_position_y,
            "weekday_header_height": self.weekday_header_height,
            "weekday_font_size": self.weekday_font_size,
            "weekday_font_color": self.weekday_font_color,
            "weekday_background_color": self.weekday_background_color,
            "weekday_names": self.weekday_names,
            "highlight_weekends": self.highlight_weekends,
            "weekend_background_color": self.weekend_background_color,
            "weekend_font_color": self.weekend_font_color,
            "weekend_days": self.weekend_days,
            "add_default_holidays": self.add_default_holidays,
            "holidays": self.holidays,
            "special_days": self.special_days,
            "assets_folder": self.assets_folder,
            "notes_title": self.notes_title,
            "notes_background_color": self.notes_background_color,
            "notes_font_size": self.notes_font_size,
            "notes_line_color": self.notes_line_color,
        }
    
    def to_json(self, json_path: str, indent: int = 2) -> None:
        """Save configuration to JSON file."""
        data = self.to_dict()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=enum_encoder)
    
    def save(self, json_path: str) -> None:
        """Alias for to_json."""
        self.to_json(json_path)
    
    @staticmethod
    def load(json_path: str) -> "CalendarConfig":
        """Alias for from_json."""
        return CalendarConfig.from_json(json_path)
