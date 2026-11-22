"""
Hashing functions. MD5, SHA-1, SHA-256 are manual educational implementations
(see md5_core.py / sha1_core.py / sha256_core.py). bcrypt is a deliberately
slow, salted password-hashing algorithm whose internals (Blowfish-based key
schedule, cost factor) are impractical to reimplement safely from scratch for
a teaching project, so we use the `bcrypt` library here - clearly marked as
such. Hashing is one-way: there is no "decrypt" for any of these.
"""
import bcrypt as _bcrypt_lib

from md5_core import md5_hexdigest
from sha1_core import sha1_hexdigest
from sha256_core import sha256_hexdigest


def md5_hash(data: str) -> str:
    return md5_hexdigest(data.encode("utf-8"))


def sha1_hash(data: str) -> str:
    return sha1_hexdigest(data.encode("utf-8"))


def sha256_hash(data: str) -> str:
    return sha256_hexdigest(data.encode("utf-8"))


def bcrypt_hash(data: str, rounds: int = 12) -> str:
    """Library-based (not manual) - see module docstring."""
    salt = _bcrypt_lib.gensalt(rounds=rounds)
    return _bcrypt_lib.hashpw(data.encode("utf-8"), salt).decode("ascii")


def bcrypt_verify(data: str, hashed: str) -> bool:
    return _bcrypt_lib.checkpw(data.encode("utf-8"), hashed.encode("ascii"))


def md5_hash_bytes(data: bytes) -> str:
    return md5_hexdigest(data)


def sha1_hash_bytes(data: bytes) -> str:
    return sha1_hexdigest(data)


def sha256_hash_bytes(data: bytes) -> str:
    return sha256_hexdigest(data)


def bcrypt_hash_bytes(data: bytes, rounds: int = 12) -> str:
    salt = _bcrypt_lib.gensalt(rounds=rounds)
    return _bcrypt_lib.hashpw(data, salt).decode("ascii")


def bcrypt_verify_bytes(data: bytes, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(data, hashed.strip().encode("ascii"))
    except Exception:
        return False
