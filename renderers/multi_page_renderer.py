from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer
from models import Month


class MultiPageRenderer(BaseRenderer):
    """Renderer for multi-page calendar (one month per page)."""
    
    def render(self) -> list[Image.Image]:
        """Render each month on a separate page."""
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
            
            self._render_month_full_page(draw, month)
            images.append(canvas)
        
        return images
    
    def _render_month_full_page(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
    ) -> None:
        """Render a single month on a full page."""
        # Margins
        margin_x = self.config.layout.multi_page_margin_x
        margin_y = self.config.layout.multi_page_margin_y
        
        # Header area
        header_height = self.config.layout.multi_page_header_height
        
        # Draw month header
        self._draw_month_header(
            draw,
            month,
            margin_x,
            margin_y,
            self.config.canvas.width - 2 * margin_x,
            header_height,
        )
        
        # Content area for weeks
        content_y = margin_y + header_height
        content_height = self.config.canvas.height - content_y - margin_y
        
        weeks_count = len(month.weeks)
        if weeks_count == 0:
            return
        
        week_height = content_height // weeks_count
        day_width = (self.config.canvas.width - 2 * margin_x) // 7
        
        # Draw weekday headers
        for i, weekday in enumerate(month.weekdays):
            weekday.position.x = margin_x + i * day_width
            weekday.position.y = content_y
            weekday.size.width = day_width
            weekday.size.height = self.config.weekday_header_height
            self._draw_weekday_header(draw, weekday)
        
        # Draw weeks
        for week_idx, week in enumerate(month.weeks):
            week_y = content_y + self.config.weekday_header_height + week_idx * week_height
            
            # Draw 7 days per week
            for day_idx, day in enumerate(week.days):
                day.position.x = margin_x + day_idx * day_width
                day.position.y = week_y
                day.size.width = day_width
                day.size.height = week_height
                self._draw_day(draw, day)
