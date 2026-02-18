from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer
from models import Month


class MultiPageNotesRenderer(BaseRenderer):
    """Renderer for multi-page calendar with notes area (one month per page with notes section)."""
    
    def render(self) -> list[Image.Image]:
        """Render each month on a separate page with notes area."""
        images = []
        
        if not self.months:
            # Return blank page if no months
            canvas = Image.new(
                "RGB",
                (self.config.canvas.width, self.config.canvas.height),
                color=self._hex_to_rgb(self.config.canvas.background_color)
            )
            return [canvas]
        
        for month in self.months:
            canvas = Image.new(
                "RGB",
                (self.config.canvas.width, self.config.canvas.height),
                color=self._hex_to_rgb(self.config.canvas.background_color)
            )
            draw = ImageDraw.Draw(canvas)
            
            self._render_month_with_notes(draw, month)
            images.append(canvas)
        
        return images
    
    def _render_month_with_notes(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
    ) -> None:
        """Render a single month with notes area on a full page."""
        # Margins
        margin_x = self.config.layout.multi_page_margin_x
        margin_y = self.config.layout.multi_page_margin_y
        
        # Header area
        header_height = 150
        
        # Draw month header
        self._draw_month_header(
            draw,
            month,
            margin_x,
            margin_y,
            self.config.canvas.width - 2 * margin_x,
            header_height,
        )
        
        # Calendar area (top portion of remaining space)
        content_y = margin_y + header_height
        available_height = self.config.canvas.height - content_y - margin_y
        calendar_height = int(available_height * (1 - self.config.layout.notes_area_ratio))
        
        # Notes area (bottom portion)
        notes_height = int(available_height * self.config.layout.notes_area_ratio)
        notes_y = content_y + calendar_height + 30
        
        # Draw calendar grid
        self._draw_calendar_grid(
            draw,
            month,
            margin_x,
            content_y,
            self.config.canvas.width - 2 * margin_x,
            calendar_height,
        )
        
        # Draw notes section
        self._draw_notes_section(
            draw,
            month,
            margin_x,
            notes_y,
            self.config.canvas.width - 2 * margin_x,
            notes_height,
        )
    
    def _draw_calendar_grid(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Draw the calendar grid."""
        weeks_count = len(month.weeks)
        if weeks_count == 0:
            return
        
        week_height = height // weeks_count
        day_width = width // 7
        
        # Draw weekday headers
        for i, weekday in enumerate(month.weekdays):
            weekday.position.x = x + i * day_width
            weekday.position.y = y
            weekday.size.width = day_width
            weekday.size.height = self.config.weekday_header_height
            self._draw_weekday_header(draw, weekday)
        
        # Draw weeks
        for week_idx, week in enumerate(month.weeks):
            week_y = y + self.config.weekday_header_height + week_idx * week_height
            
            # Draw 7 days per week
            for day_idx, day in enumerate(week.days):
                day.position.x = x + day_idx * day_width
                day.position.y = week_y
                day.size.width = day_width
                day.size.height = week_height
                self._draw_day(draw, day)
    
    def _draw_notes_section(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Draw the notes section."""
        # Draw background
        self._draw_rectangle(
            draw,
            x,
            y,
            width,
            height,
            month.background,
            month.border,
        )
        
        # Draw title
        from models.day import Font
        title_font = Font(
            font_type=self.config.month_font_type,
            font_size=self.config.notes_font_size,
            font_color=self.config.month_font_color,
        )
        self._draw_text(
            draw,
            self.config.notes_title,
            x + 20,
            y + 20,
            title_font,
        )
        
        # Draw lined paper effect
        line_color = self._hex_to_rgb(self.config.notes_line_color)
        lines_start_y = y + 80
        
        for i in range((height - 80) // self.config.layout.notes_line_spacing):
            line_y = lines_start_y + i * self.config.layout.notes_line_spacing
            draw.line(
                [(x + 20, line_y), (x + width - 20, line_y)],
                fill=line_color,
                width=2,
            )
