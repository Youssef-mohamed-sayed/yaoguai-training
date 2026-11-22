"""Manual (educational) SHA-256 implementation, following the standard
algorithm: padding, length append, 64 rounds using the message schedule and
the eight working variables a-h, per FIPS 180-4."""

import math

# first 32 bits of the fractional parts of the cube roots of the first 64 primes
K = [int((p ** (1 / 3) % 1) * 2 ** 32) for p in
     [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
      73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
      157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
      239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311]]

# first 32 bits of the fractional parts of the square roots of the first 8 primes
H0 = [int((p ** 0.5 % 1) * 2 ** 32) for p in [2, 3, 5, 7, 11, 13, 17, 19]]


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256(message: bytes) -> bytes:
    h = list(H0)

    ml = (len(message) * 8) & 0xFFFFFFFFFFFFFFFF
    msg = bytearray(message)
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg += ml.to_bytes(8, byteorder="big")

    for chunk_start in range(0, len(msg), 64):
        chunk = msg[chunk_start:chunk_start + 64]
        w = [0] * 64
        for i in range(16):
            w[i] = int.from_bytes(chunk[i * 4:i * 4 + 4], "big")
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (hh + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            hh = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, hh])]

    return b"".join(x.to_bytes(4, "big") for x in h)


def sha256_hexdigest(message: bytes) -> str:
    return sha256(message).hex()
