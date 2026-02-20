from PIL import Image

def create_collages(template_path, cropped_images, output_dir, green_color=(0, 255, 0)):
    """
    template_path: путь к template.png
    cropped_images: список путей к кропнутым изображениям
    output_dir: папка для готовых коллажей
    green_color: цвет области для вставки (R,G,B)
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    # открываем шаблон
    template = Image.open(template_path).convert("RGBA")
    template_data = template.load()
    width, height = template.size

    # находим bounding box зеленой области
    min_x, min_y = width, height
    max_x, max_y = 0, 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = template_data[x, y]
            if (r, g, b) == green_color:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if min_x >= max_x or min_y >= max_y:
        raise ValueError("Не удалось найти зеленую область в шаблоне")

    green_box = (min_x, min_y, max_x+1, max_y+1)
    box_w = max_x - min_x + 1
    box_h = max_y - min_y + 1

    print(f"Найдена зеленая область: {green_box}, размер: {box_w}x{box_h}")

    # создаем коллажи
    for idx, img_path in enumerate(cropped_images):
        collage = template.copy()
        img = Image.open(img_path).convert("RGBA")

        # растягиваем кропнутое изображение на зеленую область
        img_resized = img.resize((box_w, box_h), Image.Resampling.LANCZOS)

        # вставляем на шаблон
        collage.paste(img_resized, (min_x, min_y), img_resized)

        # сохраняем результат
        out_path = os.path.join(output_dir, f"collage_{idx+1}.png")
        collage.save(out_path)
        print(f"Создан коллаж: {out_path}")

    print("Все коллажи созданы ✅")
template_path = r'C:\Masya\Projects\calendar_maker\wb\template.png'
output_dir = r"C:\Users\Чумба\Downloads\19-02-2026_17-34-34\cropped\w"
import os

cropped_folder = r"C:\Users\Чумба\Downloads\19-02-2026_17-34-34\cropped"
cropped_images = [
    os.path.join(cropped_folder, f)
    for f in os.listdir(cropped_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg"))
]
create_collages(template_path, cropped_images, output_dir, green_color=(0, 255, 0))