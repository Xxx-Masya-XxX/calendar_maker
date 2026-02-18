from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer
from models import Month


class SinglePageRenderer(BaseRenderer):
    """Renderer for single-page calendar (all 12 months on one page)."""
    
    def render(self) -> list[Image.Image]:
        """Render all 12 months on a single page."""
        # Create canvas
        canvas = Image.new(
            "RGB",
            (self.config.canvas.width, self.config.canvas.height),
            color=self._hex_to_rgb(self.config.canvas.background_color)
        )
        draw = ImageDraw.Draw(canvas)
        
        if not self.months:
            return [canvas]
        
        # Calculate layout
        cols = self.config.layout.single_page_columns
        rows = self.config.layout.single_page_rows
        
        # Calculate cell sizes
        margin_x = self.config.layout.single_page_margin_x
        margin_y = self.config.layout.single_page_margin_y
        spacing_x = self.config.layout.single_page_spacing_x
        spacing_y = self.config.layout.single_page_spacing_y
        
        cell_width = (self.config.canvas.width - 2 * margin_x - (cols - 1) * spacing_x) // cols
        cell_height = (self.config.canvas.height - 2 * margin_y - (rows - 1) * spacing_y) // rows
        
        # Render each month
        for idx, month in enumerate(self.months):
            row = idx // cols
            col = idx % cols
            
            x = margin_x + col * (cell_width + spacing_x)
            y = margin_y + row * (cell_height + spacing_y)
            
            self._render_month_on_canvas(draw, month, x, y, cell_width, cell_height)
        
        return [canvas]
    
    def _render_month_on_canvas(
        self,
        draw: ImageDraw.ImageDraw,
        month: Month,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Render a single month on the canvas."""
        # Header height
        header_height = self.config.weekday_header_height + 60
        
        # Draw month header
        self._draw_month_header(
            draw,
            month,
            x,
            y,
            width,
            header_height,
        )
        
        # Calculate grid for weeks and days
        content_y = y + header_height
        content_height = height - header_height
        
        weeks_count = len(month.weeks)
        if weeks_count == 0:
            return
        
        week_height = content_height // weeks_count
        day_width = width // 7
        
        # Draw weekday headers
        for i, weekday in enumerate(month.weekdays):
            weekday.position.x = x + i * day_width
            weekday.position.y = content_y
            weekday.size.width = day_width
            weekday.size.height = self.config.weekday_header_height
            self._draw_weekday_header(draw, weekday)
        
        # Draw weeks
        for week_idx, week in enumerate(month.weeks):
            week_y = content_y + self.config.weekday_header_height + week_idx * week_height
            
            # Draw 7 days per week
            for day_idx, day in enumerate(week.days):
                day.position.x = x + day_idx * day_width
                day.position.y = week_y
                # Use configured day size or calculate from grid
                day.size.width = day_width
                day.size.height = week_height
                self._draw_day(draw, day)
