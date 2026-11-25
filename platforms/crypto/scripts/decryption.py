"""Decryption functions for each supported algorithm. Ciphertext inputs are
auto-detected: base64 (what encryption.py produces), hex, decimal byte lists,
or raw strings."""
import base64
import re

from stream_core import xor_crypt_bytes, rc4_crypt_bytes
from des_core import des_decrypt_bytes
from aes_core import aes_decrypt_bytes
from rsa_core import rsa_decrypt_int, int_to_text
from encryption import _normalize_key


def _unb64(data: str) -> bytes:
    """Smart ciphertext decoder (the name is historical - not only base64).

    Accepts the ciphertext in any of these representations and returns the
    raw bytes:

    1. decimal - byte values separated by spaces/commas ("221 184 52 ...")
    2. hex     - hex digits, optional spaces and 0x prefixes ("DDB83487...")
    3. base64  - the format encryption.py produces ("3bg0h019...")
    4. string  - anything else is taken as raw UTF-8 text

    Detection runs in that order, so an input matching more than one form is
    read as the earliest match: a pure-digit string of even length is hex,
    and any text that is valid base64 is base64 (never a plain string).
    """
    text = data.strip()

    parts = re.split(r"[\s,;]+", text)
    if len(parts) > 1 and all(p.isdigit() and int(p) <= 255 for p in parts):
        return bytes(int(p) for p in parts)

    squashed = re.sub(r"0[xX]", "", re.sub(r"\s+", "", text))
    if len(squashed) >= 4 and len(squashed) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", squashed):
        return bytes.fromhex(squashed)

    try:
        return base64.b64decode(re.sub(r"\s+", "", text), validate=True)
    except ValueError:
        return data.encode("utf-8")


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
