"""Image manipulation utilities."""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class ImageUtils:
    """Utility class for image operations."""

    @staticmethod
    def ensure_bgra(image: np.ndarray) -> np.ndarray:
        """
        Ensure image has BGRA channels.

        Args:
            image: Input image

        Returns:
            Image with BGRA channels
        """
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        elif image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        return image

    @staticmethod
    def overlay_image(background: np.ndarray, foreground: np.ndarray,
                      x: int, y: int) -> np.ndarray:
        """
        Overlay foreground image on background with alpha blending.

        Args:
            background: Background image (BGRA)
            foreground: Foreground image (BGRA)
            x, y: Top-left corner position

        Returns:
            Composite image
        """
        bg = background.copy()
        fg = ImageUtils.ensure_bgra(foreground)

        fh, fw = fg.shape[:2]
        bh, bw = bg.shape[:2]

        # Check bounds
        if x >= bw or y >= bh:
            return bg

        x_end = min(x + fw, bw)
        y_end = min(y + fh, bh)
        fg_w = x_end - x
        fg_h = y_end - y

        fg_cropped = fg[:fg_h, :fg_w]
        roi = bg[y:y_end, x:x_end]

        # Alpha blending
        alpha = fg_cropped[:, :, 3].astype(float) / 255.0
        alpha_inv = 1.0 - alpha

        for c in range(3):
            fg_channel = fg_cropped[:, :, c].astype(float)
            roi_channel = roi[:, :, c].astype(float)
            roi[:, :, c] = (alpha * fg_channel + alpha_inv * roi_channel).astype(np.uint8)

        # Blend alpha channel as well
        bg_alpha = roi[:, :, 3].astype(float) / 255.0
        fg_alpha = fg_cropped[:, :, 3].astype(float) / 255.0
        new_alpha = fg_alpha + bg_alpha * (1 - fg_alpha)
        roi[:, :, 3] = (new_alpha * 255).astype(np.uint8)

        bg[y:y_end, x:x_end] = roi
        return bg

    @staticmethod
    def draw_text(img: np.ndarray, text: str, pos: tuple,
                  color: tuple, font: ImageFont.FreeTypeFont,
                  align: str = 'left', outline: bool = True) -> np.ndarray:
        """
        Draw text on image using PIL (supports Cyrillic).

        Args:
            img: Image to draw on (BGRA numpy array)
            text: Text to draw
            pos: Position (x, y)
            color: RGB color tuple
            font: PIL font object
            align: Text alignment ('left', 'center', 'right')
            outline: Add white outline for contrast

        Returns:
            Image with text
        """
        # Convert numpy array to PIL Image
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)

        # Get text dimensions for alignment
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x, y = pos

        # Horizontal alignment
        if align == 'center':
            x = x - text_width // 2
        elif align == 'right':
            x = x - text_width

        # Adjust y for PIL baseline
        y = y - text_height

        # Draw outline (white) for contrast
        if outline:
            outline_color = (255, 255, 255)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, fill=outline_color, font=font)

        # Draw main text
        draw.text((x, y), text, fill=color, font=font)

        # Convert back to numpy array
        return np.array(img_pil)

    @staticmethod
    def load_background(path: str, width: int, height: int) -> np.ndarray | None:
        """
        Load and resize background image.

        Args:
            path: Path to image file
            width: Target width
            height: Target height

        Returns:
            BGRA image or None if loading failed
        """
        if not path or not Path(path).exists():
            return None

        background = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if background is None:
            return None

        background = ImageUtils.ensure_bgra(background)
        background = cv2.resize(background, (width, height),
                                interpolation=cv2.INTER_LANCZOS4)
        return background

    @staticmethod
    def create_transparent_image(width: int, height: int) -> np.ndarray:
        """
        Create transparent BGRA image.

        Args:
            width: Image width
            height: Image height

        Returns:
            Transparent BGRA image
        """
        return np.full((height, width, 4), 0, dtype=np.uint8)

    @staticmethod
    def create_white_image(width: int, height: int) -> np.ndarray:
        """
        Create white BGRA image.

        Args:
            width: Image width
            height: Image height

        Returns:
            White BGRA image
        """
        return np.full((height, width, 4), 255, dtype=np.uint8)

    @staticmethod
    def cv2_to_qimage(img: np.ndarray) -> tuple:
        """
        Convert OpenCV image to Qt QImage compatible format.

        Args:
            img: BGRA or BGR numpy array

        Returns:
            Tuple of (rgb_data, width, height, bytes_per_line)
        """
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        if img.shape[2] == 4:
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        height, width = rgb_img.shape[:2]
        bytes_per_line = width * 4
        return rgb_img.data, width, height, bytes_per_line
