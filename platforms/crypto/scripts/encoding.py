"""Encoding functions: hex, base64, ascii, url."""
import base64
import urllib.parse


def hex_encode(data: str) -> str:
    return data.encode("utf-8").hex()


def hex_decode(data: str) -> str:
    return bytes.fromhex(data).decode("utf-8", errors="replace")


def base64_encode(data: str) -> str:
    return base64.b64encode(data.encode("utf-8")).decode("ascii")


def base64_decode(data: str) -> str:
    return base64.b64decode(data).decode("utf-8", errors="replace")


def ascii_encode(data: str) -> list:
    # list of ascii codes per character
    return [ord(c) for c in data]


def ascii_decode(codes) -> str:
    # codes: list of ints, or comma separated string
    if isinstance(codes, str):
        codes = [int(c.strip()) for c in codes.split(",") if c.strip() != ""]
    return "".join(chr(int(c)) for c in codes)


def url_encode(data: str) -> str:
    return urllib.parse.quote(data)


def url_decode(data: str) -> str:
    return urllib.parse.unquote(data)


def hex_encode_bytes(data: bytes) -> bytes:
    return data.hex().encode("ascii")


def hex_decode_bytes(data: bytes) -> bytes:
    clean = "".join(data.decode("ascii", errors="ignore").split())
    return bytes.fromhex(clean)


def base64_encode_bytes(data: bytes) -> bytes:
    return base64.b64encode(data)


def base64_decode_bytes(data: bytes) -> bytes:
    return base64.b64decode(data.strip())


def ascii_encode_bytes(data: bytes) -> bytes:
    return ", ".join(str(b) for b in data).encode("ascii")


def ascii_decode_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="ignore")
    codes = [int(c.strip()) for c in text.replace("\n", ",").replace("\r", ",").split(",") if c.strip()]
    return bytes(codes)


def url_encode_bytes(data: bytes) -> bytes:
    return urllib.parse.quote_from_bytes(data).encode("ascii")


def url_decode_bytes(data: bytes) -> bytes:
    return urllib.parse.unquote_to_bytes(data.decode("ascii", errors="ignore"))
