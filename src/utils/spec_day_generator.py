"""Special day image generator utility."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from src.day_renderer import DayRenderer
from src.utils.font_manager import FontManager
from PIL import Image, ImageDraw, ImageFont


class SpecDayGenerator:
    """Generator for creating special day preview images."""

    def __init__(
        self,
        width: int = 200,
        height: int = 200,
        background: str = "",
        # Day number settings
        day_color: List[int] = None,
        day_font: str = None,
        day_size: int = 48,
        day_position: List[int] = None,
        day_align: str = "center",
        # Name text settings
        name_text: str = "{name}",
        name_font: str = None,
        name_size: int = 24,
        name_position: List[int] = None,
        name_color: List[int] = None,
        name_align: str = "center",
        name_line_spacing: int = 5,
    ):
        """
        Initialize spec day generator.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            background: Path to background image
            day_color: Text color as [R, G, B] for day number
            day_font: Path to font file for day number
            day_size: Font size for day number
            day_position: Text position as [x, y] for day number
            day_align: Text alignment for day number (left, center, right)
            name_text: Template for name text (e.g., "{name}", "ДР: {name}")
            name_font: Path to font file for names
            name_size: Font size for names
            name_position: Text position as [x, y] for names
            name_color: Text color as [R, G, B] for names
            name_align: Text alignment for names (left, center, right)
            name_line_spacing: Spacing between name lines
        """
        self.width = width
        self.height = height
        self.background = background
        
        # Day number settings
        self.day_color = day_color or [255, 0, 255]
        self.day_font = day_font or 'C:/Windows/Fonts/arial.ttf'
        self.day_size = day_size
        self.day_position = day_position or [40, 40]
        self.day_align = day_align
        
        # Name text settings
        self.name_text = name_text
        self.name_font = name_font or self.day_font
        self.name_size = name_size
        self.name_position = name_position or [40, 100]
        self.name_color = name_color or [255, 255, 255]
        self.name_align = name_align
        self.name_line_spacing = name_line_spacing

        # Initialize font manager
        self.font_manager = FontManager(self.day_font)

    @staticmethod
    def group_by_date(spec_days: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group spec days entries by date.

        Args:
            spec_days: List of spec day dicts

        Returns:
            Dict mapping date -> list of entries for that date
        """
        grouped = defaultdict(list)
        for item in spec_days:
            date = item.get("date", "")
            if date:
                grouped[date].append(item)
        return dict(grouped)

    @staticmethod
    def get_unique_dates(spec_days: List[Dict]) -> List[Tuple[str, List[str]]]:
        """
        Get unique dates with their names.

        Args:
            spec_days: List of spec day dicts

        Returns:
            List of (date, [names]) tuples
        """
        grouped = SpecDayGenerator.group_by_date(spec_days)
        result = []
        for date, entries in sorted(grouped.items()):
            names = [e.get("name", "") for e in entries]
            result.append((date, names))
        return result

    def _create_image_with_names(
        self,
        day: int,
        month: int,
        names: List[str],
        background_override: Optional[str] = None
    ) -> np.ndarray:
        """
        Create image with day number and names.

        Args:
            day: Day of month
            month: Month number
            names: List of names to display
            background_override: Optional background override

        Returns:
            BGRA image array
        """
        # Load background
        bg_path = background_override or self.background
        if bg_path and Path(bg_path).exists():
            bg_img = Image.open(bg_path)
            bg_img = bg_img.convert("RGBA").resize((self.width, self.height))
        else:
            # Create transparent background
            bg_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        # Create draw object
        draw = ImageDraw.Draw(bg_img)

        # Load fonts
        try:
            font = ImageFont.truetype(self.day_font, self.day_size)
        except Exception:
            font = ImageFont.load_default()

        try:
            name_font = ImageFont.truetype(self.name_font, self.name_size)
        except Exception:
            name_font = font

        # Convert colors (BGR to RGB)
        rgb_color = tuple(self.day_color)
        name_rgb_color = tuple(self.name_color)

        # Draw day number
        day_str = str(day)
        bbox = draw.textbbox((0, 0), day_str, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x, y = self.day_position
        if self.day_align == "center":
            text_x = (self.width - text_w) / 2
        elif self.day_align == "right":
            text_x = self.width - text_w - x
        else:  # left
            text_x = x
        
        # Draw day number with outline
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((text_x + dx, y + dy), day_str, font=font, fill=(0, 0, 0))
        draw.text((text_x, y), day_str, font=font, fill=rgb_color)

        # Draw names
        name_x, name_y = self.name_position
        for i, name in enumerate(names):
            # Apply template
            formatted_name = self.name_text.replace("{name}", name)
            
            # Get text bounding box
            bbox = draw.textbbox((0, 0), formatted_name, font=name_font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            # Calculate x position based on name alignment
            if self.name_align == "center":
                text_x = (self.width - text_w) / 2
            elif self.name_align == "right":
                text_x = self.width - text_w - name_x
            else:  # left
                text_x = name_x

            # Calculate y position (offset for each line)
            line_offset = i * (text_h + self.name_line_spacing)
            text_y = name_y + line_offset

            # Draw text with outline
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                draw.text((text_x + dx, text_y + dy), formatted_name, font=name_font, fill=(0, 0, 0))
            
            # Draw main text
            draw.text((text_x, text_y), formatted_name, font=name_font, fill=name_rgb_color)

        # Convert to numpy array (BGRA for OpenCV)
        img_array = np.array(bg_img)
        if img_array.shape[2] == 4:
            # Convert RGBA to BGRA
            img_array = img_array[:, :, [2, 1, 0, 3]]
        else:
            # Convert RGB to BGR and add alpha
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            alpha = np.ones((img_array.shape[0], img_array.shape[1], 1), dtype=np.uint8) * 255
            img_array = np.concatenate([img_array, alpha], axis=2)

        return img_array

    def generate(
        self,
        day: int,
        month: int,
        names: List[str],
        background_override: Optional[str] = None,
    ) -> np.ndarray:
        """
        Generate image for a single spec day (with possible multiple names).

        Args:
            day: Day of month
            month: Month number (1-12)
            names: List of names to display on the image
            background_override: Optional background override for this specific day

        Returns:
            BGRA image array
        """
        return self._create_image_with_names(day, month, names, background_override)

    def generate_batch(
        self,
        spec_days: List[Dict],
        output_dir: str,
        selected_dates: Optional[List[str]] = None,
        filename_pattern: str = "spec_{date}.png",
        merge_same_date: bool = True
    ) -> List[str]:
        """
        Generate images for multiple spec days.

        Args:
            spec_days: List of spec day dicts with 'date', 'name', 'background' keys
            output_dir: Output directory path
            selected_dates: Optional list of dates to generate (if None, generate all)
            filename_pattern: Filename pattern with {date}, {month}, {day} placeholders
            merge_same_date: If True, merge multiple names on same date into one image

        Returns:
            List of generated file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if merge_same_date:
            # Group by date
            grouped = self.group_by_date(spec_days)
        else:
            # Each entry is separate
            grouped = {item.get("date", ""): [item] for item in spec_days if item.get("date")}

        generated_files = []

        for date, entries in sorted(grouped.items()):
            # Skip if not selected
            if selected_dates and date not in selected_dates:
                continue

            if not date:
                continue

            # Parse date
            parts = date.split('.')
            day = int(parts[0])
            month = int(parts[1])

            # Get names
            if merge_same_date:
                names = [e.get("name", "") for e in entries]
            else:
                names = [entries[0].get("name", "")]

            # Get background override from first entry
            bg_override = entries[0].get('background') if entries else None
            if not bg_override:
                bg_override = self.background

            # Generate image
            day_img = self.generate(day, month, names, bg_override)

            # Build filename
            filename = filename_pattern.format(
                date=date,
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
        names: List[str],
        background_override: Optional[str] = None
    ) -> bytes:
        """
        Generate image and return as PNG-encoded bytes.

        Args:
            day: Day of month
            month: Month number
            names: List of names to display
            background_override: Optional background override

        Returns:
            PNG-encoded image bytes
        """
        img = self.generate(day, month, names, background_override)
        _, buffer = cv2.imencode('.png', img)
        return buffer.tobytes()
