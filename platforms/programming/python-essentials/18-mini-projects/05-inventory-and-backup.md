# Project: Directory Inventory and Backup

## Learning Objectives

- Inventory a directory tree: sizes, types, and newest/oldest files.
- Create timestamped, verified backups of important files.
- Combine pathlib, hashing, and reporting into one maintenance tool.

## Introduction

The final project is the one you will actually run monthly: inventory a directory (what is here, how big, what changed) and back up the important parts with integrity verification. It stitches together pathlib (module 10), hashing (project 2), JSON state (project 3), and clean reporting.

## Part 1: Inventory

```python
from pathlib import Path

def inventory(root):
    files = [p for p in Path(root).rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    by_suffix = {}
    for p in files:
        by_suffix.setdefault(p.suffix.lower() or "(none)", []).append(p)
    print(f"{len(files)} files, {total / 1e6:.1f} MB under {root}")
    for suffix, group in sorted(by_suffix.items(), key=lambda kv: -len(kv[1]))[:8]:
        size = sum(p.stat().st_size for p in group)
        print(f"  {suffix:>8} {len(group):>5} files  {size / 1e6:>8.1f} MB")
    newest = max(files, key=lambda p: p.stat().st_mtime, default=None)
    if newest:
        print("newest:", newest)
```

```text
$ python3 inventory.py ~/Documents
412 files, 86.3 MB under /home/you/Documents
       .pdf   102 files      61.2 MB
      .docx    87 files      18.4 MB
       .png    55 files       4.1 MB
newest: /home/you/Documents/notes/todo.md
```

`rglob("*")` walks the tree; grouping by suffix with a dict of lists (module 08 pattern) shows where the space goes.

## Part 2: Verified Backup

Copy important files to a timestamped folder, then prove every copy matches its source:

```python
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def backup(sources, dest_root):
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = Path(dest_root) / f"backup-{stamp}"
    copied, failed = 0, 0
    for source in sources:
        src = Path(source)
        if not src.is_file():
            print(f"SKIP (missing): {src}")
            continue
        target = dest / src.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)              # preserves timestamps
        if digest(src) == digest(target):
            copied += 1
        else:
            failed += 1
            print(f"CORRUPT COPY: {src}")
    print(f"{copied} files backed up to {dest}" + (f", {failed} FAILED" if failed else ""))

backup(["/etc/ssh/sshd_config", str(Path.home() / ".bashrc")], Path.home() / "backups")
```

Verification is the difference between a backup and a pile of copies: hash source and destination immediately after copying. `shutil.copy2` preserves modification times, which later inventory runs will thank you for.

## Notes That Matter

- This is a *local* backup. Real backup doctrine is 3-2-1: three copies, two media, one off-site - this script is one building block.
- For large trees, `rsync -a --delete src/ dest/` does this better; knowing what it must do underneath makes you a competent user of it.
- Deduplication idea: name backup files by content hash so unchanged files never get stored twice (that is how real backup tools work).

## Common Mistakes

- Copying without verifying - silent truncation and disk errors turn backups into decor.
- Timestamped folders with local time that collide across timezones; UTC or fine-grained stamps avoid it.
- Recursively backing up the backup destination into itself. Exclude the destination path.

## Key Takeaways

- `rglob` + `stat()` + grouping answers "what is in this tree and how big is it."
- Verified copies (hash source and destination) make backups trustworthy; `shutil.copy2` preserves metadata.
- Timestamped destinations plus skip/fail reporting make the tool safe to run unattended.

## Practice Exercises

**Exercise 1.** Run the inventory on your home directory's smallest subfolder and identify the dominant file type.

<details>
<summary>Show a worked solution</summary>

Point `inventory()` at a small folder first (a full home scan is slow). The suffix table immediately shows where space goes - usually media or documents.
</details>

**Exercise 2.** Back up three files, then tamper with one destination copy by hand and explain how you would detect it on a later verification run.

<details>
<summary>Show a worked solution</summary>

Append a byte to one file under the backup folder, then re-hash both sides:

```python
for target in dest.glob("*"):
    print(target.name, digest(target))
```

The tampered file's digest no longer matches the source's - and had you stored the manifest (filename -> digest as JSON at backup time), a `verify` subcommand could check the whole set unattended.
</details>

**Exercise 3.** Store a `manifest.json` inside each backup folder mapping filename to digest, then write the verify function that re-hashes the backup and reports OK/CHANGED per file.

<details>
<summary>Show a worked solution</summary>

```python
import json

manifest = {t.name: digest(t) for t in dest.glob("*") if t.is_file()}
(dest / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def verify(backup_dir):
    backup_dir = Path(backup_dir)
    manifest = json.loads((backup_dir / "manifest.json").read_text())
    for name, expected in manifest.items():
        actual = digest(backup_dir / name)
        print(f"{'OK     ' if actual == expected else 'CHANGED'} {name}")
```
</details>

## Check Yourself

**Why hash the copy after `shutil.copy2`?**

<details>
<summary>Show answer</summary>

To catch write-time corruption (disk errors, truncation, interruption) immediately, instead of discovering it when restoring.
</details>

**What does `p.suffix.lower() or "(none)"` handle?**

<details>
<summary>Show answer</summary>

Files with no extension produce an empty suffix string; the `or` groups them under a readable label, and lowercasing merges `.JPG` with `.jpg`.
</details>

**Why must the backup destination be excluded when the source tree contains it?**

<details>
<summary>Show answer</summary>

Otherwise the backup copies itself recursively, ballooning until the disk fills.
</details>
