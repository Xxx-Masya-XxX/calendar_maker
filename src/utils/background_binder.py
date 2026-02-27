"""Background binding utility for special days."""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class BackgroundBinder:
    """Utility for binding generated background images to special days."""

    # Patterns to match date in filename
    DATE_PATTERNS = [
        r'(\d{2}\.\d{2})',  # bg_16.01.png
        r'(\d{2}-\d{2})',   # bg_16-01.png
        r'(\d{4})(\d{2})(\d{2})',  # 20260116.png
    ]

    def __init__(self, supported_extensions: List[str] = None):
        """
        Initialize binder.

        Args:
            supported_extensions: List of supported image extensions
        """
        self.supported_extensions = supported_extensions or [
            '.png', '.jpg', '.jpeg', '.bmp', '.webp'
        ]

    def scan_folder(self, folder_path: str) -> Dict[str, str]:
        """
        Scan folder for images with date patterns in filename.

        Args:
            folder_path: Path to folder with generated images

        Returns:
            Dict mapping date (DD.MM) -> file path
        """
        folder = Path(folder_path)
        if not folder.exists():
            return {}

        date_to_file = {}

        for ext in self.supported_extensions:
            for file_path in folder.glob(f'*{ext}'):
                date = self._extract_date_from_filename(file_path.name)
                if date:
                    # Normalize to DD.MM format
                    date_to_file[date] = str(file_path)

        return date_to_file

    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from filename.

        Args:
            filename: Name of file

        Returns:
            Date in DD.MM format or None
        """
        # Remove extension
        name = Path(filename).stem

        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, name)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # DD.MM or DD-MM
                    day, month = groups
                    if '-' in pattern:
                        return f"{day}.{month}"
                    return f"{day}.{month}"
                elif len(groups) == 3:
                    # YYYYMMDD
                    year, month, day = groups
                    return f"{day}.{month}"

        return None

    def bind_to_spec_days(
        self,
        spec_days: List[Dict],
        folder_path: str,
        filename_pattern: str = "spec_{date}.png"
    ) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Bind background images to special days.

        Args:
            spec_days: List of special day entries
            folder_path: Path to folder with generated images
            filename_pattern: Expected filename pattern (for info)

        Returns:
            Tuple of (updated spec_days list, dict of bindings made)
        """
        # Scan folder for images
        date_to_file = self.scan_folder(folder_path)

        # Track bindings
        bindings = {}
        updated_days = []

        for entry in spec_days:
            date = entry.get('date', '')
            if not date:
                updated_days.append(entry)
                continue

            # Check if we have a background for this date
            bg_path = date_to_file.get(date)

            new_entry = entry.copy()
            if bg_path:
                new_entry['background'] = bg_path
                bindings[date] = bg_path

            updated_days.append(new_entry)

        return updated_days, bindings


def bind_backgrounds_to_spec_days(
    spec_days: List[Dict],
    folder_path: str
) -> Tuple[List[Dict], Dict[str, str]]:
    """
    Convenience function to bind backgrounds to special days.

    Args:
        spec_days: List of special day entries
        folder_path: Path to folder with generated images

    Returns:
        Tuple of (updated spec_days list, dict of bindings made)
    """
    binder = BackgroundBinder()
    return binder.bind_to_spec_days(spec_days, folder_path)
