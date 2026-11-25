# Course Review: From First print to Working Tools

## Learning Objectives

- Consolidate the course's core skills into one mental map.
- Identify which module owns which problem.
- Plan deliberate practice to lock the skills in.

## Introduction

You started with `print` and ended with port scanners, log analyzers, and verified backups. This review compresses the course into the decisions you will actually face at a keyboard: *which tool do I reach for, and why?*

## The Map

**Foundations (modules 01-05).** How Python runs (bytecode, REPL), scripts and arguments (`sys.argv`, exit codes), environments (venv + pip), variables and types, operators and branches. Decision it answers: *how do I structure and run code at all?*

**Flow and structure (modules 06-08).** `for`/`while` with `break`/`continue`/`else`, functions with clean signatures and scope discipline, and the four containers. Decision: *which loop and which structure fit this data?* The cheat sheet: list for ordered mutable, dict for lookup and counting, set for membership and diffs, tuple for fixed records.

**Method (module 09).** Input -> transform -> output; contracts before bodies; test matrices; big-O instincts. Decision: *how do I attack a problem I have never seen?*

**Data in and out (modules 10-14).** Files (streaming, `pathlib`, binary), exceptions as designed failure, imports and the `__main__` guard, HTTP with `requests`. Decision: *how does my program touch the world safely?*

**Networking and craft (modules 15-16).** Raw sockets, framing, clients and servers; reading code, hand-tracing, pdb, logging. Decision: *how do I work below the libraries and above the guesswork?*

**Application (modules 17-18).** Scanners, log parsers, baseline diffing, header inspection, and five small but complete tools. Decision: *how do these pieces compose into something useful?*

## Ten Lines You Should Be Able to Write From Memory

```python
for line in open(path, encoding="utf-8"): ...           # stream a file
counts[key] = counts.get(key, 0) + 1                     # count anything
sorted(d.items(), key=lambda kv: kv[1], reverse=True)    # rank by value
try:
    risky_call()
except SpecificError:                        # targeted handling
if __name__ == "__main__": main()                        # script structure
requests.get(url, timeout=5)                             # never without timeout
subprocess.run([cmd, arg], capture_output=True, text=True, timeout=60)
socket.create_connection((host, port), timeout=3)        # raw TCP
hashlib.sha256(p.read_bytes()).hexdigest()               # small-file hash
assert f(x) == expected                                  # always be testing
```

If any line is shaky, that module is your next hour of practice.

## Keeping the Skill

Skills decay without reps. The reliable maintenance loop:

1. **Rebuild from memory.** Pick a project (status checker, log analyzer) and rewrite it without looking. Diff against your original.
2. **Extend one tool a week.** A new flag, a CSV export, a concurrency bound - small scope, finished completely.
3. **Read one real codebase.** The `requests` source or a small CLI tool on GitHub; apply the three-pass method.
4. **CTF and practice platforms.** Bandit (Linux course), PicoCTF, and TryHackMe give legal, structured targets.

## Key Takeaways

- The course is one arc: run code, structure data, handle failure, touch the network, build tools.
- Ten idioms cover most daily scripting; drill whichever feels slow.
- Deliberate practice - rebuild, extend, read - keeps the skill alive.

## Practice Exercises

**Exercise 1.** Write from memory, then check: count word frequencies in a file and print the top 3.

<details>
<summary>Show a worked solution</summary>

```python
from collections import Counter

counts = Counter()
with open("text.txt", encoding="utf-8") as f:
    for line in f:
        counts.update(line.split())
print(counts.most_common(3))
```
</details>

**Exercise 2.** Without looking anything up, sketch the port-scanner main loop with a timeout. Then compare with module 17.

<details>
<summary>Show a worked solution</summary>

```python
import socket

for port in range(1, 1025):
    with socket.socket() as s:
        s.settimeout(0.5)
        if s.connect_ex((host, port)) == 0:
            print(port, "open")
```
</details>

**Exercise 3.** Explain out loud (or in writing) what each of the ten lines above does and when you would use it. Any hesitation marks your review target.

<details>
<summary>Show a worked solution</summary>

Example for line 3: "Sort a dict's items by value descending - I use it whenever a Counter or counts dict needs ranking, like top IPs in a log report." Write one of these sentences per line.
</details>

## Check Yourself

**Which container do you pick for "count events per category"?**

<details>
<summary>Show answer</summary>

A dict (or Counter): keys are categories, values are counts, updated with `.get(k, 0) + 1` or `Counter.update`.
</details>

**Which module's pattern answers "did anything change since yesterday"?**

<details>
<summary>Show answer</summary>

Module 17's automation lesson: snapshot, reviewed baseline, set/dict diff, report changes only.
</details>

**What are the three passes for reading unfamiliar code?**

<details>
<summary>Show answer</summary>

Purpose, flow, then detail - main() and docstrings first, function bodies last.
</details>
