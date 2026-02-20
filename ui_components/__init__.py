"""UI components for Calendar Config Editor."""

# Constants
from ui_components.constants import (
    DAYS_OF_WEEK,
    FONT_PRESETS,
    ALIGN_OPTIONS,
    WIDTH_POS_OPTIONS,
    HEIGHT_POS_OPTIONS,
)

# Helpers
from ui_components.helpers import (
    color_from_list,
    list_from_color,
    color_swatch,
)

# Widgets
from ui_components.widgets import (
    ColorPickerWidget,
    ImagePickerWidget,
    FontPickerWidget,
    PreviewLabel,
)

# Tabs
from ui_components.tabs import (
    DaySectionTab,
    SpecDaysTab,
    MonthsTab,
)

# Preview
from ui_components.preview import (
    get_day_preview,
    get_month_preview,
)

# Main window
from ui_components.main_window import (
    MainWindow,
    STYLESHEET,
    DEFAULT_CONFIG,
)

__all__ = [
    # Constants
    "DAYS_OF_WEEK",
    "FONT_PRESETS",
    "ALIGN_OPTIONS",
    "WIDTH_POS_OPTIONS",
    "HEIGHT_POS_OPTIONS",
    # Helpers
    "color_from_list",
    "list_from_color",
    "color_swatch",
    # Widgets
    "ColorPickerWidget",
    "ImagePickerWidget",
    "FontPickerWidget",
    "PreviewLabel",
    # Tabs
    "DaySectionTab",
    "SpecDaysTab",
    "MonthsTab",
    # Preview
    "get_day_preview",
    "get_month_preview",
    # Main
    "MainWindow",
    "STYLESHEET",
    "DEFAULT_CONFIG",
]
