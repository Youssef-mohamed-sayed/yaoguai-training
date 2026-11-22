"""
Encryption functions for each supported algorithm.
Convention: inputs are plain strings (utf-8), keys are strings unless noted.
Outputs are base64-encoded ciphertext so they are safe to put in JSON.
"""
import base64
import os

from stream_core import xor_crypt_bytes, rc4_crypt_bytes
from des_core import des_encrypt_bytes
from aes_core import aes_encrypt_bytes
from rsa_core import rsa_encrypt_int, text_to_int, generate_keypair


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def xor_encrypt(data: str, key: str) -> str:
    return _b64(xor_crypt_bytes(data.encode("utf-8"), key.encode("utf-8")))


def rc4_encrypt(data: str, key: str) -> str:
    return _b64(rc4_crypt_bytes(data.encode("utf-8"), key.encode("utf-8")))


def _normalize_key(key: str, length: int) -> bytes:
    """Educational helper: pad/truncate a utf-8 key to the exact byte length
    DES/AES need (8 bytes for DES, 16 for AES-128)."""
    key_bytes = key.encode("utf-8")
    if len(key_bytes) < length:
        key_bytes = key_bytes.ljust(length, b"\0")
    return key_bytes[:length]


def des_encrypt(data: str, key: str) -> str:
    key8 = _normalize_key(key, 8)
    return _b64(des_encrypt_bytes(data.encode("utf-8"), key8))


def des_encrypt_file_bytes(data: bytes, key: str) -> bytes:
    """Encrypt raw bytes with DES; return raw encrypted bytes. Used by file routes."""
    key8 = _normalize_key(key, 8)
    return des_encrypt_bytes(data, key8)


def des_decrypt_file_bytes(data: bytes, key: str) -> bytes:
    """Decrypt raw DES-encrypted bytes; return raw plaintext bytes. Used by file routes."""
    if not data or len(data) % 8 != 0:
        raise ValueError("Malformed ciphertext: file length must be a non-zero multiple of 8 bytes.")
    from des_core import des_decrypt_bytes as _dec
    key8 = _normalize_key(key, 8)
    return _dec(data, key8)


def aes_encrypt_file_bytes(data: bytes, key: str) -> bytes:
    """Encrypt raw bytes with AES-128; return raw encrypted bytes."""
    key16 = _normalize_key(key, 16)
    return aes_encrypt_bytes(data, key16)


def aes_decrypt_file_bytes(data: bytes, key: str) -> bytes:
    """Decrypt raw AES-128 encrypted bytes; return raw plaintext bytes."""
    if not data or len(data) % 16 != 0:
        raise ValueError("Malformed ciphertext: file length must be a non-zero multiple of 16 bytes for AES.")
    from aes_core import aes_decrypt_bytes as _dec
    key16 = _normalize_key(key, 16)
    return _dec(data, key16)


def triple_des_encrypt_file_bytes(data: bytes, key1: str, key2: str, key3: str = None) -> bytes:
    """Encrypt raw bytes with Triple-DES (EDE3/EDE2)."""
    import des_core as d
    k1 = _normalize_key(key1, 8)
    k2 = _normalize_key(key2, 8)
    k3 = _normalize_key(key3 if key3 else key1, 8)
    step1 = d.des_encrypt_bytes(data, k1)
    subkeys2 = d.generate_subkeys(d._bytes_to_bits(k2))
    step2 = bytearray()
    for i in range(0, len(step1), 8):
        block = d._bytes_to_bits(step1[i:i + 8])
        step2 += d._bits_to_bytes(d._des_block(block, subkeys2, decrypt=True))
    subkeys3 = d.generate_subkeys(d._bytes_to_bits(k3))
    step3 = bytearray()
    for i in range(0, len(step2), 8):
        block = d._bytes_to_bits(bytes(step2[i:i + 8]))
        step3 += d._bits_to_bytes(d._des_block(block, subkeys3, decrypt=False))
    return bytes(step3)


def triple_des_decrypt_file_bytes(data: bytes, key1: str, key2: str, key3: str = None) -> bytes:
    """Decrypt raw bytes with Triple-DES (EDE3/EDE2)."""
    if not data or len(data) % 8 != 0:
        raise ValueError("Malformed ciphertext: file length must be a non-zero multiple of 8 bytes for 3DES.")
    import des_core as d
    k1 = _normalize_key(key1, 8)
    k2 = _normalize_key(key2, 8)
    k3 = _normalize_key(key3 if key3 else key1, 8)
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
    subkeys1 = d.generate_subkeys(d._bytes_to_bits(k1))
    step3 = bytearray()
    for i in range(0, len(step2), 8):
        block = d._bytes_to_bits(bytes(step2[i:i + 8]))
        step3 += d._bits_to_bytes(d._des_block(block, subkeys1, decrypt=True))
    return d._unpad(bytes(step3))


def rc4_file_bytes(data: bytes, key: str) -> bytes:
    """Encrypt/decrypt raw bytes with RC4 stream cipher."""
    return rc4_crypt_bytes(data, key.encode("utf-8"))


def xor_file_bytes(data: bytes, key: str) -> bytes:
    """Encrypt/decrypt raw bytes with repeating-key XOR."""
    return xor_crypt_bytes(data, key.encode("utf-8"))


def triple_des_encrypt(data: str, key1: str, key2: str, key3: str = None) -> str:
    """EDE3: encrypt with key1, decrypt with key2, encrypt with key3.
    If key3 is not given, key1 is reused (EDE2, common in legacy systems)."""
    from des_core import des_decrypt_bytes
    k1 = _normalize_key(key1, 8)
    k2 = _normalize_key(key2, 8)
    k3 = _normalize_key(key3 if key3 else key1, 8)
    raw = data.encode("utf-8")
    step1 = des_encrypt_bytes(raw, k1)  # padding happens once, here
    # For steps 2 and 3 we use the raw block transform (no re-padding),
    # since step1 is already a multiple of 8 bytes.
    import des_core as d
    subkeys2 = d.generate_subkeys(d._bytes_to_bits(k2))
    step2 = bytearray()
    for i in range(0, len(step1), 8):
        block = d._bytes_to_bits(step1[i:i + 8])
        step2 += d._bits_to_bytes(d._des_block(block, subkeys2, decrypt=True))
    subkeys3 = d.generate_subkeys(d._bytes_to_bits(k3))
    step3 = bytearray()
    for i in range(0, len(step2), 8):
        block = d._bytes_to_bits(bytes(step2[i:i + 8]))
        step3 += d._bits_to_bytes(d._des_block(block, subkeys3, decrypt=False))
    return _b64(bytes(step3))


def aes_encrypt(data: str, key: str) -> str:
    key16 = _normalize_key(key, 16)
    return _b64(aes_encrypt_bytes(data.encode("utf-8"), key16))


def rsa_encrypt(message: str, e: int, n: int) -> str:
    """Encrypts a short message (must fit as an integer < n)."""
    m = text_to_int(message)
    c = rsa_encrypt_int(m, e, n)
    return str(c)


def rsa_generate_keys(bits: int = 512):
    return generate_keypair(bits)
