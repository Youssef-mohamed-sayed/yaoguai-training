# Project: File Hash Calculator

## Learning Objectives

- Hash files of any size with chunked reading.
- Verify downloads against published checksums.
- Compare hashes safely and report matches clearly.

## Introduction

A cryptographic hash (SHA-256 here) maps any input to a fixed 64-hex-digit digest; change one bit of a file and the digest is unrecognizably different. That makes hashing the standard answer to "did this file change or arrive intact?" - download verification, backup integrity, and the file-watching from module 17.

## Chunked Hashing

Reading a 4 GB ISO into memory to hash it is a self-own. Hash in 64 KB chunks:

```python
import hashlib

def sha256_file(path, chunk_size=65536):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()
```

The walrus operator `:=` assigns `chunk` and tests it in one expression: `f.read` returns empty bytes at EOF, which is falsy, ending the loop. Constant memory, any file size.

## Verifying a Download

Vendors publish checksums next to downloads. Comparing what you got against what they published catches corruption and (on a trusted channel) tampering:

```python
import sys

def main():
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} FILE EXPECTED_SHA256")
    _, path, expected = sys.argv
    actual = sha256_file(path)
    print(f"file:     {path}")
    print(f"actual:   {actual}")
    print(f"expected: {expected.lower()}")
    if actual == expected.strip().lower():
        print("MATCH - file is intact")
        return 0
    print("MISMATCH - do not trust this file")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
```

```text
$ python3 verify.py ubuntu.iso 9f8c...d2
file:     ubuntu.iso
actual:   9f8c...d2
expected: 9f8c...d2
MATCH - file is intact
```

Normalize case and whitespace before comparing - published checksums vary in formatting. Exit code 0/1 lets scripts chain the check (`verify.py ... && sudo ./install.sh`).

## Notes That Matter

- **MD5 and SHA-1 are broken for security purposes** (collisions are practical). Fine for accidental-corruption checks, never for tamper evidence. Default to SHA-256.
- A checksum only proves integrity if the *published* value came over a trusted channel; a hash posted next to the download on the same compromised server proves little.
- `hashlib` also offers `sha512`, `blake2b` (fast); `hmac` for keyed verification.

## Common Mistakes

- Hashing the whole `read()` of a huge file instead of chunking.
- Comparing digests case-sensitively or with trailing whitespace and reporting false mismatches.
- Using MD5 "because the site gave an MD5" without understanding it detects accidents, not attackers.

## Key Takeaways

- `hashlib.sha256()` + `.update()` in a read loop hashes any file in constant memory.
- Compare normalized digests, report MATCH/MISMATCH, and return a meaningful exit code.
- SHA-256 for anything security-relevant; MD5/SHA-1 only for accident detection.

## Practice Exercises

**Exercise 1.** Hash a file with your script and with the system tool (`sha256sum` on Linux, `shasum -a 256` on macOS, `certutil -hashfile f SHA256` on Windows). Confirm they agree.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 verify.py report.pdf $(sha256sum report.pdf | cut -d' ' -f1)
file:     report.pdf
actual:   4c2f...9a
expected: 4c2f...9a
MATCH - file is intact
```

Agreement with the OS tool validates the chunked implementation.
</details>

**Exercise 2.** Flip one byte in a copy of the file (`printf 'x' | dd of=copy bs=1 count=1 conv=notrunc` on Linux/macOS) and show the digest changes completely.

<details>
<summary>Show a worked solution</summary>

```text
$ cp report.pdf copy.pdf
$ printf 'x' | dd of=copy.pdf bs=1 count=1 conv=notrunc
$ python3 verify.py copy.pdf 4c2f...9a
actual:   71bd...03
MISMATCH - do not trust this file
```

The avalanche effect: one flipped bit changes about half the digest bits.
</details>

**Exercise 3.** Extend the script to hash every file in a directory and print a `sha256sum`-compatible listing (`digest  filename`).

<details>
<summary>Show a worked solution</summary>

```python
from pathlib import Path

for p in sorted(Path(sys.argv[1].rstrip('/')).glob("*")):
    if p.is_file():
        print(f"{sha256_file(p)}  {p.name}")
```

```text
$ python3 hashall.py downloads
4c2f...9a  report.pdf
aa01...7e  notes.txt
```
</details>

## Check Yourself

**Why hash in chunks instead of `sha256(path.read_bytes())`?**

<details>
<summary>Show answer</summary>

`read_bytes()` loads the whole file into RAM; chunked updates keep memory constant regardless of file size.
</details>

**What does the walrus operator do in the read loop?**

<details>
<summary>Show answer</summary>

`while chunk := f.read(n)` assigns the read result to `chunk` and tests its truthiness in one step, ending the loop at EOF (empty bytes).
</details>

**Why is MD5 unacceptable for verifying software against tampering?**

<details>
<summary>Show answer</summary>

Practical collision attacks let an attacker craft a malicious file with the same MD5 as the genuine one; SHA-256 has no such practical attacks.
</details>
