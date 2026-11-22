"""Manual XOR cipher and RC4 stream cipher implementations."""


def xor_crypt_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("key must not be empty")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _rc4_ksa(key: bytes):
    S = list(range(256))
    j = 0
    key_len = len(key)
    for i in range(256):
        j = (j + S[i] + key[i % key_len]) % 256
        S[i], S[j] = S[j], S[i]
    return S


def _rc4_prga(S, length):
    i = j = 0
    out = bytearray()
    S = S[:]
    for _ in range(length):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        out.append(k)
    return bytes(out)


def rc4_crypt_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("key must not be empty")
    S = _rc4_ksa(key)
    keystream = _rc4_prga(S, len(data))
    return bytes(b ^ k for b, k in zip(data, keystream))
