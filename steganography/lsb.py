import numpy as np
from PIL import Image
import os
import random

def embed(image_path, output_path, data: bytes, seed: int):
    img = Image.open(image_path)
    img = img.convert('RGBA')
    pixels = np.array(img)

    prng = random.Random(seed)
    flat_pixels = pixels.reshape(-1, 4)

    required_bits = len(data) * 8
    if required_bits + 64 > flat_pixels.shape[0]:
        raise ValueError("Image too small to embed data.")

    indices = list(range(flat_pixels.shape[0]))
    prng.shuffle(indices)

    for i in range(64):
        bit = (len(data) >> (63 - i)) & 0x1
        flat_pixels[indices[i], 0] = (flat_pixels[indices[i], 0] & ~1) | bit

    for i, byte in enumerate(data):
        for bit in range(8):
            idx = indices[64 + i * 8 + bit]
            flat_pixels[idx, 0] = (flat_pixels[idx, 0] & ~1) | ((byte >> (7 - bit)) & 0x1)

    new_img = Image.fromarray(flat_pixels.reshape(pixels.shape), 'RGBA')
    new_img.save(output_path)
    print(f"Data hidden in '{output_path}'.")

def extract(image_path, seed: int, data_length: int):
    img = Image.open(image_path).convert('RGBA')
    pixels = np.array(img).reshape(-1, 4)

    prng = random.Random(seed)
    indices = list(range(pixels.shape[0]))
    prng.shuffle(indices)

    extracted = bytearray()
    for i in range(data_length):
        byte = 0
        for bit in range(8):
            idx = indices[64 + i * 8 + bit]
            byte = (byte << 1) | (pixels[idx, 0] & 0x1)
        extracted.append(byte)
    return bytes(extracted)
