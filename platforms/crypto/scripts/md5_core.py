"""Manual (educational) MD5 implementation, following the standard algorithm
described in the slides: padding, length append, 4 rounds of 16 steps each
using F/G/H/I functions, per-round constants K and shift amounts."""

S = [
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
]

import math
K = [int(abs(math.sin(i + 1)) * 2 ** 32) & 0xFFFFFFFF for i in range(64)]


def _left_rotate(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF


def md5(message: bytes) -> bytes:
    a0, b0, c0, d0 = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476

    orig_len_bits = (len(message) * 8) & 0xFFFFFFFFFFFFFFFF
    msg = bytearray(message)
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg += orig_len_bits.to_bytes(8, byteorder="little")

    for chunk_start in range(0, len(msg), 64):
        chunk = msg[chunk_start:chunk_start + 64]
        M = [int.from_bytes(chunk[i:i + 4], "little") for i in range(0, 64, 4)]

        A, B, C, D = a0, b0, c0, d0
        for i in range(64):
            if i < 16:
                F = (B & C) | (~B & D)
                g = i
            elif i < 32:
                F = (D & B) | (~D & C)
                g = (5 * i + 1) % 16
            elif i < 48:
                F = B ^ C ^ D
                g = (3 * i + 5) % 16
            else:
                F = C ^ (B | (~D & 0xFFFFFFFF))
                g = (7 * i) % 16

            F = (F + A + K[i] + M[g]) & 0xFFFFFFFF
            A = D
            D = C
            C = B
            B = (B + _left_rotate(F, S[i])) & 0xFFFFFFFF

        a0 = (a0 + A) & 0xFFFFFFFF
        b0 = (b0 + B) & 0xFFFFFFFF
        c0 = (c0 + C) & 0xFFFFFFFF
        d0 = (d0 + D) & 0xFFFFFFFF

    return b"".join(x.to_bytes(4, "little") for x in (a0, b0, c0, d0))


def md5_hexdigest(message: bytes) -> str:
    return md5(message).hex()
