"""Font management utilities."""

from pathlib import Path
from PIL import ImageFont


class FontManager:
    """Manages font loading and caching for calendar generation."""

    def __init__(self, default_font: str = 'C:/Windows/Fonts/arial.ttf'):
        """
        Initialize font manager.

        Args:
            default_font: Path to default font file
        """
        self.default_font = default_font
        self.font_cache: dict[int, ImageFont.FreeTypeFont] = {}
        self._init_fonts()

    def _init_fonts(self):
        """Initialize fonts for common sizes."""
        font_path = self.default_font

        # Check if font file exists
        if not Path(font_path).exists():
            # Try alternative fonts
            alt_fonts = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/times.ttf',
                'C:/Windows/Fonts/calibri.ttf',
                'C:/Windows/Fonts/consola.ttf',
            ]
            for alt in alt_fonts:
                if Path(alt).exists():
                    font_path = alt
                    break

        try:
            # Cache fonts for different sizes
            for size in [24, 32, 48, 64, 78]:
                self.font_cache[size] = ImageFont.truetype(font_path, size)
            print(f"Fonts loaded: {font_path}")
        except Exception as e:
            print(f"Font loading error: {e}")
            print("Using default font")
            for size in [24, 32, 48, 64, 78]:
                self.font_cache[size] = ImageFont.load_default()

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        Get font of nearest size.

        Args:
            size: Requested font size

        Returns:
            Font object
        """
        if size in self.font_cache:
            return self.font_cache[size]

        # Find nearest size
        sizes = sorted(self.font_cache.keys())
        closest = min(sizes, key=lambda x: abs(x - size))
        return self.font_cache[closest]

    def load_font(self, font_path: str, size: int) -> ImageFont.FreeTypeFont:
        """
        Load a specific font file.

        Args:
            font_path: Path to font file
            size: Font size

        Returns:
            Font object
        """
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return self.get_font(size)
