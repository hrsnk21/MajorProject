from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_public_key(path):
    with open(path, 'rb') as f:
        return serialization.load_pem_public_key(f.read())

def load_private_key(path, passphrase):
    with open(path, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=passphrase.encode())

def encrypt_session_key(session_key, public_key):
    return public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_session_key(encrypted_session_key, private_key):
    return private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
