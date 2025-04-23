from PIL import Image

def compute_seed_from_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width + height
