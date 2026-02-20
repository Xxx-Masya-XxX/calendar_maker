"""Main calendar generator module."""

import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

from src.utils.font_manager import FontManager
from src.utils.image_utils import ImageUtils
from src.month_renderer import MonthRenderer


class CalendarGenerator:
    """Calendar generator based on JSON configuration."""

    def __init__(self, config_path: str = 'settings.json'):
        """
        Initialize calendar generator.

        Args:
            config_path: Path to JSON configuration file
        """
        self.config = self._load_config(config_path)
        self.spec_days = self._parse_spec_days()

        # Initialize font manager
        default_font = self.config.get('regular_day', {}).get(
            'text_font', 'C:/Windows/Fonts/arial.ttf'
        )
        self.font_manager = FontManager(default_font)

        # Get month-specific configurations
        self.months_config = self.config.get('months', [])

        # Initialize month renderer
        self.month_renderer = MonthRenderer(
            self.font_manager, 
            self.spec_days, 
            self.months_config
        )

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_spec_days(self) -> dict:
        """Parse special days into {month.day: description} dict."""
        spec_days_dict = {}
        for spec_day in self.config.get('spec_days', []):
            date = spec_day['date']  # format "DD.MM"
            spec_days_dict[date] = {
                'desc': spec_day.get('desc', ''),
                'name': spec_day.get('name', ''),
                'background': spec_day.get('background', '')
            }
        return spec_days_dict

    def create_month(self, year: int, month: int) -> np.ndarray:
        """
        Create calendar for a month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            BGRA image array
        """
        return self.month_renderer.create_month(year, month, self.config)

    def create_year(self, year: int) -> list[np.ndarray]:
        """
        Create calendar for entire year.

        Args:
            year: Year

        Returns:
            List of month images
        """
        months = []
        for month in range(1, 13):
            print(f"Generating month {month}/12...")
            month_img = self.create_month(year, month)
            months.append(month_img)
        return months

    def save_month(self, month_img: np.ndarray, year: int, month: int,
                   output_dir: str = 'output') -> str:
        """
        Save month image.

        Args:
            month_img: Month image
            year: Year
            month: Month
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"{output_dir}/calendar_{year}_{month:02d}.png"
        cv2.imwrite(filename, month_img)
        return filename

    def save_year(self, months: list[np.ndarray], year: int,
                  output_dir: str = 'output') -> list[str]:
        """
        Save all months of the year.

        Args:
            months: List of month images
            year: Year
            output_dir: Output directory

        Returns:
            List of paths to saved files
        """
        filenames = []
        for i, month_img in enumerate(months):
            filename = self.save_month(month_img, year, i + 1, output_dir)
            filenames.append(filename)
            print(f"Saved: {filename}")
        return filenames


def main():
    """Main function."""
    # Initialize generator
    generator = CalendarGenerator('settings.json')

    # Year to generate
    year = 2026

    print(f"Generating calendar for {year}...")

    # Create year calendar
    months = generator.create_year(year)

    # Save months
    filenames = generator.save_year(months, year, 'output')

    print(f"\nDone! Created {len(filenames)} files:")
    for f in filenames:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
