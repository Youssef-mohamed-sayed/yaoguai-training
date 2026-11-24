"""Checks the hand-written crypto tools against known correct answers.
The standard library (hashlib, base64, urllib) is used ONLY here, as the
"answer key". Run:  python -m unittest platforms/crypto/tests/test_crypto_tools.py
"""
import base64, hashlib, os, sys, unittest, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import encoding, md5_core, sha1_core, sha256_core, stream_core, aes_core, des_core, rsa_core

SAMPLES = [b"", b"a", b"ab", b"abc", b"Hello, World!", "yaoguai 妖怪 & co/?=".encode("utf-8"), bytes(range(256))]


class EncodingTests(unittest.TestCase):
    def test_hex(self):
        for s in SAMPLES:
            self.assertEqual(encoding.hex_encode_bytes(s), s.hex().encode())
            self.assertEqual(encoding.hex_decode_bytes(s.hex().encode()), s)

    def test_base64(self):
        for s in SAMPLES:
            self.assertEqual(encoding.base64_encode_bytes(s), base64.b64encode(s))
            self.assertEqual(encoding.base64_decode_bytes(base64.b64encode(s)), s)

    def test_url(self):
        for s in SAMPLES:
            self.assertEqual(encoding.url_encode_bytes(s), urllib.parse.quote_from_bytes(s).encode())
            self.assertEqual(encoding.url_decode_bytes(encoding.url_encode_bytes(s)), s)

    def test_ascii(self):
        self.assertEqual(encoding.ascii_encode("Hi"), [72, 105])
        self.assertEqual(encoding.ascii_decode("72, 105"), "Hi")


class HashTests(unittest.TestCase):
    def test_md5_sha1_sha256(self):
        for s in SAMPLES + [b"x" * 55, b"x" * 56, b"x" * 64, b"x" * 1000]:
            self.assertEqual(md5_core.md5_hexdigest(s), hashlib.md5(s).hexdigest())
            self.assertEqual(sha1_core.sha1_hexdigest(s), hashlib.sha1(s).hexdigest())
            self.assertEqual(sha256_core.sha256_hexdigest(s), hashlib.sha256(s).hexdigest())


class CipherTests(unittest.TestCase):
    def test_xor_roundtrip(self):
        self.assertEqual(stream_core.xor_crypt_bytes(stream_core.xor_crypt_bytes(b"secret", b"key"), b"key"), b"secret")

    def test_rc4_known_vector(self):
        # classic RC4 test: key "Key", plaintext "Plaintext"
        self.assertEqual(stream_core.rc4_crypt_bytes(b"Plaintext", b"Key").hex().upper(), "BBF316E8D940AF0AD3")

    def test_aes_fips197_block(self):
        # FIPS-197 appendix C.1 (AES-128): key 000102..0f, plaintext 00112233..ff
        key = bytes(range(16))
        plain = bytes.fromhex("00112233445566778899aabbccddeeff")
        cipher = aes_core.aes_encrypt_bytes(plain, key)
        self.assertEqual(cipher[:16].hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")
        self.assertEqual(aes_core.aes_decrypt_bytes(cipher, key), plain)

    def test_des_known_vector(self):
        # classic DES vector: key 133457799BBCDFF1, plaintext 0123456789ABCDEF
        key = bytes.fromhex("133457799BBCDFF1")
        plain = bytes.fromhex("0123456789ABCDEF")
        cipher = des_core.des_encrypt_bytes(plain, key)
        self.assertEqual(cipher[:8].hex().upper(), "85E813540F0AB405")
        self.assertEqual(des_core.des_decrypt_bytes(cipher, key), plain)

    def test_rsa_textbook(self):
        # p=61, q=53 -> n=3233, e=17, d=2753; message 65 -> 2790
        self.assertEqual(rsa_core.rsa_encrypt_int(65, 17, 3233), 2790)
        self.assertEqual(rsa_core.rsa_decrypt_int(2790, 2753, 3233), 65)

    def test_rsa_generated_keys(self):
        k = rsa_core.generate_keypair(128)
        m = rsa_core.text_to_int("hi")
        self.assertEqual(rsa_core.rsa_decrypt_int(rsa_core.rsa_encrypt_int(m, k["e"], k["n"]), k["d"], k["n"]), m)


if __name__ == "__main__":
    unittest.main()
