"""Date and calendar utilities."""

from datetime import datetime


class DateUtils:
    """Utility class for date operations."""

    MONTH_NAMES_RU = [
        '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    WEEKDAY_NAMES_RU = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    @staticmethod
    def get_month_name(month: int) -> str:
        """
        Get month name in Russian.

        Args:
            month: Month number (1-12)

        Returns:
            Month name
        """
        return DateUtils.MONTH_NAMES_RU[month]

    @staticmethod
    def get_weekday_name(weekday: int) -> str:
        """
        Get weekday name in Russian.

        Args:
            weekday: Weekday number (0=Monday, 6=Sunday)

        Returns:
            Weekday name
        """
        return DateUtils.WEEKDAY_NAMES_RU[weekday]

    @staticmethod
    def is_weekend(weekday: int) -> bool:
        """
        Check if weekday is weekend (Saturday=5, Sunday=6).

        Args:
            weekday: Weekday number (0-6)

        Returns:
            True if weekend
        """
        return weekday >= 5

    @staticmethod
    def get_first_weekday(year: int, month: int) -> int:
        """
        Get weekday of first day of month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Weekday number (0=Monday, 6=Sunday)
        """
        return datetime(year, month, 1).weekday()

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """
        Get number of days in month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Number of days
        """
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        return (datetime(next_year, next_month, 1) - datetime(year, month, 1)).days

    @staticmethod
    def format_spec_day_date(day: int, month: int) -> str:
        """
        Format date as DD.MM string.

        Args:
            day: Day of month
            month: Month number

        Returns:
            Formatted date string
        """
        return f"{day:02d}.{month:02d}"

    @staticmethod
    def parse_spec_day_date(date_str: str) -> tuple[int, int]:
        """
        Parse DD.MM string to day and month.

        Args:
            date_str: Date string in DD.MM format

        Returns:
            Tuple of (day, month)
        """
        parts = date_str.split('.')
        return int(parts[0]), int(parts[1])
