"""Preview functions for Calendar Config Editor."""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QPixmap, QImage

from src.utils.font_manager import FontManager
from src.day_renderer import DayRenderer
from src.month_renderer import MonthRenderer


# ---------------------------------------------------------------------------
# Global instances for preview rendering (cached to avoid re-initialization)
# ---------------------------------------------------------------------------

_preview_font_manager = None
_preview_day_renderer = None
_preview_full_config = None


def _get_preview_font_manager():
    """Get cached font manager for preview rendering."""
    global _preview_font_manager
    if _preview_font_manager is None:
        _preview_font_manager = FontManager()
    return _preview_font_manager


def _get_preview_day_renderer(spec_days=None):
    """Get cached day renderer for preview rendering."""
    global _preview_day_renderer
    if _preview_day_renderer is None:
        _preview_day_renderer = DayRenderer(_get_preview_font_manager(), spec_days or {})
    return _preview_day_renderer


def _get_full_config_for_preview() -> dict:
    """Load full config from settings.json for month preview."""
    global _preview_full_config
    if _preview_full_config is None:
        # Try to load from settings.json in the same directory as the calling script
        # First try relative to this file
        settings_path = Path(__file__).parent.parent / "settings.json"
        if not settings_path.exists():
            # Try current working directory
            settings_path = Path("settings.json")
        
        if settings_path.exists():
            import json
            with open(settings_path, 'r', encoding='utf-8') as f:
                _preview_full_config = json.load(f)
        else:
            # Fallback to minimal config
            _preview_full_config = {
                'regular_day': {
                    'width': 200, 'height': 200, 'text_color': [0, 0, 0],
                    'text_position': [40, 40], 'text_size': 48, 'text_align': 'center',
                    'padding': 20, 'text_font': 'C:/Windows/Fonts/arial.ttf'
                },
                'weekend': {
                    'width': 200, 'height': 200, 'text_color': [255, 0, 0],
                    'text_position': [40, 40], 'text_size': 48, 'text_align': 'center',
                    'padding': 20, 'text_font': 'C:/Windows/Fonts/arial.ttf'
                },
                'spec_day': {
                    'width': 200, 'height': 200, 'text_color': [255, 0, 255],
                    'text_position': [40, 40], 'text_size': 48, 'text_align': 'center',
                    'padding': 20, 'text_font': 'C:/Windows/Fonts/arial.ttf'
                },
                'day_of_the_week': {
                    'width': 200, 'height': 50, 'text_color': [0, 0, 0],
                    'text_position': [40, 40], 'text_size': 48, 'text_align': 'center',
                    'text_font': 'C:/Windows/Fonts/arial.ttf'
                },
                'month': {
                    'gap': 30, 'text_color': [0, 0, 0], 'text_size': 98,
                    'text_font': 'C:/Windows/Fonts/mistral.ttf', 'text_align': 'center',
                    'month_text_height': 200
                },
                'months': []
            }
    return _preview_full_config


def _cv2_to_pixmap(img: np.ndarray) -> QPixmap:
    """Convert OpenCV BGRA image to Qt QPixmap."""
    if img is None:
        return QPixmap()

    # Convert BGRA to RGBA for Qt
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # BGRA -> RGBA
    rgba = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

    height, width = rgba.shape[:2]
    bytes_per_line = width * 4

    # Create QImage from data
    qimage = QImage(rgba.data, width, height, bytes_per_line, QImage.Format_RGBA8888)

    # Copy to avoid data lifetime issues
    qimage = qimage.copy()

    return QPixmap.fromImage(qimage)


def get_day_preview(config: dict) -> "QPixmap | None":
    """Return a QPixmap preview for a regular/weekend/spec day cell config."""
    try:
        # Get dimensions from config
        width = config.get('width', 200)
        height = config.get('height', 200)

        # Create a minimal spec_days dict for preview (use first day of current month)
        spec_days = {
            "01.01": {
                'desc': '',
                'name': '',
                'background': config.get('background', '')
            }
        }

        # Get renderer
        renderer = _get_preview_day_renderer(spec_days)

        # Use current date for preview
        now = datetime.now()
        day = 15  # Use middle of month for preview
        month = now.month
        weekday = 2  # Wednesday (weekday)

        # Create day image using the renderer
        day_img = renderer.create_day_image(day, month, weekday, {'regular_day': config})

        # Scale down for preview if too large
        max_preview_size = 300
        if day_img.shape[0] > max_preview_size or day_img.shape[1] > max_preview_size:
            scale = min(max_preview_size / day_img.shape[0], max_preview_size / day_img.shape[1])
            new_size = (int(day_img.shape[1] * scale), int(day_img.shape[0] * scale))
            day_img = cv2.resize(day_img, new_size, interpolation=cv2.INTER_LANCZOS4)

        return _cv2_to_pixmap(day_img)
    except Exception as e:
        print(f"Day preview error: {e}")
        return None


def get_month_preview(config: dict) -> "QPixmap | None":
    """Return a QPixmap preview for a month page config."""
    try:
        # Get full config and update with the passed month config
        full_config = _get_full_config_for_preview()

        # Find which month index this config corresponds to
        months_config = full_config.get('months', [])
        month_index = -1
        for i, m_cfg in enumerate(months_config):
            if m_cfg is config:
                month_index = i
                break

        # If not found in list, use the config directly (for editor preview)
        if month_index >= 0:
            # Use the actual month from config list
            month_num = month_index + 1
        else:
            # Use current month for preview
            month_num = datetime.now().month

        # Create font manager and renderer
        font_manager = _get_preview_font_manager()
        spec_days = {}
        renderer = MonthRenderer(font_manager, spec_days, months_config)

        # Use current year
        year = datetime.now().year

        # Create month image
        month_img = renderer.create_month(year, month_num, full_config)

        # Scale down for preview if too large
        max_preview_size = 400
        if month_img.shape[0] > max_preview_size or month_img.shape[1] > max_preview_size:
            scale = min(max_preview_size / month_img.shape[0], max_preview_size / month_img.shape[1])
            new_size = (int(month_img.shape[1] * scale), int(month_img.shape[0] * scale))
            month_img = cv2.resize(month_img, new_size, interpolation=cv2.INTER_LANCZOS4)

        return _cv2_to_pixmap(month_img)
    except Exception as e:
        print(f"Month preview error: {e}")
        return None
