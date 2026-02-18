from abc import ABC, abstractmethod
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
import os

from models import Month, Week, Day, WeekDay, Holiday, SpecialDay
from models.day import Position, Size, Font, Background, Border
from config import CalendarConfig


class BaseRenderer(ABC):
    """Base class for all calendar renderers."""
    
    def __init__(self, config: Optional[CalendarConfig] = None):
        self.config = config or CalendarConfig()
        self.months: List[Month] = []
        self.holidays: List[Holiday] = []
        self.special_days: List[SpecialDay] = []
        
        # Default fonts path
        self.fonts_path = self._get_fonts_path()
        self.assets_path = self._get_assets_path()
    
    def _get_fonts_path(self) -> str:
        """Get the fonts directory path."""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "fonts"),
            os.path.join(os.path.dirname(__file__), "fonts"),
            "C:\\Windows\\Fonts",
            "/usr/share/fonts",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return ""
    
    def _get_assets_path(self) -> str:
        """Get the assets directory path."""
        base_paths = [
            os.path.join(os.path.dirname(__file__), "..", self.config.assets_folder),
            os.path.join(os.path.dirname(__file__), self.config.assets_folder),
            os.path.join(os.getcwd(), self.config.assets_folder),
        ]
        for path in base_paths:
            if os.path.exists(path):
                return path
        return ""
    
    def _load_font(self, font_type: str, font_size: int) -> ImageFont.FreeTypeFont:
        """Load a font, falling back to default if not found."""
        font_extensions = [".ttf", ".otf", ".ttc"]
        
        # Try to find the font file
        for ext in font_extensions:
            font_path = os.path.join(self.fonts_path, f"{font_type}{ext}")
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    pass
        
        # Try system fonts
        system_font_paths = [
            os.path.join("C:\\Windows\\Fonts", f"{font_type}{ext}")
            for ext in font_extensions
        ]
        for font_path in system_font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    pass
        
        # Fall back to default font
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            return ImageFont.load_default()
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _load_background_image(self, image_path: str, size: tuple = None) -> Optional[Image.Image]:
        """Load a background image from assets folder."""
        if not image_path:
            return None
        
        full_path = os.path.join(self.assets_path, image_path)
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path).convert("RGBA")
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                return img
            except Exception:
                pass
        return None
    
    def _draw_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        background: Background,
        border: Border,
    ) -> None:
        """Draw a rectangle with background and border."""
        # Draw background color
        draw.rectangle(
            [x, y, x + width, y + height],
            fill=self._hex_to_rgb(background.background_color)
        )
        
        # Draw background image if present
        if background.background_image:
            bg_image = self._load_background_image(background.background_image, (width, height))
            if bg_image:
                # Create a temporary RGBA canvas
                temp_canvas = Image.new("RGBA", (width, height), (255, 255, 255, 0))
                temp_canvas.paste(bg_image, (0, 0))
                # Apply opacity if needed
                if background.opacity < 255:
                    alpha = temp_canvas.split()[3]
                    alpha = alpha.point(lambda i: i * background.opacity // 255)
                    temp_canvas.putalpha(alpha)
        
        # Draw border
        if border.border_width > 0:
            if border.border_style == "solid":
                for i in range(border.border_width):
                    draw.rectangle(
                        [x + i, y + i, x + width - i - 1, y + height - i - 1],
                        outline=self._hex_to_rgb(border.border_color)
                    )
            elif border.border_style == "dashed":
                self._draw_dashed_rectangle(
                    draw, x, y, width, height, border.border_color, border.border_width
                )
            elif border.border_style == "dotted":
                self._draw_dotted_rectangle(
                    draw, x, y, width, height, border.border_color, border.border_width
                )
    
    def _draw_dashed_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        width_pixels: int,
        dash_length: int = 20,
        gap_length: int = 10,
    ) -> None:
        """Draw a dashed rectangle."""
        rgb = self._hex_to_rgb(color)
        
        # Top and bottom edges
        for i in range(0, width, dash_length + gap_length):
            end = min(i + dash_length, width)
            draw.line(
                [(x + i, y), (x + end, y)],
                fill=rgb,
                width=width_pixels
            )
            draw.line(
                [(x + i, y + height), (x + end, y + height)],
                fill=rgb,
                width=width_pixels
            )
        
        # Left and right edges
        for i in range(0, height, dash_length + gap_length):
            end = min(i + dash_length, height)
            draw.line(
                [(x, y + i), (x, y + end)],
                fill=rgb,
                width=width_pixels
            )
            draw.line(
                [(x + width, y + i), (x + width, y + end)],
                fill=rgb,
                width=width_pixels
            )
    
    def _draw_dotted_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        width_pixels: int,
        dot_spacing: int = 10,
    ) -> None:
        """Draw a dotted rectangle."""
        rgb = self._hex_to_rgb(color)
        dot_size = max(2, width_pixels)
        
        # Top and bottom edges
        for i in range(0, width, dot_spacing):
            draw.ellipse(
                [x + i, y, x + dot_size, y + dot_size],
                fill=rgb
            )
            draw.ellipse(
                [x + i, y + height - dot_size, x + dot_size, y + height],
                fill=rgb
            )
        
        # Left and right edges
        for i in range(0, height, dot_spacing):
            draw.ellipse(
                [x, y + i, x + dot_size, y + dot_size],
                fill=rgb
            )
            draw.ellipse(
                [x + width - dot_size, y + i, x + width, y + dot_size],
                fill=rgb
            )
    
    def _draw_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        font: Font,
        max_width: Optional[int] = None,
    ) -> None:
        """Draw text with specified properties."""
        font_obj = self._load_font(font.font_type, font.font_size)
        rgb = self._hex_to_rgb(font.font_color)
        
        # Get text bounding box
        bbox = font_obj.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate x position based on alignment
        if font.align == "center" and max_width:
            x = x + (max_width - text_width) // 2
        elif font.align == "right" and max_width:
            x = x + (max_width - text_width)
        
        draw.text((x, y), text, font=font_obj, fill=rgb)
    
    def _draw_day(
        self,
        draw: ImageDraw.ImageDraw,
        day: Day,
    ) -> None:
        """Draw a single day cell."""
        # Draw background and border
        self._draw_rectangle(
            draw,
            day.position.x,
            day.position.y,
            day.size.width,
            day.size.height,
            day.background,
            day.border,
        )
        
        # Draw day number at configured position (relative to day cell)
        self._draw_text(
            draw,
            str(day.day_number),
            day.position.x + self.config.day_number_position_x,
            day.position.y + self.config.day_number_position_y,
            day.font,
        )
        
        # Draw holiday name if applicable
        if day.is_holiday and day.holiday_name:
            self._draw_text(
                draw,
                day.holiday_name,
                day.position.x + self.config.holiday_text_position_x,
                day.position.y + self.config.holiday_text_position_y,
                day.holiday_font,
                max_width=day.size.width - 20,
            )
    
    def _draw_weekday_header(
        self,
        draw: ImageDraw.ImageDraw,
        weekday: WeekDay,
    ) -> None:
        """Draw a weekday header."""
        self._draw_rectangle(
            draw,
            weekday.position.x,
            weekday.position.y,
            weekday.size.width,
            weekday.size.height,
            weekday.background,
            weekday.border,
        )
        
        self._draw_text(
            draw,
            weekday.short_name,
            weekday.position.x,
            weekday.position.y + 10,
            weekday.font,
            max_width=weekday.size.width,
        )
    
    def _draw_month_header(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Draw a month header."""
        # Draw background
        self._draw_rectangle(
            draw,
            x,
            y,
            width,
            height,
            month.background,
            month.border,
        )
        
        # Draw month name at configured position
        title_text = f"{month.name} {month.year}"
        title_x = x + self.config.month_title_position_x
        title_y = y + self.config.month_title_position_y
        
        # Create font with configured settings
        title_font = Font(
            font_type=self.config.month_font_type,
            font_size=self.config.month_title_font_size,
            font_color=self.config.month_title_font_color,
            align=self.config.month_title_align,
        )
        
        self._draw_text(
            draw,
            title_text,
            title_x,
            title_y,
            title_font,
            max_width=width,
        )
    
    def add_month(self, month: Month) -> None:
        """Add a month to render."""
        self.months.append(month)
    
    def add_holiday(self, holiday: Holiday) -> None:
        """Add a holiday."""
        self.holidays.append(holiday)
    
    def add_special_day(self, special_day: SpecialDay) -> None:
        """Add a special day."""
        self.special_days.append(special_day)
    
    def set_months(self, months: list[Month]) -> None:
        """Set all months to render."""
        self.months = months
    
    def set_holidays(self, holidays: list[Holiday]) -> None:
        """Set all holidays."""
        self.holidays = holidays
    
    def set_special_days(self, special_days: list[SpecialDay]) -> None:
        """Set all special days."""
        self.special_days = special_days
    
    def set_config(self, config: CalendarConfig) -> None:
        """Set the calendar configuration."""
        self.config = config
    
    @abstractmethod
    def render(self) -> list[Image.Image]:
        """Render the calendar and return list of images."""
        pass
    
    def save(self, output_path: str) -> None:
        """Render and save the calendar to a file."""
        images = self.render()
        
        if len(images) == 1:
            images[0].save(output_path, "PNG", dpi=(self.config.canvas.dpi, self.config.canvas.dpi))
        else:
            # Save as individual files
            base, ext = os.path.splitext(output_path)
            for i, img in enumerate(images):
                img.save(f"{base}_{i+1}{ext}", "PNG", dpi=(self.config.canvas.dpi, self.config.canvas.dpi))
