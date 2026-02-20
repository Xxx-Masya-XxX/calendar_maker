# Руководство по Pillow (PIL)

**Pillow** — это библиотека для работы с графикой в Python. Она позволяет создавать изображения, рисовать фигуры, добавлять текст и выполнять другие операции.

## Установка

```bash
pip install Pillow
```

## Импорт

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter
```

---

## 1. Создание изображений

### Создание пустого изображения

```python
from PIL import Image

# Создать изображение 400x300 пикселей, цвет - белый
img = Image.new('RGB', (400, 300), color='white')
img.save('output.png')

# Другие способы указания цвета
img = Image.new('RGB', (400, 300), color=(255, 255, 255))  # RGB кортеж
img = Image.new('RGB', (400, 300), color='#FFFFFF')         # HEX
img = Image.new('RGBA', (400, 300), color=(0, 0, 0, 0))     # С прозрачностью
```

### Режимы изображений

- `'RGB'` — обычный цветной (красный, зелёный, синий)
- `'RGBA'` — цветной с прозрачностью (альфа-канал)
- `'L'` — чёрно-белый (grayscale)
- `'1'` — чёрно-белый (1 бит)

---

## 2. Загрузка и сохранение изображений

### Открытие изображения из файла

```python
from PIL import Image

# Открыть изображение
img = Image.open('assets/img/test.jpg')

# Получить информацию
print(f"Размер: {img.size}")      # (ширина, высота)
print(f"Режим: {img.mode}")       # 'RGB', 'RGBA' и т.д.
print(f"Формат: {img.format}")    # 'JPEG', 'PNG' и т.д.

# Конвертировать режим
img_rgb = img.convert('RGB')
img_rgba = img.convert('RGBA')
```

### Сохранение изображения

```python
# Сохранить в файл
img.save('output.png')

# Сохранить с параметрами (для JPEG)
img.save('output.jpg', quality=95, optimize=True)

# Сохранить в другом формате
img.save('output.pdf')
```

---

## 3. Рисование фигур

### Инициализация рисовальщика

```python
from PIL import Image, ImageDraw

# Создать изображение
img = Image.new('RGB', (500, 400), color='white')

# Создать объект для рисования
draw = ImageDraw.Draw(img)
```

### Рисование линий

```python
# draw.line(xy, fill, width)
draw.line([(50, 50), (200, 50)], fill='black', width=2)
draw.line([(50, 60), (200, 60)], fill='red', width=5)

# Несколько линий подряд
draw.line([(50, 50), (100, 100), (150, 50)], fill='blue', width=3)
```

### Рисование прямоугольников

```python
# draw.rectangle(xy, fill, outline, width)
# xy = [(x1, y1), (x2, y2)] - верхний левый и нижний правый углы

# Закрашенный прямоугольник
draw.rectangle([(50, 100), (200, 180)], fill='lightblue')

# Только контур
draw.rectangle([(220, 100), (370, 180)], outline='green', width=3)

# И заливка, и контур
draw.rectangle([(50, 200), (200, 280)], fill='yellow', outline='black', width=2)
```

### Рисование эллипсов и кругов

```python
# draw.ellipse(xy, fill, outline, width)
# Эллипс вписывается в прямоугольник xy

# Эллипс
draw.ellipse([(50, 300), (200, 380)], fill='pink', outline='purple', width=2)

# Круг (когда прямоугольник - квадрат)
draw.ellipse([(220, 300), (300, 380)], fill='orange')
```

### Рисование многоугольников

```python
# draw.polygon(xy, fill, outline)
# xy - список вершин [(x1, y1), (x2, y2), ...]

# Треугольник
points = [(350, 50), (450, 150), (250, 150)]
draw.polygon(points, fill='lightgreen', outline='darkgreen')

# Пятиугольник
import math
cx, cy, r = 400, 300, 50
points = [(cx + r * math.cos(2 * math.pi * i / 5), 
           cy + r * math.sin(2 * math.pi * i / 5)) for i in range(5)]
draw.polygon(points, fill='gold', outline='black')
```

### Рисование дуг и секторов

```python
# draw.arc(xy, start, end, fill, width)
# start и end - углы в градусах (0° = вправо, по часовой стрелке)

draw.arc([(50, 50), (150, 150)], 0, 90, fill='red', width=3)
draw.arc([(160, 50), (260, 150)], 90, 180, fill='green', width=3)
draw.arc([(270, 50), (370, 150)], 180, 270, fill='blue', width=3)

# draw.chord() - дуга с соединяющей линией (как сектор)
draw.chord([(50, 170), (150, 270)], 0, 90, fill='lightblue', outline='blue')

