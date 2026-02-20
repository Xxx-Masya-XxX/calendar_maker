"""Day rendering logic for calendar generation."""

import numpy as np
from pathlib import Path

from src.utils.image_utils import ImageUtils
from src.utils.font_manager import FontManager
from src.utils.date_utils import DateUtils


class DayRenderer:
    """Renders individual calendar days."""

    def __init__(self, font_manager: FontManager, spec_days: dict):
        """
        Initialize day renderer.

        Args:
            font_manager: Font manager instance
            spec_days: Special days configuration dict
        """
        self.font_manager = font_manager
        self.spec_days = spec_days

    def _is_spec_day(self, day: int, month: int) -> bool:
        """Check if day is a special day."""
        date_key = DateUtils.format_spec_day_date(day, month)
        return date_key in self.spec_days

    def _get_spec_day_background(self, day: int, month: int) -> str | None:
        """Get background path for special day."""
        date_key = DateUtils.format_spec_day_date(day, month)
        if date_key in self.spec_days:
            return self.spec_days[date_key].get('background', '')
        return None

    def _get_day_config(self, day: int, month: int, weekday: int, config: dict) -> dict:
        """Get configuration for a day based on type."""
        if self._is_spec_day(day, month):
            return config['spec_day']
        elif DateUtils.is_weekend(weekday):
            return config['weekend']
        else:
            return config['regular_day']

    def create_day_image(self, day: int, month: int, weekday: int,
                         config: dict) -> np.ndarray:
        """
        Create image for a single day.

        Args:
            day: Day of month
            month: Month number
            weekday: Weekday number
            config: Full configuration dict

        Returns:
            BGRA image array
        """
        cfg = self._get_day_config(day, month, weekday, config)
        width, height = cfg['width'], cfg['height']

        # Create transparent background
        day_img = ImageUtils.create_transparent_image(width, height)

        # Check for special day background first
        spec_bg_path = self._get_spec_day_background(day, month)
        background_loaded = False

        if spec_bg_path:
            background = ImageUtils.load_background(spec_bg_path, width, height)
            if background is not None:
                day_img = ImageUtils.overlay_image(day_img, background, 0, 0)
                background_loaded = True

        # Load background from config if not loaded from spec_days
        if not background_loaded:
            bg_path = cfg.get('background')
            if bg_path:
                background = ImageUtils.load_background(bg_path, width, height)
                if background is not None:
                    day_img = ImageUtils.overlay_image(day_img, background, 0, 0)

        # Draw day number
        text_color = tuple(cfg['text_color'])  # BGR
        text_pos = tuple(cfg['text_position'])
        text_size = cfg['text_size']
        text_align = cfg.get('text_align', 'left')
        text_font = cfg.get('text_font', self.font_manager.default_font)

        # Get font
        font = self.font_manager.load_font(text_font, text_size)

        # Convert BGR to RGB for PIL
        rgb_color = (text_color[2], text_color[1], text_color[0])

        day_img = ImageUtils.draw_text(
            day_img, str(day), text_pos, rgb_color,
            font, text_align, outline=True
        )

        return day_img
