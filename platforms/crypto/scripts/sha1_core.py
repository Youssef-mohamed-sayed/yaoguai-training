"""Manual (educational) SHA-1 implementation."""


def _left_rotate(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF


def sha1(message: bytes) -> bytes:
    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0

    ml = (len(message) * 8) & 0xFFFFFFFFFFFFFFFF
    msg = bytearray(message)
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg += ml.to_bytes(8, byteorder="big")

    for chunk_start in range(0, len(msg), 64):
        chunk = msg[chunk_start:chunk_start + 64]
        w = [0] * 80
        for i in range(16):
            w[i] = int.from_bytes(chunk[i * 4:i * 4 + 4], "big")
        for i in range(16, 80):
            w[i] = _left_rotate(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)

        a, b, c, d, e = h0, h1, h2, h3, h4
        for i in range(80):
            if i < 20:
                f = (b & c) | (~b & d)
                k = 0x5A827999
            elif i < 40:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif i < 60:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = (_left_rotate(a, 5) + f + e + k + w[i]) & 0xFFFFFFFF
            e = d
            d = c
            c = _left_rotate(b, 30)
            b = a
            a = temp

        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF
        h4 = (h4 + e) & 0xFFFFFFFF

    return b"".join(x.to_bytes(4, "big") for x in (h0, h1, h2, h3, h4))


def sha1_hexdigest(message: bytes) -> str:
    return sha1(message).hex()