# draw.pieslice() - сектор круга
draw.pieslice([(160, 170), (260, 270)], 0, 180, fill='lightyellow', outline='orange')
```

---

## 4. Работа с текстом

### Подключение шрифтов

```python
from PIL import ImageFont

# Загрузить шрифт (укажите путь к .ttf файлу)
font = ImageFont.truetype("arial.ttf", 24)        # Размер 24
font_small = ImageFont.truetype("arial.ttf", 14)
font_bold = ImageFont.truetype("timesbd.ttf", 32) # Жирный Times New Roman

# Шрифт по умолчанию
default_font = ImageFont.load_default()
```

### Рисование текста

```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (500, 300), color='white')
draw = ImageDraw.Draw(img)

# Загрузить шрифт
font = ImageFont.truetype("arial.ttf", 28)

# draw.text(xy, text, fill, font, anchor)
draw.text((50, 50), "Привет, мир!", fill='black', font=font)

# Текст с другим цветом
draw.text((50, 100), "Красный текст", fill='red', font=font)

# Выравнивание текста (anchor)
# anchor='lm' - left middle, 'mm' - middle middle, 'rm' - right middle
draw.text((250, 150), "По центру", fill='blue', font=font, anchor='mm')

# Крупный заголовок
font_large = ImageFont.truetype("arial.ttf", 48)
draw.text((250, 220), "Заголовок", fill='darkgreen', font=font_large, anchor='mm')

img.save('text_example.png')
```

### Получение размеров текста

```python
font = ImageFont.truetype("arial.ttf", 24)
text = "Пример текста"

# Получить bounding box текста
bbox = draw.textbbox((0, 0), text, font=font)
width = bbox[2] - bbox[0]
height = bbox[3] - bbox[1]

print(f"Ширина: {width}, Высота: {height}")

# Центрировать текст
img_width, img_height = 500, 300
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (img_width - text_width) // 2
y = (img_height - text_height) // 2

draw.text((x, y), text, fill='black', font=font)
```

---

## 5. Рисование точек и фигур с антиалиасингом

### Точки

```python
# draw.point(xy, fill)
draw.point((100, 100), fill='red')
draw.point((101, 100), fill='red')
draw.point((102, 100), fill='red')

# Несколько точек
points = [(150, 150), (151, 151), (152, 152)]
draw.point(points, fill='blue')
```

---

## 6. Полные примеры

### Пример 1: Создание простой открытки

```python
from PIL import Image, ImageDraw, ImageFont

# Создать изображение
img = Image.new('RGB', (600, 400), color='#87CEEB')  # Небесно-голубой
draw = ImageDraw.Draw(img)

# Солнце
draw.ellipse([(50, 50), (150, 150)], fill='#FFD700', outline='#FFA500', width=3)

# Земля (зелёная полоса внизу)
draw.rectangle([(0, 300), (600, 400)], fill='#228B22')

# Домик
draw.rectangle([(250, 200), (350, 300)], fill='#DEB887', outline='#8B4513', width=2)
draw.polygon([(240, 200), (300, 150), (360, 200)], fill='#8B0000', outline='#654321')

# Окно
draw.rectangle([(280, 220), (320, 260)], fill='#87CEEB', outline='#654321', width=2)

# Текст
font = ImageFont.truetype("arial.ttf", 32)
draw.text((300, 350), "Добро пожаловать!", fill='white', font=font, anchor='mm')

img.save('postcard.png')
img.show()
```

### Пример 2: Создание календарной сетки

```python
from PIL import Image, ImageDraw, ImageFont

