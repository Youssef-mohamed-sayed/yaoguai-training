# Cryptography / Encoding Flask API

An educational Flask REST API covering encoding, symmetric/asymmetric
encryption, hashing, and password-cracking integrations, built to be
consumed by a front-end web app.

## A. Topic inventory

| Category | Algorithm | In slides? | Implemented? |
|---|---|---:|---:|
| Basics | Plaintext/ciphertext/key terminology | Yes | N/A (concept only) |
| Basics | Symmetric vs asymmetric cryptosystems | Yes | N/A (concept only) |
| Basics | Stream cipher / One-Time Pad | Yes (mentioned, no algorithm detail) | Not practical from slides alone; OTP requires a truly random key as long as the message, so it isn't a "cracking/implementing" exercise - noted only |
| Basics | Block cipher concept | Yes | N/A (concept, covered by DES/AES) |
| Symmetric | DES (full 16-round, key schedule, Feistel, S-boxes) | Yes (detailed) | Yes - manual, `des_core.py` |
| Symmetric | S-DES (simplified 2-round teaching cipher) | Yes (detailed, separate PDF/notebooks) | Not exposed as its own endpoint (full DES supersedes it); logic is present in the uploaded notebooks and mirrored by `des_core.py`'s structure |
| Symmetric | IDEA, RC6 (named in a diagram only) | Yes (named only, no algorithm detail given) | Not implemented - no detail was given in the slides to implement correctly; noted here per the "identify but don't silently omit" instruction |
| Symmetric | AES | Requested explicitly (not detailed in slides) | Yes - manual, `aes_core.py` (AES-128, ECB+PKCS7) |
| Symmetric | 3DES / Triple DES | Requested explicitly | Yes - built on `des_core.py` (EDE2/EDE3) |
| Symmetric | XOR cipher | Requested explicitly | Yes - manual, `stream_core.py` |
| Symmetric | RC4 | Requested explicitly | Yes - manual, `stream_core.py` |
| Asymmetric | RSA (key generation, encryption, decryption) | Yes (detailed, worked example) | Yes - manual, `rsa_core.py` |
| Asymmetric | Diffie-Hellman key exchange | Yes (detailed, worked example) | Not exposed as an encrypt/decrypt endpoint since DH is a *key exchange*, not a cipher - it has no ciphertext to produce. The slides' own worked example (p=23, g=9, private a/b) is pure modular exponentiation and can be added as a `/api/dh/exchange` endpoint if the front end needs it; flagged here rather than silently dropped. |
| Hashing | Hash function concept, use cases | Yes | N/A (concept) |
| Hashing | MD5 (full algorithm: padding, buffers, 4 rounds of 16 steps) | Yes (detailed) | Yes - manual, `md5_core.py` |
| Hashing | SHA-1 | Requested explicitly (slides mention it by name only) | Yes - manual, `sha1_core.py` |
| Hashing | SHA-256 | Requested explicitly | Yes - manual, `sha256_core.py` |
| Hashing | bcrypt | Requested explicitly | Library-based (`bcrypt` package) - see note below |
| Cracking | John the Ripper | Requested explicitly | Yes - subprocess wrapper, `crack.py` |
| Cracking | Hashcat | Requested explicitly | Yes - subprocess wrapper, `crack.py` |
| Cracking | RockYou wordlist | Requested explicitly | Yes - default wordlist path, `rockyou.txt` (placeholder included - replace with the real file) |
| Cracking | Hashes.com lookup | Requested explicitly | Yes - real documented API, `hashescom.py` |

**Why bcrypt isn't manually implemented:** bcrypt's security comes from its
expensive, Blowfish-derived key schedule (`EksBlowfishSetup`) run many times
based on a configurable cost factor. Reimplementing this correctly and
safely from scratch is a significant undertaking with real security
pitfalls (e.g. getting the Blowfish P/S-box initialization or the OpenBSD
`$2b$` encoding subtly wrong), so this project uses the well-audited
`bcrypt` Python package instead and documents that choice rather than
presenting a toy version as production-safe.

