"""Utilities for parsing and converting text to spec_days format."""

import re
from typing import List, Dict


# Mapping of Russian month names to month numbers
MONTH_MAP = {
    "январь": "01",
    "февраль": "02",
    "март": "03",
    "апрель": "04",
    "май": "05",
    "июнь": "06",
    "июль": "07",
    "август": "08",
    "сентябрь": "09",
    "октябрь": "10",
    "ноябрь": "11",
    "декабрь": "12",
}


def parse_spec_days_text(text: str, default_bg: str = "", default_color: List[int] = None) -> List[Dict]:
    """
    Parse text in the format:
    
    Январь:
    16.01 - Настя Чанкина
    19.01 - б.Фая Мацик
    
    Returns a list of spec_day entries.
    
    Args:
        text: Input text with month headers and date-name pairs
        default_bg: Default background image path for all entries
        default_color: Default text color [R, G, B]
    
    Returns:
        List of dictionaries in spec_days format
    """
    if default_color is None:
        default_color = [255, 0, 0]
    
    result = []
    current_month = None
    
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a month header (e.g., "Январь:" or "Январь")
        month_match = re.match(r'^(Январь|Февраль|Март|Апрель|Май|Июнь|Июль|Август|Сентябрь|Октябрь|Ноябрь|Декабрь):?\s*$', line, re.IGNORECASE)
        if month_match:
            month_name = month_match.group(1).lower()
            current_month = MONTH_MAP.get(month_name)
            continue
        
        # Parse date-name line (e.g., "16.01 - Настя Чанкина" or "21.05 Лера Чанкина")
        # Support both formats: with " - " separator and without
        date_pattern = r'^(\d{2}\.\d{2})\s*(?:-\s*)?(.+)$'
        date_match = re.match(date_pattern, line)
        
        if date_match and current_month:
            day_part = date_match.group(1)  # e.g., "16.01"
            name = date_match.group(2).strip()
            
            # Extract just the day (DD) from the input
            day = day_part.split('.')[0]
            
            # Construct the full date using the current month
            full_date = f"{day}.{current_month}"
            
            entry = {
                "date": full_date,
                "name": name,
                "desc": "День рождения",
                "text_color": default_color,
            }
            
            if default_bg:
                entry["background"] = default_bg
            
            result.append(entry)
    
    return result


def validate_parsed_entries(entries: List[Dict]) -> List[str]:
    """
    Validate parsed spec_days entries and return list of warnings.
    
    Args:
        entries: List of parsed spec_day entries
    
    Returns:
        List of warning messages
    """
    warnings = []
    
    for entry in entries:
        date = entry.get("date", "")
        if not re.match(r'^\d{2}\.\d{2}$', date):
            warnings.append(f"Некорректный формат даты: {date}")
        
        if not entry.get("name"):
            warnings.append(f"Пустое имя для даты {date}")
    
    return warnings
