from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

import os
import tempfile


class CalendarWidget(QWidget):
    """Widget for calendar preview."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 500)
        self.preview_label.setStyleSheet(
            "QLabel { background-color: #F5F5F5; border: 1px solid #CCC; }"
        )
        self.preview_label.setText("Preview will appear here\nПредпросмотр появится здесь")
        layout.addWidget(self.preview_label)
        
        # Preview button
        self.preview_btn = QPushButton("Generate Preview / Предпросмотр")
        self.preview_btn.clicked.connect(self.on_preview)
        layout.addWidget(self.preview_btn)
        
        self.setLayout(layout)
    
    def on_preview(self):
        """Generate preview from main window settings."""
        # Get parent main window
        main_window = self.parent()
        while main_window and not isinstance(main_window, type(None)):
            main_window = main_window.parent()
            if hasattr(main_window, 'get_config'):
                break
        
        if not hasattr(main_window, 'get_config'):
            QMessageBox.warning(self, "Warning", "Could not find main window settings")
            return
        
        try:
            from config import CalendarConfig
            from calendar_core import CalendarBuilder, CalendarFactory
            
            config = main_window.get_config()
            
            # Build calendar
            builder = CalendarBuilder(config)
            builder.build_all_months()
            
            # Create renderer
            renderer = CalendarFactory.create_renderer(config.calendar_type)
            renderer.set_config(config)
            renderer.set_months(builder.months)
            
            # Render to temp file
            temp_path = os.path.join(tempfile.gettempdir(), "calendar_preview.png")
            renderer.save(temp_path)
            
            # Show preview
            pixmap = QPixmap(temp_path)
            scaled_pixmap = pixmap.scaled(
                400, 565,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setText("")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate preview:\n{e}")