**Why Hashes.com instead of CrackStation:** CrackStation's public form is
gated behind a Google reCAPTCHA that only a human in a browser can solve,
so no automated request - including one made by this app's own backend -
can ever succeed against it (confirmed against CrackStation's own published
source). Hashes.com, by contrast, publishes a real, documented API
(https://hashes.com/en/api) that takes a plain POST request and returns
JSON, no captcha involved, so it actually works when called from a
backend. It does require a free Hashes.com account and an API key, which
the person pastes into the Tools page themselves (never hardcoded here) -
see `hashescom.py`.

## B. Project structure

```text
API/
├── app.py              # Flask routes
├── encoding.py          # hex/base64/ascii/url encode+decode
├── decoding.py          # thin re-export of the decode half of encoding.py
├── encryption.py        # encrypt functions for every cipher
├── decryption.py        # decrypt functions for every cipher
├── hashing.py           # md5/sha1/sha256 (manual) + bcrypt (library)
├── crack.py             # John the Ripper / Hashcat subprocess wrappers
├── hashescom.py          # Hashes.com API integration (crowd-sourced "already cracked" lookup)
├── des_core.py          # manual DES (verified against FIPS 46-3 test vector)
├── aes_core.py           # manual AES-128 (verified against FIPS-197 test vector)
├── stream_core.py        # manual XOR and RC4
├── rsa_core.py           # manual RSA (prime gen, key gen, modpow)
├── md5_core.py           # manual MD5 (verified against hashlib)
├── sha1_core.py          # manual SHA-1 (verified against hashlib)
├── sha256_core.py        # manual SHA-256 (verified against hashlib)
├── requirements.txt
├── README.md
└── rockyou.txt           # placeholder - replace with the real wordlist
```

## C. Installation

```bash
pip install -r requirements.txt
```

## D. Running

```bash
python app.py
```

The API listens on `http://localhost:5000` by default.

### John the Ripper / Hashcat setup

These are **not** Python packages - they are separate command-line tools
that must be installed on the host OS and available on `PATH`:

- **John the Ripper**: `apt install john` (Debian/Ubuntu), or build from
  https://github.com/openwall/john. Verify with `john --version`.
- **Hashcat**: `apt install hashcat`, or download from https://hashcat.net.
  Verify with `hashcat --version`.

If a tool isn't found, the corresponding endpoint returns
`{"success": false, "error": "... is not installed or not on PATH."}`
rather than crashing.

### rockyou.txt

Replace the placeholder `rockyou.txt` in the project root with the real
RockYou wordlist (widely available for security research/education). The
cracking endpoints resolve this path relative to the project directory, so
no absolute path needs to be configured - just drop the real file in place
of the placeholder.

## E. API documentation

All endpoints accept and return JSON. Successful responses:
`{"success": true, "result": ...}`. Errors: `{"success": false, "error": "..."}`
with an appropriate HTTP status code (usually 400).

### Encoding / Decoding

| Method | Endpoint | Body | Example response |
|---|---|---|---|
| POST | `/api/encoding/hex/encode` | `{"data": "hi"}` | `{"result": "6869"}` |
| POST | `/api/encoding/hex/decode` | `{"data": "6869"}` | `{"result": "hi"}` |
| POST | `/api/encoding/base64/encode` | `{"data": "hi"}` | `{"result": "aGk="}` |
| POST | `/api/encoding/base64/decode` | `{"data": "aGk="}` | `{"result": "hi"}` |
| POST | `/api/encoding/ascii/encode` | `{"data": "hi"}` | `{"result": [104, 105]}` |
| POST | `/api/encoding/ascii/decode` | `{"data": "104,105"}` | `{"result": "hi"}` |
| POST | `/api/encoding/url/encode` | `{"data": "a b"}` | `{"result": "a%20b"}` |
| POST | `/api/encoding/url/decode` | `{"data": "a%20b"}` | `{"result": "a b"}` |

### Encryption / Decryption

Encryption returns base64 ciphertext in the JSON response (except RSA,
which uses a decimal integer string, matching the slides' `c = m^e mod n`).
Decryption auto-detects the input format: base64, hex, decimal byte lists
("221 184 52 ..."), or plain UTF-8 text are all accepted and converted
internally to the bytes each algorithm needs.

| Method | Endpoint | Body |
|---|---|---|
| POST | `/api/encryption/xor` | `{"data": "hi", "key": "k"}` |
| POST | `/api/decryption/xor` | `{"data": "<base64>", "key": "k"}` |
| POST | `/api/encryption/rc4` | `{"data": "hi", "key": "k"}` |
| POST | `/api/decryption/rc4` | `{"data": "<base64>", "key": "k"}` |
| POST | `/api/encryption/des` | `{"data": "hi", "key": "mykey123"}` |
| POST | `/api/decryption/des` | `{"data": "<base64>", "key": "mykey123"}` |
| POST | `/api/encryption/3des` | `{"data": "hi", "key1": "...", "key2": "...", "key3": "..." (optional)}` |
| POST | `/api/decryption/3des` | same shape |
| POST | `/api/encryption/aes` | `{"data": "hi", "key": "0123456789abcdef"}` |
| POST | `/api/decryption/aes` | `{"data": "<base64>", "key": "0123456789abcdef"}` |
| POST | `/api/encryption/rsa/generate-keys` | `{"bits": 512}` -> `{"n": ..., "e": ..., "d": ...}` |
| POST | `/api/encryption/rsa` | `{"data": "hi", "e": ..., "n": ...}` |
| POST | `/api/decryption/rsa` | `{"data": "<int string>", "d": ..., "n": ...}` |

Keys for DES/AES are any UTF-8 string; they're padded/truncated to the
required byte length (8 bytes for DES, 16 for AES-128) - this is a teaching
convenience, not a secure key-derivation function.

### Hashing

| Method | Endpoint | Body |
|---|---|---|
| POST | `/api/hashing/md5` | `{"data": "hi"}` |
| POST | `/api/hashing/sha1` | `{"data": "hi"}` |
| POST | `/api/hashing/sha256` | `{"data": "hi"}` |
| POST | `/api/hashing/bcrypt` | `{"data": "hi", "rounds": 12}` |
| POST | `/api/hashing/bcrypt/verify` | `{"data": "hi", "hash": "$2b$..."}` |

### Cracking

| Method | Endpoint | Body |
|---|---|---|
| POST | `/api/crack/john` | `{"hash": "5d41...", "hash_type": "md5", "wordlist": "/optional/path"}` |
| POST | `/api/crack/hashcat` | same shape |
| POST | `/api/hashescom` | `{"hash": "5d41...", "api_key": "..."}` |

## F. curl examples

```bash
curl -X POST http://localhost:5000/api/hashing/md5 \
  -H "Content-Type: application/json" \
  -d '{"data": "hello"}'

curl -X POST http://localhost:5000/api/encryption/aes \
  -H "Content-Type: application/json" \
  -d '{"data": "hello world", "key": "mysecretkey12345"}'

curl -X POST http://localhost:5000/api/encryption/rsa/generate-keys \
  -H "Content-Type: application/json" \
  -d '{"bits": 512}'

curl -X POST http://localhost:5000/api/crack/john \
  -H "Content-Type: application/json" \
  -d '{"hash": "5d41402abc4b2a76b9719d911017c592", "hash_type": "md5"}'
```

## G. Security notes

- All block ciphers here use ECB mode with PKCS7 padding for simplicity.
  ECB leaks patterns in the plaintext and should never be used in real
  systems - use an authenticated mode like AES-GCM with a random IV/nonce
  for anything beyond learning the algorithm's internals.
- DES, 3DES, XOR, and RC4 are legacy/broken for real security use and are
  included for educational/historical purposes only (DES's 56-bit
  effective key is brute-forceable; RC4 has known biases; XOR is trivially
  broken with known-plaintext).
- MD5 and SHA-1 are cryptographically broken for collision resistance and
  should not be used for digital signatures or certificate hashing; they
  remain useful for teaching and some non-adversarial checksums.
- The manual RSA here generates small (demo-sized) keys by default and is
  not constant-time - do not use it for real secrets. Use 2048+ bit keys
  and a vetted library (e.g. `cryptography`) for production RSA.
- `crack.py` never builds shell command strings; it only calls
  `subprocess.run([...])` with explicit argument lists.