def create_calendar_grid(year, month):
    """Создаёт изображение календаря на месяц"""
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Заголовок
    font_header = ImageFont.truetype("arial.ttf", 28)
    font_day = ImageFont.truetype("arial.ttf", 16)
    
    title = f"{month} {year}"
    draw.text((width // 2, 20), title, fill='black', font=font_header, anchor='mm')
    
    # Дни недели
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    cell_width = width // 7
    for i, day in enumerate(days):
        x = i * cell_width + cell_width // 2
        draw.text((x, 60), day, fill='darkblue', font=font_day, anchor='mm')
    
    # Сетка
    for i in range(8):  # Горизонтальные линии
        y = 80 + i * 30
        draw.line([(0, y), (width, y)], fill='gray', width=1)
    
    for i in range(8):  # Вертикальные линии
        x = i * cell_width
        draw.line([(x, 80), (x, height)], fill='gray', width=1)
    
    # Числа (пример - просто 1-31)
    font_num = ImageFont.truetype("arial.ttf", 18)
    for day in range(1, 32):
        row = (day - 1) // 7
        col = (day - 1) % 7
        x = col * cell_width + cell_width // 2
        y = 110 + row * 30
        draw.text((x, y), str(day), fill='black', font=font_num, anchor='mm')
    
    return img

# Использование
img = create_calendar_grid(2026, "Февраль")
img.save('calendar_feb_2026.png')
img.show()
```

### Пример 3: Обработка изображения и добавление текста

```python
from PIL import Image, ImageDraw, ImageFont

# Открыть изображение
img = Image.open('assets/img/test.jpg')

# Изменить размер
img = img.resize((800, 600), Image.Resampling.LANCZOS)

# Создать объект для рисования
draw = ImageDraw.Draw(img)

# Добавить полупрозрачную подложку для текста
overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([(0, 500), (800, 600)], fill=(0, 0, 0, 128))

# Наложить подложку
img = Image.alpha_composite(img.convert('RGBA'), overlay)

# Добавить текст
font = ImageFont.truetype("arial.ttf", 36)
draw = ImageDraw.Draw(img)
draw.text((400, 530), "Моя красивая картинка", fill='white', font=font, anchor='mm')

img.save('result.png')
img.show()
```

### Пример 4: Рисование градиента

```python
from PIL import Image, ImageDraw

def create_gradient(width, height, color1, color2, vertical=True):
    """Создаёт градиент между двумя цветами"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    for i in range(height if vertical else width):
        if vertical:
            ratio = i / height
        else:
            ratio = i / width
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        if vertical:
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, height)], fill=(r, g, b))
    
    return img

# Использование
gradient = create_gradient(400, 300, (255, 0, 0), (0, 0, 255), vertical=True)
gradient.save('gradient.png')
gradient.show()
```

---

## 7. Фильтры и эффекты

```python
from PIL import Image, ImageFilter

img = Image.open('image.jpg')

# Размытие
blurred = img.filter(ImageFilter.BLUR)

# Размытие по Гауссу
gaussian = img.filter(ImageFilter.GaussianBlur(radius=5))

# Резкость
sharpened = img.filter(ImageFilter.SHARPEN)

# Контур
edges = img.filter(ImageFilter.FIND_EDGES)

# Сохранить
blurred.save('blurred.png')
```

---

## 8. Полезные функции

### Изменение размера и кадрирование

```python
# Изменить размер
img_resized = img.resize((800, 600), Image.Resampling.LANCZOS)

# Кадрировать (crop)
box = (100, 100, 400, 400)  # (left, upper, right, lower)
cropped = img.crop(box)

# Повернуть
rotated = img.rotate(45)  # На 45 градусов

# Отразить
flipped = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
```

### Вставка одного изображения в другое

```python
# Открыть основное изображение и вставку
background = Image.new('RGB', (500, 500), 'white')
logo = Image.open('logo.png').convert('RGBA')

# Изменить размер логотипа
logo = logo.resize((100, 100), Image.Resampling.LANCZOS)

# Вставить (координаты верхнего левого угла)
background.paste(logo, (200, 200), logo)  # logo как маска для прозрачности
background.save('result.png')
```

---

## 9. Справочник основных методов

### ImageDraw

| Метод | Описание |
|-------|----------|
| `draw.line(xy, fill, width)` | Рисует линию |
| `draw.rectangle(xy, fill, outline, width)` | Рисует прямоугольник |
| `draw.ellipse(xy, fill, outline, width)` | Рисует эллипс |
| `draw.polygon(xy, fill, outline)` | Рисует многоугольник |
| `draw.arc(xy, start, end, fill, width)` | Рисует дугу |
| `draw.chord(xy, start, end, fill, outline, width)` | Рисует хорду |
| `draw.pieslice(xy, start, end, fill, outline, width)` | Рисует сектор |
| `draw.text(xy, text, fill, font, anchor)` | Рисует текст |
| `draw.point(xy, fill)` | Рисует точку(и) |
| `draw.textbbox(xy, text, font)` | Возвращает границы текста |

### Image

| Метод | Описание |
|-------|----------|
| `Image.new(mode, size, color)` | Создаёт новое изображение |
| `Image.open(path)` | Открывает изображение из файла |
| `img.save(path, **params)` | Сохраняет изображение |
| `img.convert(mode)` | Конвертирует режим цвета |
| `img.resize(size, resample)` | Изменяет размер |
| `img.crop(box)` | Кадрирует изображение |
| `img.rotate(angle)` | Поворачивает изображение |
| `img.transpose(method)` | Отражает изображение |
| `img.filter(filter)` | Применяет фильтр |

---

## 10. Распространённые цвета

```python
# Названия цветов
colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 128, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'gray': (128, 128, 128),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'brown': (165, 42, 42),
}
```

---

## Ресурсы

- [Официальная документация Pillow](https://pillow.readthedocs.io/)
- [Pillow Handbook](https://pillow.readthedocs.io/en/stable/handbook/index.html)
