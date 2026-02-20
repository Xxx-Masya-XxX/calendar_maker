"""
Утилиты для работы с изображениями Pillow
"""

from PIL import Image


def set_opacity(img: Image.Image, opacity: float) -> Image.Image:
    """
    Изменяет прозрачность изображения.
    
    Args:
        img: Объект PIL Image
        opacity: Уровень непрозрачности от 0.0 до 1.0
                 0.0 - полностью прозрачный
                 1.0 - полностью непрозрачный
    
    Returns:
        PIL Image с изменённой прозрачностью
    
    Example:
        >>> img = Image.open('logo.png')
        >>> img_semi = set_opacity(img, 0.5)  # 50% прозрачности
        >>> img_semi.save('result.png')
    """
    # Конвертировать в RGBA для работы с альфа-каналом
    img = img.convert('RGBA')
    
    # Получить альфа-канал
    alpha = img.split()[3]
    
    # Применить коэффициент прозрачности
    alpha = alpha.point(lambda i: i * opacity)
    
    # Обновить альфа-канал
    img.putalpha(alpha)
    
    return img


def set_opacity_region(img: Image.Image, opacity: float, box: tuple = None) -> Image.Image:
    """
    Изменяет прозрачность только в указанной области.
    
    Args:
        img: Объект PIL Image
        opacity: Уровень непрозрачности от 0.0 до 1.0
        box: Область (left, upper, right, lower). Если None - всё изображение
    
    Returns:
        PIL Image с изменённой прозрачностью в области
    """
    img = img.convert('RGBA')
    
    if box is None:
        box = (0, 0, img.width, img.height)
    
    # Вырезать область
    region = img.crop(box)
    
    # Изменить прозрачность области
    alpha = region.split()[3]
    alpha = alpha.point(lambda i: i * opacity)
    region.putalpha(alpha)
    
    # Вставить обратно
    img.paste(region, box)
    
    return img


def fade_opacity(img: Image.Image, direction: str = 'horizontal') -> Image.Image:
    """
    Создаёт градиент прозрачности.
    
    Args:
        img: Объект PIL Image
        direction: Направление градиента ('horizontal', 'vertical', 'left', 'right', 'top', 'bottom')
    
    Returns:
        PIL Image с градиентом прозрачности
    """
    img = img.convert('RGBA')
    width, height = img.size
    pixels = img.load()
    
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            
            if direction in ('horizontal', 'left'):
                factor = x / width
            elif direction == 'right':
                factor = 1 - (x / width)
            elif direction in ('vertical', 'top'):
                factor = y / height
            elif direction == 'bottom':
                factor = 1 - (y / height)
            else:
                factor = x / width
            
            new_alpha = int(a * factor)
            pixels[x, y] = (r, g, b, new_alpha)
    
    return img


def add_opacity_to_rgb(img: Image.Image, opacity: float = 1.0) -> Image.Image:
    """
    Добавляет альфа-канал к RGB изображению с заданной прозрачностью.
    
    Args:
        img: Объект PIL Image (RGB или RGBA)
        opacity: Уровень непрозрачности от 0.0 до 1.0
    
    Returns:
        PIL Image в режиме RGBA с заданной прозрачностью
    """
    img = img.convert('RGBA')
    
    if opacity < 1.0:
        alpha = img.split()[3]
        alpha = alpha.point(lambda i: i * opacity)
        img.putalpha(alpha)
    
    return img


def make_color_transparent(img: Image.Image, color: tuple, threshold: int = 30) -> Image.Image:
    """
    Делает указанный цвет прозрачным.
    
    Args:
        img: Объект PIL Image
        color: Цвет для удаления (RGB кортеж)
        threshold: Порог чувствительности (0-255)
    
    Returns:
        PIL Image с прозрачным фоном
    """
    img = img.convert('RGBA')
    datas = img.getdata()
    new_data = []
    
    for item in datas:
        if (abs(item[0] - color[0]) < threshold and
            abs(item[1] - color[1]) < threshold and
            abs(item[2] - color[2]) < threshold):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    
    img.putdata(new_data)
    return img
