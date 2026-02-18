# Calendar Maker

A Python application for creating custom calendars with various layouts and full JSON configuration support. Built with Pillow for rendering and PySide6 for the user interface.

## Features

### Three Calendar Types
- **Single Page** - all 12 months on one page (2480x3508 px)
- **Multi Page** - one month per page
- **Multi Page with Notes** - one month per page with notes section

### Full Customization via JSON
- Canvas size and DPI settings
- Layout configuration (columns, rows, margins, spacing)
- Font settings (type, size, color)
- Color settings for all elements
- Day cell sizes and borders
- Weekday header customization
- Weekend highlighting
- Holiday and special day management
- Background images support

### UI Features
- Tabbed settings interface
- Real-time preview
- JSON import/export
- Color pickers
- Holiday/special day management

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
uv run python main.py
```

### Programmatic Usage

```python
from config import CalendarConfig
from calendar_core import CalendarBuilder, CalendarFactory

# Load config from JSON
config = CalendarConfig.from_json("my_config.json")

# Or create config programmatically
config = CalendarConfig()
config.year = 2026
config.calendar_type = "single_page"
config.day_width = 350
config.day_height = 450

# Build calendar
builder = CalendarBuilder(config)
builder.build_all_months()

# Create renderer
renderer = CalendarFactory.create_renderer(config.calendar_type)
renderer.set_config(config)
renderer.set_months(builder.months)

# Save calendar
renderer.save("output.png")
```

### JSON Configuration

Each calendar configuration is saved as a JSON file. One JSON file generates one calendar.

```json
{
  "name": "My Calendar 2026",
  "year": 2026,
  "calendar_type": "single_page",
  "canvas": {
    "width": 2480,
    "height": 3508,
    "dpi": 300,
    "background_color": "#FFFFFF"
  },
  "layout": {
    "single_page_columns": 3,
    "single_page_rows": 4,
    "single_page_margin_x": 40,
    "single_page_margin_y": 40,
    "single_page_spacing_x": 20,
    "single_page_spacing_y": 20
  },
  "day_width": 300,
  "day_height": 400,
  "day_font_size": 14,
  "day_font_color": "#000000",
  "day_background_color": "#FFFFFF",
  "day_border_color": "#CCCCCC",
  "day_border_width": 1,
  "day_border_style": "solid",
  "highlight_weekends": true,
  "weekend_background_color": "#FFF5F5",
  "weekend_font_color": "#FF0000",
  "add_default_holidays": true,
  "holidays": [],
  "special_days": []
}
```

## Project Structure

```
calendar_maker/
├── main.py                 # Application entry point
├── config/                 # Configuration module
│   ├── __init__.py
│   ├── calendar_config.py  # JSON config model
│   └── sample_config.json  # Sample configuration
├── models/                 # Data models
│   ├── __init__.py
│   ├── day.py             # Day model with position/size
│   ├── week.py            # Week model
│   ├── month.py           # Month model
│   ├── holiday.py         # Holiday model
│   ├── special_day.py     # Special day model
│   └── weekday.py         # Weekday header model
├── renderers/             # Calendar renderers
│   ├── __init__.py
│   ├── base_renderer.py   # Base renderer class
│   ├── single_page_renderer.py
│   ├── multi_page_renderer.py
│   └── multi_page_notes_renderer.py
├── calendar_core/         # Calendar building logic
│   ├── __init__.py
│   ├── calendar_factory.py
│   └── calendar_builder.py
├── ui/                    # PySide6 UI components
│   ├── __init__.py
│   ├── main_window.py     # Main window
│   ├── calendar_widget.py # Preview widget
│   ├── settings_tabs.py   # Settings tabs
│   └── settings_dialog.py # Dialogs
├── assets/                # Background images folder
├── test_calendar.py       # Test script
└── requirements.txt
```

## Model Properties

### Day Model
```python
@dataclass
class Day:
    # Position and size
    position: Position      # x, y coordinates
    size: Size             # width, height
    
    # Font settings
    font: Font             # font_type, font_size, font_color, align
    
    # Background settings
    background: Background # background_color, background_image, opacity
    
    # Border settings
    border: Border         # border_color, border_width, border_style, border_image
    
    # Holiday settings
    is_holiday: bool
    holiday_name: str
    holiday_font: Font
    holiday_background: Background
```

### Configuration Options

| Category | Options |
|----------|---------|
| Canvas | width, height, dpi, background_color |
| Layout | columns, rows, margins, spacing, header_height |
| Day | width, height, font_size, font_color, background_color, border_* |
| Weekday | header_height, font_size, background_color |
| Weekend | highlight, background_color, font_color |
| Notes | area_ratio, line_spacing, title, background_color |

## Output Format

- **Format:** PNG
- **Resolution:** Configurable (default 2480x3508 px, A4 at 300 DPI)
- **Color mode:** RGB

## Requirements

- Python >= 3.12
- Pillow >= 10.0.0
- PySide6 >= 6.6.0

## License

MIT License
