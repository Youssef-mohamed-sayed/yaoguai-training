# Reading and Writing Files

## Learning Objectives

- Open files safely with `with`, choosing the right mode and encoding.
- Read whole files, iterate line by line, and write or append output.
- Understand what happens when paths are wrong and how to fail cleanly.

## Introduction

File I/O is three questions: **which file, which mode, which encoding.** The `with` statement answers a fourth - guaranteeing the file closes even when an error interrupts:

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    text = f.read()
```

Modes: `"r"` read (default, errors if missing), `"w"` write (**truncates the file to empty first**), `"a"` append, `"x"` create but fail if it exists. Add `"b"` for binary (`"rb"`, `"wb"`), which returns `bytes` and skips encoding. Always pass `encoding="utf-8"` for text; the platform default varies and causes mojibake bugs that only appear on other machines.

## Reading Patterns

```python
with open("app.log", encoding="utf-8") as f:
    whole = f.read()          # entire file as one string - small files only

with open("app.log", encoding="utf-8") as f:
    lines = f.readlines()     # list of lines, each keeping its '\n'

with open("app.log", encoding="utf-8") as f:
    for line in f:            # lazy: constant memory at any file size
        process(line.rstrip("\n"))
```

The loop form is the professional default: a 10 GB log streams through with the same memory as a 10 KB one. `readlines()` on a huge file is a self-inflicted outage; `read()` is for files you know are small.

## Writing and Appending

```python
with open("report.txt", "w", encoding="utf-8") as f:
    f.write("scan report\n")
    print("host: web-1", file=f)     # print can write to any file object

with open("report.txt", "a", encoding="utf-8") as f:
    f.write("--- second run ---\n")
```

Remember: `"w"` destroys existing content the moment `open` succeeds, before a single `write`. If data loss would hurt, write to a temp file and rename, or use `"a"` and headers.

## When the Path Is Wrong

`open` raises `FileNotFoundError` for a missing read target and `PermissionError` when access is denied. For scripts, catching and saying something useful beats a raw traceback:

```python
import sys

try:
    f = open(sys.argv[1], encoding="utf-8")
except FileNotFoundError:
    sys.exit(f"no such file: {sys.argv[1]}")
except PermissionError:
    sys.exit(f"permission denied: {sys.argv[1]}")

with f:
    ...
```

`sys.exit(message)` prints to stderr and exits with code 1 - exactly what a command-line tool should do. Module 11 goes deeper on exception handling.

## Common Mistakes

- Forgetting `with`, leaving files unflushed or locked (especially on Windows).
- Reading with `readlines()` or `read()` on multi-GB logs.
- Opening in `"w"` when `"a"` was meant; the old data is already gone.
- Omitting `encoding="utf-8"` and getting `UnicodeDecodeError` on a teammate's machine.

## Key Takeaways

- `with open(path, mode, encoding="utf-8")` is the one safe pattern; modes are `r/w/a/x` plus `b` for binary.
- Iterate `for line in f` for anything that might be large; `read()`/`readlines()` are for known-small files.
- `"w"` truncates immediately; catch `FileNotFoundError`/`PermissionError` and exit with a clear message.

## Practice Exercises

**Exercise 1.** Write three lines to `out.txt`, then read the file back and print it. Verify the content with `cat out.txt`.

<details>
<summary>Show a worked solution</summary>

```python
with open("out.txt", "w", encoding="utf-8") as f:
    for n in range(1, 4):
        f.write(f"line {n}\n")

with open("out.txt", encoding="utf-8") as f:
    print(f.read())
```

```text
line 1
line 2
line 3
```
</details>

**Exercise 2.** Count the lines, words, and characters of a file (a mini `wc`), streaming it line by line.

<details>
<summary>Show a worked solution</summary>

```python
lines = words = chars = 0
with open("app.log", encoding="utf-8") as f:
    for line in f:
        lines += 1
        words += len(line.split())
        chars += len(line)
print(lines, words, chars)
```

```text
$ python3 miniwc.py app.log
1200 9541 68302
$ wc app.log
1200 9541 68302 app.log
```
</details>

**Exercise 3.** Append a timestamped entry to `activity.log` each time the script runs; run it twice and show the file keeps both entries.

<details>
<summary>Show a worked solution</summary>

```python
from datetime import datetime

with open("activity.log", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now().isoformat(timespec='seconds')} ran\n")
```

```text
$ python3 logrun.py && python3 logrun.py && cat activity.log
2024-10-10T03:14:15 ran
2024-10-10T03:14:17 ran
```
</details>

## Check Yourself

**What does opening an existing file with mode `"w"` do before you write anything?**

<details>
<summary>Show answer</summary>

It truncates the file to zero bytes immediately. To keep existing content, use `"a"` (append) or read first.
</details>

**Why prefer `for line in f` over `f.readlines()` for logs?**

<details>
<summary>Show answer</summary>

The loop reads one line at a time (constant memory), while `readlines()` loads the whole file as a list - fatal on multi-GB logs.
</details>

**Which exceptions does `open` raise for a missing file and for a permission problem?**

<details>
<summary>Show answer</summary>

`FileNotFoundError` and `PermissionError`, respectively.
</details>
