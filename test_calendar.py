"""Test script to generate calendars from JSON config."""
from config import CalendarConfig
from calendar_core import CalendarBuilder, CalendarFactory
from renderers import SinglePageRenderer, MultiPageRenderer, MultiPageNotesRenderer


def test_from_json_config():
    """Test generating calendar from JSON config."""
    print("Loading configuration from JSON...")
    
    # Load config from JSON
    config = CalendarConfig.from_json("config/sample_config.json")
    print(f"Calendar: {config.name}, Year: {config.year}, Type: {config.calendar_type}")
    
    # Build calendar
    builder = CalendarBuilder(config)
    builder.build_all_months()
    
    # Create renderer
    renderer = CalendarFactory.create_renderer(config.calendar_type)
    renderer.set_config(config)
    renderer.set_months(builder.months)
    renderer.set_holidays(builder.holidays)
    
    # Save calendar
    output_path = f"test_output_{config.calendar_type}.png"
    renderer.save(output_path)
    print(f"Saved: {output_path}")


def test_all_types():
    """Test generating all calendar types."""
    print("\nTesting all calendar types...")
    
    for cal_type in ["single_page", "multi_page", "multi_page_notes"]:
        config = CalendarConfig()
        config.calendar_type = cal_type
        config.name = f"Test Calendar {cal_type}"
        config.year = 2026
        
        builder = CalendarBuilder(config)
        builder.build_all_months()
        
        renderer = CalendarFactory.create_renderer(cal_type)
        renderer.set_config(config)
        renderer.set_months(builder.months)
        
        output_path = f"test_{cal_type}.png"
        renderer.save(output_path)
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    test_from_json_config()
    test_all_types()
    print("\nAll tests completed successfully!")
