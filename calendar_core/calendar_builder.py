from datetime import date
from typing import List, Optional
from calendar import monthrange as calendar_monthrange

from models import Month, Week, Day, WeekDay, Holiday, SpecialDay
from models.day import Position, Size, Font, Background, Border
from config import CalendarConfig


class CalendarBuilder:
    """Builder class for creating calendar data structures from config."""

    WEEKDAY_NAMES = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    def __init__(self, config: CalendarConfig):
        self.config = config
        self.year = config.year
        self.months: List[Month] = []
        self.holidays: List[Holiday] = []
        self.special_days: List[SpecialDay] = []

        # Load holidays from config
        self._load_holidays_from_config()
        self._load_special_days_from_config()

    def _load_holidays_from_config(self):
        """Load holidays from config."""
        if self.config.add_default_holidays:
            self.add_default_holidays()

        # Load custom holidays from config
        for holiday_data in self.config.holidays:
            # Handle both formats: with 'date' string or separate month/day
            if "date" in holiday_data:
                date_str = holiday_data["date"]
            else:
                # Build date from month/day
                month = holiday_data.get("month", 1)
                day = holiday_data.get("day", 1)
                date_str = f"{self.year:04d}-{month:02d}-{day:02d}"
            
            holiday = Holiday(
                name=holiday_data.get("name", "Holiday"),
                date_value=date_str,
                is_recurring=holiday_data.get("is_recurring", True),
            )
            if "font_color" in holiday_data:
                holiday.font.font_color = holiday_data["font_color"]
            if "color" in holiday_data:
                holiday.font.font_color = holiday_data["color"]
            self.holidays.append(holiday)

    def _load_special_days_from_config(self):
        """Load special days from config."""
        for special_day_data in self.config.special_days:
            # Handle both formats: with 'date' string or separate month/day
            if "date" in special_day_data:
                date_str = special_day_data["date"]
            else:
                # Build date from month/day
                month = special_day_data.get("month", 1)
                day = special_day_data.get("day", 1)
                date_str = f"{self.year:04d}-{month:02d}-{day:02d}"
            
            special_day = SpecialDay(
                name=special_day_data.get("name", "Special Day"),
                date_value=date_str,
                description=special_day_data.get("description", ""),
                is_recurring=special_day_data.get("is_recurring", True),
            )
            if "font_color" in special_day_data:
                special_day.font.font_color = special_day_data["font_color"]
            if "color" in special_day_data:
                special_day.font.font_color = special_day_data["color"]
            self.special_days.append(special_day)

    def add_holiday(
        self,
        name: str,
        month: int,
        day: int,
        is_recurring: bool = True,
        font_color: str = "#FF0000",
    ) -> None:
        """Add a holiday to the calendar."""
        holiday = Holiday(
            name=name,
            date_value=f"{self.year:04d}-{month:02d}-{day:02d}",
            is_recurring=is_recurring,
        )
        holiday.font.font_color = font_color
        self.holidays.append(holiday)

    def add_special_day(
        self,
        name: str,
        month: int,
        day: int,
        description: str = "",
        is_recurring: bool = True,
        font_color: str = "#0000FF",
    ) -> None:
        """Add a special day to the calendar."""
        special_day = SpecialDay(
            name=name,
            date_value=f"{self.year:04d}-{month:02d}-{day:02d}",
            description=description,
            is_recurring=is_recurring,
        )
        special_day.font.font_color = font_color
        self.special_days.append(special_day)

    def _is_holiday(self, month: int, day: int) -> Optional[Holiday]:
        """Check if a date is a holiday."""
        for holiday in self.holidays:
            if holiday.date.month == month and holiday.date.day == day:
                return holiday
        return None

    def _is_special_day(self, month: int, day: int) -> Optional[SpecialDay]:
        """Check if a date is a special day."""
        for special_day in self.special_days:
            if special_day.date.month == month and special_day.date.day == day:
                return special_day
        return None

    def _is_weekend(self, weekday: int) -> bool:
        """Check if a weekday is a weekend."""
        return weekday in self.config.weekend_days

    def _create_day(
        self,
        day_number: int,
        is_current_month: bool = True,
        is_weekend: bool = False,
        holiday: Optional[Holiday] = None,
        special_day: Optional[SpecialDay] = None,
    ) -> Day:
        """Create a day with settings from config."""
        day = Day(
            day_number=day_number,
            is_current_month=is_current_month,
            position=Position(0, 0),
            size=Size(self.config.day_width, self.config.day_height),
            font=Font(
                font_type=self.config.month_font_type,
                font_size=self.config.day_font_size,
                font_color=self.config.day_font_color,
                align=self.config.day_number_align,
            ),
            background=Background(
                background_color=self.config.day_background_color,
                background_image=self.config.day_background_image,
            ),
            border=Border(
                border_color=self.config.day_border_color,
                border_width=self.config.day_border_width,
                border_style=self.config.day_border_style,
            ),
        )
        
        # Apply weekend styling
        if is_weekend and self.config.highlight_weekends:
            day.background.background_color = self.config.weekend_background_color
            day.font.font_color = self.config.weekend_font_color
            day.is_weekend = True
        
        # Apply holiday styling
        if holiday:
            day.is_holiday = True
            day.holiday_name = holiday.name
            day.font.font_color = holiday.font.font_color
        
        # Apply special day styling
        if special_day:
            day.is_holiday = True
            day.holiday_name = special_day.name
            day.font.font_color = special_day.font.font_color
            day.border.border_style = "dashed"
            day.border.border_color = special_day.border.border_color
        
        return day

    def _create_weekday_header(self, index: int, short_name: str) -> WeekDay:
        """Create a weekday header with settings from config."""
        is_weekend = index in self.config.weekend_days
        
        weekday = WeekDay(
            name=self.WEEKDAY_NAMES[index],
            short_name=short_name,
            position=Position(0, 0),
            size=Size(self.config.day_width, self.config.weekday_header_height),
            font=Font(
                font_type=self.config.month_font_type,
                font_size=self.config.weekday_font_size,
                font_color=self.config.weekday_font_color if is_weekend else self.config.weekday_font_color,
                align="center",
            ),
            background=Background(
                background_color=self.config.weekday_background_color,
            ),
            border=Border(),
            is_weekend=is_weekend,
        )
        
        if is_weekend and self.config.highlight_weekends:
            weekday.background.background_color = self.config.weekend_background_color
            weekday.font.font_color = self.config.weekend_font_color
        
        return weekday

    def build_month(self, month_number: int) -> Month:
        """Build a month with all its weeks and days."""
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = month_names[month_number - 1]
        
        month = Month(
            name=month_name,
            number=month_number,
            year=self.year,
            position=Position(0, 0),
            size=Size(self.config.canvas.width, self.config.canvas.height),
            font=Font(
                font_type=self.config.month_font_type,
                font_size=self.config.month_font_size,
                font_color=self.config.month_font_color,
            ),
            background=Background(
                background_color=self.config.month_background_color,
                background_image=self.config.month_background_image,
            ),
            border=Border(
                border_color=self.config.month_border_color,
                border_width=self.config.month_border_width,
            ),
            title_font=Font(
                font_type=self.config.month_font_type,
                font_size=self.config.month_title_font_size,
                font_color=self.config.month_title_font_color,
                align="center",
            ),
            weekday_header_height=self.config.weekday_header_height,
        )
        
        # Create weekday headers
        for i, short_name in enumerate(self.config.weekday_names):
            weekday = self._create_weekday_header(i, short_name)
            month.add_weekday(weekday)
        
        # Get number of days in month
        first_weekday, days_in_month = calendar_monthrange(self.year, month_number)
        
        # Adjust for Monday start (Python uses Monday=0)
        first_weekday = (first_weekday) % 7
        
        # Create weeks
        week = Week()
        week_number = 1
        
        # Add empty days for days before the first of the month
        for _ in range(first_weekday):
            prev_month_day = self._create_day(
                day_number=1,
                is_current_month=False,
            )
            prev_month_day.background.background_color = "#F5F5F5"
            prev_month_day.font.font_color = "#999999"
            week.add_day(prev_month_day)
        
        # Add actual days
        for day_num in range(1, days_in_month + 1):
            # Calculate weekday (0=Monday, 6=Sunday)
            current_weekday = (first_weekday + day_num - 1) % 7
            
            is_weekend = self._is_weekend(current_weekday)
            holiday = self._is_holiday(month_number, day_num)
            special = self._is_special_day(month_number, day_num)
            
            day = self._create_day(
                day_number=day_num,
                is_current_month=True,
                is_weekend=is_weekend,
                holiday=holiday,
                special_day=special,
            )
            
            week.add_day(day)
            
            # Start new week after Sunday
            if current_weekday == 6:
                week.week_number = week_number
                month.add_week(week)
                week_number += 1
                week = Week()
        
        # Add remaining days from next month to complete the last week
        if week.days:
            remaining_days = 7 - len(week.days)
            for i in range(1, remaining_days + 1):
                next_month_day = self._create_day(
                    day_number=i,
                    is_current_month=False,
                )
                next_month_day.background.background_color = "#F5F5F5"
                next_month_day.font.font_color = "#999999"
                week.add_day(next_month_day)
            week.week_number = week_number
            month.add_week(week)
        
        return month

    def build_all_months(self) -> List[Month]:
        """Build all 12 months."""
        self.months = []
        for month_num in range(1, 13):
            month = self.build_month(month_num)
            self.months.append(month)
        return self.months

    def add_default_holidays(self) -> None:
        """Add common Russian holidays."""
        # New Year holidays
        self.add_holiday("New Year", 1, 1, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 2, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 3, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 4, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 5, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 6, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 7, font_color="#FF0000")
        self.add_holiday("New Year Holiday", 1, 8, font_color="#FF0000")
        
        # Other holidays
        self.add_holiday("Defender of the Fatherland Day", 2, 23, font_color="#FF0000")
        self.add_holiday("International Women's Day", 3, 8, font_color="#FF0000")
        self.add_holiday("Spring and Labor Day", 5, 1, font_color="#FF0000")
        self.add_holiday("Victory Day", 5, 9, font_color="#FF0000")
        self.add_holiday("Russia Day", 6, 12, font_color="#FF0000")
        self.add_holiday("Unity Day", 11, 4, font_color="#FF0000")

    def get_calendar_data(self) -> dict:
        """Get all calendar data as a dictionary."""
        return {
            "year": self.year,
            "months": self.months,
            "holidays": self.holidays,
            "special_days": self.special_days,
            "config": self.config.to_dict(),
        }
