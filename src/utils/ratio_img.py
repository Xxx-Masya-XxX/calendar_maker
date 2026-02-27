from PIL import Image
import sys
import math


def get_aspect_ratio(width, height):
    gcd = math.gcd(width, height)
    return width // gcd, height // gcd


def main(image_path):
    with Image.open(image_path) as img:
        width, height = img.size

    ratio_w, ratio_h = get_aspect_ratio(width, height)

    print(f"Разрешение: {width} x {height}")
    print(f"Соотношение сторон: {ratio_w}:{ratio_h}")
    print(f"В виде дроби: {width/height:.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py image.jpg")
    else:
        main(sys.argv[1])