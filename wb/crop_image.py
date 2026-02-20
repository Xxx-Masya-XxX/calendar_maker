import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QFileDialog, QVBoxLayout, QWidget, QMessageBox
)
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QPoint
from PIL import Image


from PySide6.QtGui import QPolygonF

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.points = []  # x0,y0 и x1,y1
        self.setAlignment(Qt.AlignCenter)
        self.pixmap_original = None
        self.pixmap_scaled = None
        self.scale_factor = 1.0  # масштаб превью

    def set_image(self, image_path, max_width=800, max_height=600):
        self.pixmap_original = QPixmap(image_path)
        ow = self.pixmap_original.width()
        oh = self.pixmap_original.height()

        scale_w = min(1.0, max_width / ow)
        scale_h = min(1.0, max_height / oh)
        self.scale_factor = min(scale_w, scale_h)

        if self.scale_factor < 1.0:
            self.pixmap_scaled = self.pixmap_original.scaled(
                int(ow * self.scale_factor),
                int(oh * self.scale_factor),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        else:
            self.pixmap_scaled = self.pixmap_original

        self.setPixmap(self.pixmap_scaled)
        self.points = []

    def mousePressEvent(self, event):
        if len(self.points) < 2 and self.pixmap_scaled:
            # вычисляем реальные координаты на изображении
            label_w = self.width()
            label_h = self.height()
            pixmap_w = self.pixmap_scaled.width()
            pixmap_h = self.pixmap_scaled.height()

            # смещение для AlignCenter
            self.offset_x = (label_w - pixmap_w) / 2
            self.offset_y = (label_h - pixmap_h) / 2

            # координаты внутри изображения
            x = (event.position().x() - self.offset_x) / self.scale_factor
            y = (event.position().y() - self.offset_y) / self.scale_factor

            # ограничиваем рамками изображения
            x = max(0, min(x, self.pixmap_original.width() - 1))
            y = max(0, min(y, self.pixmap_original.height() - 1))

            self.points.append(QPoint(int(x), int(y)))
            self.update()



    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap_scaled or len(self.points) == 0:
            return

        painter = QPainter(self)
        pen = QPen(Qt.red, 3)
        painter.setPen(pen)

        # рисуем точки
        for p in self.points:
            px = int(p.x() * self.scale_factor)
            py = int(p.y() * self.scale_factor)
            painter.drawEllipse(QPoint(px, py), 5, 5)

        # если есть обе точки, рисуем прямоугольник
        if len(self.points) == 2:
            x0 = int(self.points[0].x() * self.scale_factor + self.offset_x)
            y0 = int(self.points[0].y() * self.scale_factor + self.offset_y)
            x1 = int(self.points[1].x() * self.scale_factor + self.offset_x)
            y1 = int(self.points[1].y() * self.scale_factor + self.offset_y)
            rect_x = min(x0, x1)
            rect_y = min(y0, y1)
            rect_w = abs(x1 - x0)
            rect_h = abs(y1 - y0)
            painter.drawRect(rect_x, rect_y, rect_w, rect_h)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Crop Tool")

        self.image_label = ImageLabel()

        self.btn_load = QPushButton("Загрузить папку")
        self.btn_crop = QPushButton("Обрезать все")

        self.btn_load.clicked.connect(self.load_folder)
        self.btn_crop.clicked.connect(self.crop_all)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_crop)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_paths = []

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if not folder:
            return

        self.image_paths = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not self.image_paths:
            QMessageBox.warning(self, "Ошибка", "Нет изображений в папке")
            return

        self.image_label.set_image(self.image_paths[0], max_width=800, max_height=600)

    def crop_all(self):
        if len(self.image_label.points) != 2:
            QMessageBox.warning(self, "Ошибка", "Выберите 2 точки: верхний левый и нижний правый")
            return

        if not self.image_paths:
            return

        x0, y0 = self.image_label.points[0].x(), self.image_label.points[0].y()
        x1, y1 = self.image_label.points[1].x(), self.image_label.points[1].y()

        min_x, max_x = min(x0, x1), max(x0, x1)
        min_y, max_y = min(y0, y1), max(y0, y1)

        output_dir = os.path.join(os.path.dirname(self.image_paths[0]), "cropped")
        os.makedirs(output_dir, exist_ok=True)

        for path in self.image_paths:
            img = Image.open(path)
            cropped = img.crop((min_x, min_y, max_x, max_y))
            filename = os.path.basename(path)
            cropped.save(os.path.join(output_dir, filename))

        QMessageBox.information(self, "Готово", "Все изображения обрезаны!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())
