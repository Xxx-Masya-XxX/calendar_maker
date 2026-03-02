"""Generator for spec days images using OpenCV and PIL for text rendering."""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont


def load_background(path: str, width: int, height: int) -> np.ndarray:
    """Load background image with transparency support."""
    if not path or not Path(path).exists():
        # Create white background if no image provided
        bg = np.ones((height, width, 3), dtype=np.uint8) * 255
        return bg

    # Load image with alpha channel using PIL
    try:
        img = Image.open(path)
        
        # Handle transparency
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', (width, height), (255, 255, 255))
            
            # Resize image to fit canvas
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Composite with alpha
            background.paste(img_resized, (0, 0), img_resized)
            return cv2.cvtColor(np.array(background), cv2.COLOR_RGB2BGR)
        else:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize and convert to numpy array
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            return cv2.cvtColor(np.array(img_resized), cv2.COLOR_RGB2BGR)
    except Exception:
        # Fallback to white background
        bg = np.ones((height, width, 3), dtype=np.uint8) * 255
        return bg


def get_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load font from path or return default font."""
    if font_path and Path(font_path).exists():
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    
    # Try common fonts with Cyrillic support
    common_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/seguiemj.ttf",
    ]
    
    for font in common_fonts:
        if Path(font).exists():
            try:
                return ImageFont.truetype(font, size)
            except Exception:
                continue
    
    # Return default font
    return ImageFont.load_default()


def get_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple:
    """Get text size using PIL."""
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def calculate_text_position(
    text: str,
    font: ImageFont.FreeTypeFont,
    canvas_width: int,
    canvas_height: int,
    x: int,
    y: int,
    h_align: str,
    v_align: str
) -> tuple:
    """Calculate final text position based on alignment."""
    text_width, text_height = get_text_size(text, font)

    # Apply horizontal alignment
    if h_align == "left":
        pos_x = x
    elif h_align == "center":
        pos_x = x - text_width // 2
    elif h_align == "right":
        pos_x = x - text_width
    else:
        pos_x = x

    # Apply vertical alignment
    if v_align == "top":
        pos_y = y
    elif v_align == "center":
        pos_y = y - text_height // 2
    elif v_align == "bottom":
        pos_y = y - text_height
    else:
        pos_y = y

    return pos_x, pos_y


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    text: str,
    org: tuple,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    outline_color: tuple = (0, 0, 0),
    outline_width: int = 1
) -> None:
    """Draw text with outline for better visibility."""
    x, y = org

    # Draw outline (shadow) in 8 directions
    offsets = [
        (-outline_width, -outline_width), (0, -outline_width), (outline_width, -outline_width),
        (-outline_width, 0),                                       (outline_width, 0),
        (-outline_width, outline_width),  (0, outline_width),  (outline_width, outline_width)
    ]

    for dx, dy in offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

    # Draw main text
    draw.text(org, text, font=font, fill=fill)


def generate_spec_day_image(
    date_text: str,
    desc_text: str,
    date_settings: Dict,
    desc_settings: Dict,
    canvas_settings: Dict
) -> np.ndarray:
    """
    Generate a spec day image with date and description.

    Args:
        date_text: Text to display as date (e.g., "16.01")
        desc_text: Text to display as description (name(s))
        date_settings: Settings for date text
        desc_settings: Settings for description text
        canvas_settings: Canvas settings (width, height, background)

    Returns:
        Generated image as numpy array (BGR format)
    """
    width = canvas_settings.get("width", 800)
    height = canvas_settings.get("height", 600)
    bg_path = canvas_settings.get("background", "")

    # Load background
    image = load_background(bg_path, width, height)

    # Convert to PIL Image for text rendering
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # Load font for date
    date_font_size = date_settings.get("font_size", 24)
    date_font = get_font(date_settings.get("font", ""), date_font_size)

    # Calculate date position
    date_org = calculate_text_position(
        date_text,
        date_font,
        width,
        height,
        date_settings.get("x", 0),
        date_settings.get("y", 0),
        date_settings.get("h_align", "center"),
        date_settings.get("v_align", "center")
    )

    # Draw date text
    date_color = tuple(date_settings.get("color", [255, 255, 255]))
    draw_text_with_outline(draw, date_text, date_org, date_font, date_color)

    # Draw description text (may be multiline)
    desc_color = tuple(desc_settings.get("color", [255, 255, 255]))
    desc_font_size = desc_settings.get("font_size", 24)
    desc_font = get_font(desc_settings.get("font", ""), desc_font_size)

    desc_lines = desc_text.split("\n") if desc_text else []

    if desc_lines:
        # Calculate line height and total height
        line_heights = [get_text_size(line, desc_font)[1] for line in desc_lines]
        line_height = max(line_heights) if line_heights else desc_font_size
        line_spacing = int(line_height * 0.2)
        total_height = sum(line_heights) + line_spacing * (len(desc_lines) - 1)

        # Starting Y position based on vertical alignment
        base_y = desc_settings.get("y", height // 2)
        v_align = desc_settings.get("v_align", "center")

        if v_align == "top":
            current_y = base_y
        elif v_align == "center":
            current_y = base_y - total_height // 2
        else:  # bottom
            current_y = base_y - total_height

        for i, line in enumerate(desc_lines):
            line_org = calculate_text_position(
                line,
                desc_font,
                width,
                height,
                desc_settings.get("x", 0),
                current_y,
                desc_settings.get("h_align", "center"),
                "top"
            )

            draw_text_with_outline(draw, line, line_org, desc_font, desc_color)
            current_y += line_heights[i] + line_spacing

    # Convert back to OpenCV format (BGR)
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    return image


def save_spec_day_image(
    image: np.ndarray,
    output_path: str,
    date_text: str
) -> str:
    """
    Save generated image to file.

    Args:
        image: Generated image (numpy array)
        output_path: Directory to save the image
        date_text: Date text for filename

    Returns:
        Full path to saved file
    """
    # Create output directory if needed
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from date
    filename = f"spec_{date_text.replace('.', '_')}.png"
    full_path = output_dir / filename

    # Save image
    cv2.imwrite(str(full_path), image)

    return str(full_path)


def generate_all_spec_days(
    spec_days: List[Dict],
    date_settings: Dict,
    desc_settings: Dict,
    canvas_settings: Dict,
    output_dir: str
) -> List[str]:
    """
    Generate images for all spec days.

    Args:
        spec_days: List of spec day dictionaries with 'date', 'name', 'desc' keys
        date_settings: Settings for date text
        desc_settings: Settings for description text
        canvas_settings: Canvas settings
        output_dir: Directory to save generated images

    Returns:
        List of paths to generated files
    """
    generated_paths = []

    for spec_day in spec_days:
        date_text = spec_day.get("date", "")
        # Use 'name' field for the main text (as per the corrected format)
        name_text = spec_day.get("name", "")
        desc_text = spec_day.get("desc", "")

        # Combine name and desc if both exist
        if name_text and desc_text and name_text != "День рождения":
            full_desc = f"{name_text}\n{desc_text}"
        elif desc_text:
            full_desc = desc_text
        elif name_text:
            full_desc = name_text
        else:
            full_desc = ""

        image = generate_spec_day_image(
            date_text,
            full_desc,
            date_settings,
            desc_settings,
            canvas_settings
        )

        path = save_spec_day_image(image, output_dir, date_text)
        generated_paths.append(path)

    return generated_paths
