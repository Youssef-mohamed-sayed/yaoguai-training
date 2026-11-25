# pathlib and Binary Files

## Learning Objectives

- Build and inspect filesystem paths with `pathlib.Path` instead of string surgery.
- Read and write binary data and know when text mode is wrong.
- Walk directories and filter files by pattern.

## Introduction

String-concatenating paths (`folder + "/" + name`) breaks across operating systems and edge cases. `pathlib.Path` is the modern, object-oriented answer:

```python
from pathlib import Path

logdir = Path("/var/log")
auth = logdir / "auth.log"          # the / operator joins parts safely
print(auth.name)                    # auth.log
print(auth.stem, auth.suffix)       # auth .log
print(auth.parent)                  # /var/log
print(auth.exists(), auth.is_file())  # True True
print(auth.stat().st_size)          # bytes
```

`Path` picks the right separator per OS, so the same code runs on Linux and Windows. Use `Path.home()` and `Path.cwd()` instead of hardcoding.

## Globbing: Finding Files

```python
for path in Path(".").glob("*.py"):        # this directory only
    print(path)

for path in Path("logs").rglob("*.log"):   # recursive
    print(path, path.stat().st_size)

sorted(Path(".").glob("*.txt"), key=lambda p: p.stat().st_mtime)
```

`glob` vs `rglob` (non-recursive vs recursive) covers most "find me the files" needs without touching `os.walk`.

## Binary Mode

Images, packet captures, executables, and anything compressed are **bytes**, not text. Open with `"rb"`/`"wb"` and work with `bytes`:

```python
data = Path("firmware.bin").read_bytes()
print(len(data), data[:8].hex())

png = Path("logo.png").read_bytes()
print(png[:8])   # b'\x89PNG\r\n\x1a\n' - the PNG magic number
```

Reading the first bytes to identify a file type (magic numbers) is a real forensics technique: PNG starts with `89 50 4E 47`, ZIP/GZip/PDF/JPEG each have their own signature. Opening a binary file in text mode risks a `UnicodeDecodeError` - that error often *is* the hint the file is not text.

`read_bytes()`/`write_bytes()` and `read_text()`/`write_text()` on `Path` are one-call conveniences for known-small files:

```python
Path("result.bin").write_bytes(b"\x00\x01\x02")
Path("config.txt").write_text("debug = true\n", encoding="utf-8")
```

## Common Mistakes

- Joining paths with `+` and `/` by hand; one missing or doubled separator and the script only works on your machine.
- Parsing binary data in text mode and chasing encoding errors.
- Assuming a file's extension tells the truth; check magic bytes when it matters.
- `rglob("*")` over a huge tree without a pattern - it walks everything.

## Key Takeaways

- `pathlib.Path` joins with `/`, exposes `name`/`stem`/`suffix`/`parent`, and checks with `exists()`/`is_file()`.
- `glob`/`rglob` find files by pattern; sort by `stat()` fields when order matters.
- Binary data uses `"rb"`/`"wb"` and bytes; magic numbers identify file types better than extensions.

## Practice Exercises

**Exercise 1.** List all `.py` files in the current directory with their sizes, sorted from smallest to largest.

<details>
<summary>Show a worked solution</summary>

```python
from pathlib import Path

files = sorted(Path(".").glob("*.py"), key=lambda p: p.stat().st_size)
for p in files:
    print(f"{p.stat().st_size:>8} {p.name}")
```
</details>

**Exercise 2.** Print the first 16 bytes of any file as hex, and say whether it looks like a PNG, ZIP, or neither.

<details>
<summary>Show a worked solution</summary>

```python
from pathlib import Path
import sys

data = Path(sys.argv[1]).read_bytes()[:16]
print(data.hex(" "))
if data.startswith(b"\x89PNG"):
    print("PNG image")
elif data.startswith(b"PK\x03\x04"):
    print("ZIP archive")
else:
    print("unknown type")
```
</details>

**Exercise 3.** Recursively find all `.log` files under a directory given on the command line and print the total size.

<details>
<summary>Show a worked solution</summary>

```python
from pathlib import Path
import sys

total = 0
for p in Path(sys.argv[1]).rglob("*.log"):
    size = p.stat().st_size
    total += size
    print(f"{size:>10} {p}")
print(f"{total:>10} TOTAL")
```
</details>

## Check Yourself

**What does the `/` operator do on two `Path` objects?**

<details>
<summary>Show answer</summary>

It joins them into a new path with the correct separator for the OS: `Path("/var") / "log"` is `/var/log`.
</details>

**Why can opening a PNG in text mode fail?**

<details>
<summary>Show answer</summary>

Text mode decodes bytes as UTF-8, and image bytes are not valid UTF-8, raising `UnicodeDecodeError`. Use `"rb"` for binary files.
</details>

**What is the difference between `glob("*.log")` and `rglob("*.log")`?**

<details>
<summary>Show answer</summary>

`glob` matches only in the current directory; `rglob` recurses into all subdirectories.
</details>
