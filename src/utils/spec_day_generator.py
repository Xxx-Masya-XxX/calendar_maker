"""Special day image generator utility."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

from src.day_renderer import DayRenderer
from src.utils.font_manager import FontManager


class SpecDayGenerator:
    """Generator for creating special day preview images."""

    def __init__(
        self,
        width: int = 200,
        height: int = 200,
        background: str = "",
        text_color: List[int] = None,
        text_font: str = None,
        text_size: int = 48,
        text_position: List[int] = None,
        text_align: str = "center",
    ):
        """
        Initialize spec day generator.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            background: Path to background image
            text_color: Text color as [R, G, B]
            text_font: Path to font file
            text_size: Font size
            text_position: Text position as [x, y]
            text_align: Text alignment (left, center, right)
        """
        self.width = width
        self.height = height
        self.background = background
        self.text_color = text_color or [255, 0, 255]
        self.text_font = text_font or 'C:/Windows/Fonts/arial.ttf'
        self.text_size = text_size
        self.text_position = text_position or [40, 40]
        self.text_align = text_align

        # Initialize font manager
        self.font_manager = FontManager(self.text_font)

    def generate(
        self,
        day: int,
        month: int,
        background_override: Optional[str] = None,
    ) -> np.ndarray:
        """
        Generate image for a single spec day.

        Args:
            day: Day of month
            month: Month number (1-12)
            background_override: Optional background override for this specific day

        Returns:
            BGRA image array
        """
        # Use override background or default
        bg = background_override or self.background

        # Create config for renderer
        config = {
            'spec_day': {
                'width': self.width,
                'height': self.height,
                'background': bg,
                'text_color': self.text_color,
                'text_font': self.text_font,
                'text_size': self.text_size,
                'text_position': self.text_position,
                'text_align': self.text_align,
            }
        }

        # Create spec_days dict for renderer (with background)
        date_key = f"{day:02d}.{month:02d}"
        spec_days_dict = {date_key: {'background': bg}} if bg else {}

        # Create renderer
        renderer = DayRenderer(self.font_manager, spec_days_dict)

        # Generate image (weekday=0 for preview/generation)
        day_img = renderer.create_day_image(day, month, 0, config)

        return day_img

    def generate_batch(
        self,
        spec_days: List[Dict],
        output_dir: str,
        filename_pattern: str = "spec_{date}_{name}.png"
    ) -> List[str]:
        """
        Generate images for multiple spec days.

        Args:
            spec_days: List of spec day dicts with 'date', 'name', 'background' keys
            output_dir: Output directory path
            filename_pattern: Filename pattern with {date}, {name}, {month} placeholders

        Returns:
            List of generated file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for item in spec_days:
            date = item.get("date", "")
            if not date:
                continue

            # Parse date
            parts = date.split('.')
            day = int(parts[0])
            month = int(parts[1])

            # Get background override from item
            bg_override = item.get('background') or self.background

            # Generate image
            day_img = self.generate(day, month, bg_override)

            # Build filename
            name = item.get("name", "").replace(" ", "_").replace("/", "_")
            filename = filename_pattern.format(
                date=date,
                name=name,
                month=f"{month:02d}",
                day=f"{day:02d}"
            )

            # Save
            filepath = output_path / filename
            cv2.imwrite(str(filepath), day_img)
            generated_files.append(str(filepath))

        return generated_files

    def generate_to_buffer(
        self,
        day: int,
        month: int,
        background_override: Optional[str] = None
    ) -> bytes:
        """
        Generate image and return as PNG-encoded bytes.

        Args:
            day: Day of month
            month: Month number
            background_override: Optional background override

        Returns:
            PNG-encoded image bytes
        """
        img = self.generate(day, month, background_override)
        _, buffer = cv2.imencode('.png', img)
        return buffer.tobytes()
