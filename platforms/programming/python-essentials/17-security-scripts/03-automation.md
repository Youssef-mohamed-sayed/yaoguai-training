# Automating Security Tasks

## Learning Objectives

- Turn repeated manual checks into scheduled, logged scripts.
- Compare current state against a known-good baseline.
- Report only what changed - the core trick of useful automation.

## Introduction

The highest-value security scripts are rarely clever. They are the boring checks - has this file changed, are these the right users, did new services appear - run **every day without fail** and quiet unless something is wrong. This lesson builds the pattern: snapshot, baseline, diff, report.

## Pattern: Snapshot, Baseline, Diff

```python
import hashlib
import json
from pathlib import Path

def snapshot(paths):
    """Map each file path to its SHA-256 hex digest."""
    state = {}
    for path in paths:
        p = Path(path)
        if p.is_file():
            state[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return state

BASELINE = Path("baseline.json")

current = snapshot(["/etc/passwd", "/etc/ssh/sshd_config"])
if not BASELINE.exists():
    BASELINE.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print("baseline created - run again later to compare")
else:
    old = json.loads(BASELINE.read_text(encoding="utf-8"))
    for path in sorted(set(old) | set(current)):
        if path not in old:
            print(f"NEW:      {path}")
        elif path not in current:
            print(f"REMOVED:  {path}")
        elif old[path] != current[path]:
            print(f"MODIFIED: {path}")
```

```text
$ python3 watchfiles.py
baseline created - run again later to compare
$ python3 watchfiles.py        # after /etc/ssh/sshd_config changed
MODIFIED: /etc/ssh/sshd_config
```

The same shape works for users (`/etc/passwd` lines as a set), open ports (re-run the module-01 scanner and diff the sets), or installed packages (`dpkg -l` / `pip freeze` output). Set difference (`new - old`, `old - new`) answers "what appeared/disappeared" directly.

## Scheduling and Logging

A check nobody runs is nothing. Cron runs it daily; logging (module 16) keeps the evidence:

```text
# crontab -e
15 3 * * *  /home/you/venv/bin/python /home/you/watchfiles.py >> /home/you/watchfiles.log 2>&1
```

Design rules for unattended scripts:

1. **Silence is success.** Print only changes or errors; a daily "all good" email trains everyone to ignore it. (A weekly heartbeat is fine.)
2. **Fail loudly.** Catch exceptions at the top level and exit nonzero with a clear message, so cron mail or monitoring notices.
3. **State lives in one place.** Keep the baseline beside the script, version it, and treat unexpected baseline changes as their own finding.
4. **Timeouts everywhere.** An unattended script that hangs is an incident, not a check.

## Common Mistakes

- Diffing against a baseline that was never reviewed - you enshrined a compromised state as "good."
- Alerting on everything, so real changes drown in noise.
- No logging: the script fired at 3 AM, something happened, and nobody can reconstruct what.
- Hardcoded absolute paths that break when the repo moves; anchor with `Path(__file__).parent`.

## Key Takeaways

- Snapshot state, store a reviewed baseline, and diff with set/dict operations; report only changes.
- Hashing (SHA-256) detects content changes; set difference detects additions and removals.
- Cron plus logging makes checks durable: quiet on success, loud and nonzero on failure.

## Practice Exercises

**Exercise 1.** Create a baseline for two files you own, modify one, rerun, and confirm only that file is reported.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 watchfiles.py
baseline created - run again later to compare
$ echo "# comment" >> ~/.bashrc   # (or any file in the list)
$ python3 watchfiles.py
MODIFIED: /home/you/.bashrc
```
</details>

**Exercise 2.** Rewrite the file snapshot as a *user* snapshot: read `/etc/passwd` usernames into a set, store as JSON, and report NEW/REMOVED users on later runs.

<details>
<summary>Show a worked solution</summary>

```python
import json
from pathlib import Path

BASE = Path("users-baseline.json")
current = {line.split(":")[0] for line in Path("/etc/passwd").read_text().splitlines()}

if not BASE.exists():
    BASE.write_text(json.dumps(sorted(current)), encoding="utf-8")
    print("baseline created")
else:
    old = set(json.loads(BASE.read_text()))
    for user in sorted(current - old):
        print("NEW:", user)
    for user in sorted(old - current):
        print("REMOVED:", user)
```
</details>

**Exercise 3.** Add top-level error handling to the diff script: any unexpected exception prints "check failed" to stderr and exits with code 1.

<details>
<summary>Show a worked solution</summary>

```python
import sys

def main():
    ...  # snapshot/diff logic

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"check failed: {error}", file=sys.stderr)
        sys.exit(1)
```

The blanket catch is acceptable here because it is the last boundary, it logs, and it sets a failing exit code - not silent swallowing.
</details>

## Check Yourself

**Why report only differences instead of full state?**

<details>
<summary>Show answer</summary>

Attention is the scarce resource. A report of only changes keeps alerts meaningful; daily full dumps train people to ignore the tool.
</details>

**What does SHA-256 give you that file size and mtime do not?**

<details>
<summary>Show answer</summary>

Content integrity: same-size edits and timestamp-preserving changes still flip the digest.
</details>

**Why should an unattended check exit nonzero on error?**

<details>
<summary>Show answer</summary>

Schedulers and monitoring surface failures through exit codes; a script that "succeeds" while broken disables the check silently.
</details>
