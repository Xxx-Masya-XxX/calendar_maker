# Calendar Maker

A Python application for creating custom calendars with various layouts and full JSON configuration support. Built with OpenCV, Pillow for rendering, and PySide6 for the user interface.

## Features

### Calendar Generation
- Full year calendar generation (12 months)
- Per-month image output
- Support for special days with custom backgrounds
- Weekend highlighting
- Cyrillic text support

### Full Customization via JSON
- Day cell dimensions and styling
- Font settings (type, size, color, alignment)
- Color settings for weekdays, weekends, and special days
- Background images for days and months
- Special days management with custom backgrounds

### UI Features
- Tabbed configuration interface
- Real-time preview generation
- JSON import/export
- File browsers for fonts and backgrounds
- Special days table editor

## Installation

### Using uv (recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -r requirements.txt
```

## Usage

### Graphical Interface

```bash
python run_ui.py
# or
uv run python run_ui.py
```

### Command Line Generation

```bash
python run_generator.py
# or
uv run python run_generator.py
```

### Programmatic Usage

```python
from src.calendar_generator import CalendarGenerator

# Initialize with config file
generator = CalendarGenerator('settings.json')

# Generate full year
months = generator.create_year(2026)

# Save all months
filenames = generator.save_year(months, 2026, 'output')

# Or generate single month
month_img = generator.create_month(2026, 1)
generator.save_month(month_img, 2026, 1, 'output')
```

### JSON Configuration

```json
{
  "day_of_the_week": {
    "width": 200,
    "height": 50,
    "text_color": [0, 0, 0],
    "text_position": [40, 40],
    "text_size": 48,
    "text_align": "center",
    "text_font": "C:/Windows/Fonts/arial.ttf",
    "background": "assets/img/background.png"
  },
  "month": {
    "gap": 10,
    "text_color": [0, 0, 0],
    "text_size": 48,
    "text_font": "C:/Windows/Fonts/mistral.ttf",
    "background": "assets/img/testx.jpg"
  },
  "regular_day": {
    "width": 200,
    "height": 200,
    "text_color": [0, 0, 0],
    "text_position": [40, 40],
    "text_size": 48,
    "text_align": "center",
    "text_font": "C:/Windows/Fonts/arial.ttf",
    "background": "assets/img/background.png"
  },
  "spec_day": {
    "width": 200,
    "height": 200,
    "text_color": [255, 0, 255],
    "text_position": [40, 40],
    "text_size": 48,
    "text_align": "center",
    "text_font": "C:/Windows/Fonts/arial.ttf",
    "background": "assets/img/test.jpg"
  },
  "weekend": {
    "width": 200,
    "height": 200,
    "text_color": [255, 0, 0],
    "text_position": [40, 40],
    "text_size": 48,
    "text_align": "center",
    "text_font": "C:/Windows/Fonts/arial.ttf",
    "background": "assets/img/background.png"
  },
  "spec_days": [
    {"date": "07.12", "name": "Birthday", "background": "assets/img/spec_day1.png"},
    {"date": "08.03", "name": "Women's Day", "background": "assets/img/spec_day.png"},
    {"date": "23.02", "name": "Defender of the Fatherland Day"},
    {"date": "14.02", "name": "Valentine's Day"}
  ]
}
```

## Project Structure

```
calendar_maker/
├── run_generator.py        # CLI entry point
├── run_ui.py               # GUI entry point
├── settings.json           # Configuration file
├── calendar_generator.py   # Legacy entry point (compatibility)
├── ui.py                   # Legacy entry point (compatibility)
├── src/                    # Main source directory
│   ├── __init__.py
│   ├── calendar_generator.py   # Main generator class
│   ├── day_renderer.py         # Day rendering logic
│   ├── month_renderer.py       # Month rendering logic
│   ├── ui/                     # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── config_editor.py    # Configuration editor widget
│   │   ├── spec_days_editor.py # Special days editor
│   │   └── preview_thread.py   # Preview generation thread
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── font_manager.py     # Font loading and caching
│       ├── image_utils.py      # Image manipulation utilities
│       └── date_utils.py       # Date/calendar utilities
├── assets/                 # Background images
│   └── img/
├── output/                 # Generated calendars
└── requirements.txt
```

## Module Overview

### Core (`src/`)
- **CalendarGenerator**: Main class for calendar generation
- **MonthRenderer**: Handles month layout and rendering
- **DayRenderer**: Handles individual day rendering

### Utils (`src/utils/`)
- **FontManager**: Font loading, caching, and fallback handling
- **ImageUtils**: Image operations (overlay, text drawing, format conversion)
- **DateUtils**: Date calculations and Russian locale helpers

### UI (`src/ui/`)
- **CalendarMakerUI**: Main application window
- **ConfigEditor**: Widget for editing configuration sections
- **SpecDaysEditor**: Table editor for special days
- **PreviewThread**: Background thread for preview generation

## Configuration Options

| Section | Options |
|---------|---------|
| day_of_the_week | width, height, text_color, text_position, text_size, text_align, text_font, background |
| month | gap, text_color, text_size, text_font, text_align, background |
| regular_day | width, height, text_color, text_position, text_size, text_align, text_font, background |
| spec_day | width, height, text_color, text_position, text_size, text_align, text_font, background |
| weekend | width, height, text_color, text_position, text_size, text_align, text_font, background |
| spec_days | date (DD.MM), name, desc, background |

## Output Format

- **Format:** PNG
- **Color mode:** BGRA (with alpha channel support)
- **Default resolution:** Configurable per day/month

## Requirements

- Python >= 3.12
- Pillow >= 10.0.0
- PySide6 >= 6.10.2
- OpenCV (opencv-contrib-python) >= 4.13.0
- NumPy >= 2.4.2

## License

MIT License
