"""
Manual (educational) RSA implementation, following the slides' mechanism:
1) choose primes p, q
2) n = p*q, phi = (p-1)*(q-1)
3) choose e coprime with phi
4) d = modular inverse of e mod phi
Encryption: c = m^e mod n. Decryption: m = c^d mod n.
Uses small Miller-Rabin primality test to generate demo-sized primes;
real RSA needs 1024+ bit primes, which this is NOT intended to produce.
"""
import random


def _is_probable_prime(n, rounds=20):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _generate_prime(bits):
    while True:
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if _is_probable_prime(candidate):
            return candidate


def _egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _egcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def _modinv(a, m):
    g, x, _ = _egcd(a, m)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    return x % m


def generate_keypair(bits=512):
    p = _generate_prime(bits // 2)
    q = _generate_prime(bits // 2)
    while q == p:
        q = _generate_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if phi <= e:
        e = 3
    while _egcd(e, phi)[0] != 1:
        e += 2
    d = _modinv(e, phi)
    return {"n": n, "e": e, "d": d, "p": p, "q": q}


def rsa_encrypt_int(m: int, e: int, n: int) -> int:
    if m >= n:
        raise ValueError("message integer must be smaller than modulus n")
    return pow(m, e, n)


def rsa_decrypt_int(c: int, d: int, n: int) -> int:
    return pow(c, d, n)


def text_to_int(text: str) -> int:
    return int.from_bytes(text.encode("utf-8"), "big")


def int_to_text(value: int) -> str:
    length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big").decode("utf-8", errors="replace")
