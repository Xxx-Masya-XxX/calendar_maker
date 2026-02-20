"""Preview generation thread."""

import json
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, QPixmap

from src.calendar_generator import CalendarGenerator
from src.utils.image_utils import ImageUtils


class PreviewThread(QThread):
    """Thread for preview generation."""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, config: dict, year: int, month: int = 1):
        super().__init__()
        self.config = config
        self.year = year
        self.month = month
        self.finished.connect(self.quit)
        self.error.connect(self.quit)

    def run(self):
        try:
            # Save config to temp file
            temp_path = Path('temp_config.json')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            # Generate preview
            generator = CalendarGenerator(str(temp_path))
            month_img = generator.create_month(self.year, self.month)

            # Convert to QImage
            rgb_data, width, height, bytes_per_line = ImageUtils.cv2_to_qimage(month_img)

            qimage = QImage(rgb_data, width, height, bytes_per_line, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)

            self.finished.emit(pixmap)

            # Remove temp file
            temp_path.unlink(missing_ok=True)

        except Exception as e:
            self.error.emit(str(e))
