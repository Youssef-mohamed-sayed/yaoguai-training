"""Decryption functions for each supported algorithm. Ciphertext inputs are
base64 strings (matching what encryption.py produces)."""
import base64

from stream_core import xor_crypt_bytes, rc4_crypt_bytes
from des_core import des_decrypt_bytes
from aes_core import aes_decrypt_bytes
from rsa_core import rsa_decrypt_int, int_to_text
from encryption import _normalize_key


def _unb64(data: str) -> bytes:
    return base64.b64decode(data)


def xor_decrypt(data_b64: str, key: str) -> str:
    raw = xor_crypt_bytes(_unb64(data_b64), key.encode("utf-8"))
    return raw.decode("utf-8", errors="replace")


def rc4_decrypt(data_b64: str, key: str) -> str:
    raw = rc4_crypt_bytes(_unb64(data_b64), key.encode("utf-8"))
    return raw.decode("utf-8", errors="replace")


def des_decrypt(data_b64: str, key: str) -> str:
    key8 = _normalize_key(key, 8)
    raw = des_decrypt_bytes(_unb64(data_b64), key8)
    return raw.decode("utf-8", errors="replace")


def triple_des_decrypt(data_b64: str, key1: str, key2: str, key3: str = None) -> str:
    """Reverse of EDE3: decrypt with key3, encrypt with key2, decrypt with key1."""
    import des_core as d
    k1 = _normalize_key(key1, 8)
    k2 = _normalize_key(key2, 8)
    k3 = _normalize_key(key3 if key3 else key1, 8)
    data = _unb64(data_b64)

    subkeys3 = d.generate_subkeys(d._bytes_to_bits(k3))
    step1 = bytearray()
    for i in range(0, len(data), 8):
        block = d._bytes_to_bits(data[i:i + 8])
        step1 += d._bits_to_bytes(d._des_block(block, subkeys3, decrypt=True))

    subkeys2 = d.generate_subkeys(d._bytes_to_bits(k2))
    step2 = bytearray()
    for i in range(0, len(step1), 8):
        block = d._bytes_to_bits(bytes(step1[i:i + 8]))
        step2 += d._bits_to_bytes(d._des_block(block, subkeys2, decrypt=False))

    # final step unpads (this corresponds to the first encryption with k1)
    subkeys1 = d.generate_subkeys(d._bytes_to_bits(k1))
    step3 = bytearray()
    for i in range(0, len(step2), 8):
        block = d._bytes_to_bits(bytes(step2[i:i + 8]))
        step3 += d._bits_to_bytes(d._des_block(block, subkeys1, decrypt=True))
    pad_len = step3[-1]
    if 1 <= pad_len <= 8:
        step3 = step3[:-pad_len]
    return bytes(step3).decode("utf-8", errors="replace")


def aes_decrypt(data_b64: str, key: str) -> str:
    key16 = _normalize_key(key, 16)
    raw = aes_decrypt_bytes(_unb64(data_b64), key16)
    return raw.decode("utf-8", errors="replace")


def rsa_decrypt(cipher_int_str: str, d_key: int, n: int) -> str:
    c = int(cipher_int_str)
    m = rsa_decrypt_int(c, d_key, n)
    return int_to_text(m)
