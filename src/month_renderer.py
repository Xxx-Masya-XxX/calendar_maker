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

    def __init__(self, font_manager: FontManager, spec_days: dict, months_config: list = None):
        """
        Initialize month renderer.

        Args:
            font_manager: Font manager instance
            spec_days: Special days configuration dict
            months_config: List of month-specific configurations (optional)
        """
        self.font_manager = font_manager
        self.spec_days = spec_days
        self.months_config = months_config or []
        self.day_renderer = DayRenderer(font_manager, spec_days)

    def _get_month_config(self, month: int, base_config: dict) -> dict:
        """
        Get month-specific configuration, falling back to base config.

        Args:
            month: Month number (1-12)
            base_config: Base configuration dict

        Returns:
            Merged configuration dict for the month
        """
        if not self.months_config or month < 1 or month > len(self.months_config):
            return base_config

        month_cfg = self.months_config[month - 1]
        merged = base_config.copy()

        # Override with month-specific settings
        if 'background' in month_cfg:
            merged['background'] = month_cfg['background']
        if 'text_color' in month_cfg:
            merged['text_color'] = month_cfg['text_color']
        if 'text_font' in month_cfg:
            merged['text_font'] = month_cfg['text_font']
        if 'text_size' in month_cfg:
            merged['text_size'] = month_cfg['text_size']
        if 'text_position' in month_cfg:
            merged['text_position'] = month_cfg['text_position']
        if 'text_align' in month_cfg:
            merged['text_align'] = month_cfg['text_align']
        if 'title_background' in month_cfg:
            merged['title_background'] = month_cfg['title_background']
        if 'min_width' in month_cfg:
            merged['min_width'] = month_cfg['min_width']
        if 'min_height' in month_cfg:
            merged['min_height'] = month_cfg['min_height']
        if 'width_pos' in month_cfg:
            merged['width_pos'] = month_cfg['width_pos']
        if 'height_pos' in month_cfg:
            merged['height_pos'] = month_cfg['height_pos']
        if 'padding_top' in month_cfg:
            merged['padding_top'] = month_cfg['padding_top']
        if 'padding_right' in month_cfg:
            merged['padding_right'] = month_cfg['padding_right']
        if 'padding_bottom' in month_cfg:
            merged['padding_bottom'] = month_cfg['padding_bottom']
        if 'padding_left' in month_cfg:
            merged['padding_left'] = month_cfg['padding_left']

        return merged

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
        base_month_cfg = config['month']
        month_cfg = self._get_month_config(month, base_month_cfg)
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

        # Get padding from config (support individual sides)
        padding_top = month_cfg.get('padding_top', 0)
        padding_right = month_cfg.get('padding_right', 0)
        padding_bottom = month_cfg.get('padding_bottom', 0)
        padding_left = month_cfg.get('padding_left', 0)

        # Total dimensions (content size without padding)
        content_width = cols * day_width + (cols + 1) * gap
        content_height = month_header_height + dow_height + rows * day_height + (rows + 1) * gap

        # Add padding to content dimensions
        padded_content_width = content_width + padding_left + padding_right
        padded_content_height = content_height + padding_top + padding_bottom

        # Apply min_width and min_height if specified
        min_width = month_cfg.get('min_width', 0)
        min_height = month_cfg.get('min_height', 0)
        total_width = max(padded_content_width, min_width)
        total_height = max(padded_content_height, min_height)

        # Calculate offsets for positioning content
        width_pos = month_cfg.get('width_pos', 'center')
        height_pos = month_cfg.get('height_pos', 'center')

        # Base offset includes padding
        base_offset_x = padding_left
        base_offset_y = padding_top

        if width_pos == 'left':
            offset_x = base_offset_x
        elif width_pos == 'right':
            offset_x = total_width - content_width - padding_right
        else:  # center
            offset_x = (total_width - content_width) // 2

        if height_pos == 'top':
            offset_y = base_offset_y
        elif height_pos == 'bottom':
            offset_y = total_height - content_height - padding_bottom
        else:  # center
            offset_y = (total_height - content_height) // 2

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

        # Center title (relative to content area, with offset)
        title_x = offset_x + content_width // 2
        title_y = offset_y + month_header_height // 2 + month_size // 4
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
            dow_x = offset_x + gap + i * (day_width + gap) + day_width // 2
            dow_y = offset_y + month_header_height + dow_height // 2 + dow_size // 4

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
                    dow_bg_x = offset_x + gap + i * (day_width + gap)
                    dow_bg_y = offset_y + month_header_height
                    month_img = ImageUtils.overlay_image(month_img, dow_bg, dow_bg_x, dow_bg_y)

            month_img = ImageUtils.draw_text(
                month_img, dow_name, (dow_x, dow_y),
                dow_color, dow_font, 'center'
            )

        # Get first weekday and days in month
        first_weekday = DateUtils.get_first_weekday(year, month)
        days_in_month = DateUtils.get_days_in_month(year, month)

        # Draw days
        start_y = offset_y + month_header_height + dow_height + gap
        for day in range(1, days_in_month + 1):
            weekday = datetime(year, month, day).weekday()
            week_num = (first_weekday + day - 1) // 7
            day_num = (first_weekday + day - 1) % 7

            x = offset_x + gap + day_num * (day_width + gap)
            y = start_y + week_num * (day_height + gap)

            # Create day image
            day_img = self.day_renderer.create_day_image(day, month, weekday, config)

            # Overlay on month
            month_img = ImageUtils.overlay_image(month_img, day_img, x, y)

        return month_img
