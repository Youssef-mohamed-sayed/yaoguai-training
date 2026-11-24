"""Encoding functions: hex, base64, ascii codes, URL (percent) encoding.

Everything here is written by hand with plain loops, no ready-made libraries.
Encoding is NOT encryption: anyone can reverse it, there is no key.

The core work is done by the "_bytes" functions (they work on raw bytes).
The text functions just convert text <-> bytes and call them.
"""

HEX_DIGITS = "0123456789abcdef"
BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
# URL: these characters are safe and stay as they are
URL_SAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-~/"


# ---------------- hex ----------------
# One byte (0-255) becomes two hex characters. Example: 255 -> "ff".

def hex_encode_bytes(data: bytes) -> bytes:
    out = ""
    for byte in data:
        out += HEX_DIGITS[byte >> 4]      # high 4 bits
        out += HEX_DIGITS[byte & 15]      # low 4 bits
    return out.encode("ascii")


def hex_decode_bytes(data: bytes) -> bytes:
    text = ""
    for ch in data.decode("ascii", errors="ignore"):
        if ch not in " \t\r\n":           # ignore spaces and new lines
            text += ch.lower()
    if len(text) % 2 != 0:
        raise ValueError("hex text must have an even number of characters")
    out = bytearray()
    for i in range(0, len(text), 2):
        high = HEX_DIGITS.find(text[i])
        low = HEX_DIGITS.find(text[i + 1])
        if high == -1 or low == -1:
            raise ValueError("invalid hex character")
        out.append(high * 16 + low)
    return bytes(out)


# ---------------- base64 ----------------
# 3 bytes (24 bits) are cut into 4 groups of 6 bits; each group is a letter.
# If the last group has fewer than 3 bytes we add "=" padding.

def base64_encode_bytes(data: bytes) -> bytes:
    out = ""
    for i in range(0, len(data), 3):
        chunk = data[i:i + 3]
        value = 0
        for byte in chunk:                 # join the bytes into one number
            value = value * 256 + byte
        value = value << (8 * (3 - len(chunk)))   # fill missing bytes with zeros
        # take 6 bits at a time, from the left
        out += BASE64_CHARS[(value >> 18) & 63]
        out += BASE64_CHARS[(value >> 12) & 63]
        out += BASE64_CHARS[(value >> 6) & 63] if len(chunk) > 1 else "="
        out += BASE64_CHARS[value & 63] if len(chunk) > 2 else "="
    return out.encode("ascii")


def base64_decode_bytes(data: bytes) -> bytes:
    text = ""
    for ch in data.decode("ascii", errors="ignore"):
        if ch not in " \t\r\n":
            text += ch
    text = text.rstrip("=")
    out = bytearray()
    value = 0
    bits = 0
    for ch in text:
        index = BASE64_CHARS.find(ch)
        if index == -1:
            raise ValueError("invalid base64 character")
        value = (value << 6) | index       # add 6 new bits
        bits += 6
        if bits >= 8:                      # a full byte is ready
            bits -= 8
            out.append((value >> bits) & 255)
    return bytes(out)


# ---------------- ascii codes ----------------
# "Hi" -> "72, 105"

def ascii_encode_bytes(data: bytes) -> bytes:
    numbers = []
    for byte in data:
        numbers.append(str(byte))
    return ", ".join(numbers).encode("ascii")


def ascii_decode_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="ignore")
    text = text.replace("\n", ",").replace("\r", ",")
    out = bytearray()
    for part in text.split(","):
        part = part.strip()
        if part != "":
            number = int(part)
            if number < 0 or number > 255:
                raise ValueError("ascii code must be between 0 and 255")
            out.append(number)
    return bytes(out)


# ---------------- URL (percent) encoding ----------------
# Safe characters stay. Every other byte becomes "%" + two hex digits.

def url_encode_bytes(data: bytes) -> bytes:
    out = ""
    for byte in data:
        ch = chr(byte)
        if ch in URL_SAFE:
            out += ch
        else:
            out += "%" + HEX_DIGITS[byte >> 4].upper() + HEX_DIGITS[byte & 15].upper()
    return out.encode("ascii")


def url_decode_bytes(data: bytes) -> bytes:
    text = data.decode("ascii", errors="ignore")
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%" and i + 2 < len(text):
            high = HEX_DIGITS.find(text[i + 1].lower())
            low = HEX_DIGITS.find(text[i + 2].lower())
            if high != -1 and low != -1:
                out.append(high * 16 + low)
                i += 3
                continue
        out.append(ord(text[i]))
        i += 1
    return bytes(out)


# ---------------- text versions (used by the simple tools) ----------------

def hex_encode(data: str) -> str:
    return hex_encode_bytes(data.encode("utf-8")).decode("ascii")


def hex_decode(data: str) -> str:
    return hex_decode_bytes(data.encode("ascii", errors="ignore")).decode("utf-8", errors="replace")


def base64_encode(data: str) -> str:
    return base64_encode_bytes(data.encode("utf-8")).decode("ascii")


def base64_decode(data: str) -> str:
    return base64_decode_bytes(data.encode("ascii", errors="ignore")).decode("utf-8", errors="replace")


def ascii_encode(data: str) -> list:
    # list of ascii codes per character
    codes = []
    for ch in data:
        codes.append(ord(ch))
    return codes


def ascii_decode(codes) -> str:
    # codes: list of ints, or comma separated string
    if isinstance(codes, str):
        codes = [int(c.strip()) for c in codes.split(",") if c.strip() != ""]
    text = ""
    for c in codes:
        text += chr(int(c))
    return text


def url_encode(data: str) -> str:
    return url_encode_bytes(data.encode("utf-8")).decode("ascii")


def url_decode(data: str) -> str:
    return url_decode_bytes(data.encode("ascii", errors="ignore")).decode("utf-8", errors="replace")
