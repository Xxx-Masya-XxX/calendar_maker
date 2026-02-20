"""Month rendering logic for calendar generation."""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

from src.utils.image_utils import ImageUtils
from src.utils.font_manager import FontManager
from src.utils.date_utils import DateUtils
from src.day_renderer import DayRenderer


class MonthRenderer:
    """Renders calendar months."""

    def __init__(self, font_manager: FontManager, spec_days: dict):
        """
        Initialize month renderer.

        Args:
            font_manager: Font manager instance
            spec_days: Special days configuration dict
        """
        self.font_manager = font_manager
        self.spec_days = spec_days
        self.day_renderer = DayRenderer(font_manager, spec_days)

    def create_month(self, year: int, month: int, config: dict) -> np.ndarray:
        """
        Create calendar for a month.

        Args:
            year: Year
            month: Month (1-12)
            config: Configuration dict

        Returns:
            BGRA image array
        """
        day_cfg = config['regular_day']
        month_cfg = config['month']
        dow_cfg = config['day_of_the_week']

        # Dimensions
        day_width = day_cfg['width']
        day_height = day_cfg['height']
        gap = month_cfg.get('gap', 10)

        # Grid: 7 columns (days of week), 6 rows (max weeks + headers)
        cols = 7
        rows = 6

        # Calculate header heights based on font sizes
        month_size = month_cfg.get('text_size', 48)
        dow_size = dow_cfg.get('text_size', 48)
        
        # Header heights with padding (font size + padding for baseline and spacing)
        month_header_height = month_size + 40
        dow_height = dow_size + 20

        # Total dimensions
        total_width = cols * day_width + (cols + 1) * gap
        total_height = month_header_height + dow_height + rows * day_height + (rows + 1) * gap

        # Create white background
        month_img = ImageUtils.create_white_image(total_width, total_height)

        # Load month background if specified
        month_bg_path = month_cfg.get('background')
        if month_bg_path:
            month_bg = ImageUtils.load_background(month_bg_path, total_width, total_height)
            if month_bg is not None:
                month_img = ImageUtils.overlay_image(month_img, month_bg, 0, 0)

        # Draw month title
        month_name = f"{DateUtils.get_month_name(month)} {year}"
        month_color = tuple(month_cfg['text_color'])
        month_font_path = month_cfg.get('text_font', self.font_manager.default_font)
        month_font = self.font_manager.load_font(month_font_path, month_size)

        # Center title
        title_x = total_width // 2
        title_y = month_header_height // 2 + month_size // 4
        rgb_month_color = (month_color[2], month_color[1], month_color[0])
        
        # Draw month background if specified
        month_title_bg_path = month_cfg.get('title_background')
        if month_title_bg_path:
            # Calculate title background area
            title_bg_width = total_width
            title_bg_height = month_header_height
            title_bg = ImageUtils.load_background(month_title_bg_path, title_bg_width, title_bg_height)
            if title_bg is not None:
                month_img = ImageUtils.overlay_image(month_img, title_bg, 0, 0)
        
        month_img = ImageUtils.draw_text(
            month_img, month_name, (title_x, title_y),
            rgb_month_color, month_font, 'center'
        )

        # Draw days of week with background
        dow_font = self.font_manager.get_font(dow_size)

        for i in range(7):
            dow_name = DateUtils.get_weekday_name(i)
            dow_x = gap + i * (day_width + gap) + day_width // 2
            dow_y = month_header_height + dow_height // 2 + dow_size // 4

            # Weekends in red
            if i >= 5:
                dow_color = (255, 0, 0)  # Red RGB
            else:
                dow_color = tuple(reversed(dow_cfg['text_color']))  # BGR -> RGB

            # Draw day of week background if specified
            dow_bg_path = dow_cfg.get('background')
            if dow_bg_path:
                dow_bg_width = day_width
                dow_bg_height = dow_height
                dow_bg = ImageUtils.load_background(dow_bg_path, dow_bg_width, dow_bg_height)
                if dow_bg is not None:
                    dow_bg_x = gap + i * (day_width + gap)
                    dow_bg_y = month_header_height
                    month_img = ImageUtils.overlay_image(month_img, dow_bg, dow_bg_x, dow_bg_y)

            month_img = ImageUtils.draw_text(
                month_img, dow_name, (dow_x, dow_y),
                dow_color, dow_font, 'center'
            )

        # Get first weekday and days in month
        first_weekday = DateUtils.get_first_weekday(year, month)
        days_in_month = DateUtils.get_days_in_month(year, month)

        # Draw days
        start_y = month_header_height + dow_height + gap
        for day in range(1, days_in_month + 1):
            weekday = datetime(year, month, day).weekday()
            week_num = (first_weekday + day - 1) // 7
            day_num = (first_weekday + day - 1) % 7

            x = gap + day_num * (day_width + gap)
            y = start_y + week_num * (day_height + gap)

            # Create day image
            day_img = self.day_renderer.create_day_image(day, month, weekday, config)

            # Overlay on month
            month_img = ImageUtils.overlay_image(month_img, day_img, x, y)

        return month_img
