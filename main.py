import argparse, os
from getpass import getpass
from encryption import rsa, aes
from utils import compression, seed
from steganography import lsb
from PIL import Image
import numpy as np
import math

def calculate_mse(image1_path, image2_path):
    """
    Calculate Mean Squared Error (MSE) between two images.
    """
    img1 = np.array(Image.open(image1_path))
    img2 = np.array(Image.open(image2_path))

    if img1.shape != img2.shape:
        raise ValueError("Images must have the same dimensions for MSE calculation.")

    mse = np.mean((img1 - img2) ** 2)
    return mse

def calculate_psnr(image1_path, image2_path):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two images.
    """
    mse = calculate_mse(image1_path, image2_path)
    if mse == 0:
        return float('inf')  # PSNR is infinite if MSE is zero (images are identical)

    max_pixel_value = 255.0  # Assuming 8-bit images
    psnr = 20 * math.log10(max_pixel_value / math.sqrt(mse))
    return psnr

def hide_file(host, secret, pubkey_path, output):
    public_key = rsa.load_public_key(pubkey_path)
    session_key = os.urandom(32)

    with open(secret, 'rb') as f:
        data = f.read()
    compressed = compression.compress(data)
    encrypted, salt, iv = aes.encrypt(compressed, session_key)
    encrypted_session_key = rsa.encrypt_session_key(session_key, public_key)

    filename = os.path.basename(secret).encode()
    content = (len(filename).to_bytes(4, 'big') + filename + encrypted_session_key + salt + iv + encrypted)
    s = seed.compute_seed_from_image_dimensions(host)
    lsb.embed(host, output, content, s)

    # Evaluate the quality of the stego image
    mse = calculate_mse(host, output)
    psnr = calculate_psnr(host, output)
    print(f"MSE: {mse}")
    print(f"PSNR: {psnr} dB")

def extract_file(carrier, privkey_path, output=None):
    passphrase = getpass("Enter private key passphrase: ")
    private_key = rsa.load_private_key(privkey_path, passphrase)

    s = seed.compute_seed_from_image_dimensions(carrier)
    img = Image.open(carrier)
    pixel_count = np.array(img).size // 4
    data_length = pixel_count // 8 - 64
    data = lsb.extract(carrier, s, data_length)

    filename_len = int.from_bytes(data[:4], 'big')
    filename = data[4:4+filename_len].decode()
    offset = 4 + filename_len
    key_size = private_key.key_size // 8
    esk = data[offset:offset+key_size]
    salt = data[offset+key_size:offset+key_size+16]
    iv = data[offset+key_size+16:offset+key_size+32]
    enc_data = data[offset+key_size+32:]
    session_key = rsa.decrypt_session_key(esk, private_key)
    dec = aes.decrypt(enc_data, session_key, salt, iv)
    decompressed = compression.decompress(dec)

    final_path = output or filename
    with open(final_path, 'wb') as f:
        f.write(decompressed)
    print(f"Extracted to '{final_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    hide = sub.add_parser("hide")
    hide.add_argument("host")
    hide.add_argument("secret")
    hide.add_argument("pubkey")
    hide.add_argument("output")

    extract = sub.add_parser("extract")
    extract.add_argument("carrier")
    extract.add_argument("privkey")
    extract.add_argument("output", nargs='?', default=None)

    args = parser.parse_args()
    if args.cmd == "hide":
        hide_file(args.host, args.secret, args.pubkey, args.output)
    elif args.cmd == "extract":
        extract_file(args.carrier, args.privkey, args.output)
    else:
        parser.print_help()