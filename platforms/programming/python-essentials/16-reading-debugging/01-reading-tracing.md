# Reading and Tracing Code

## Learning Objectives

- Read unfamiliar code top-down by purpose, not line by line.
- Trace execution by hand with a variable table.
- Use strategic prints to follow data through a program.

## Introduction

You will read more code than you write - inherited scripts, library internals, other people's tools. Reading well is a skill with a method, not a talent.

**Pass 1: purpose.** Read the docstrings, the `main()` function, and the names. Build a one-sentence answer to "what does this program do?" Do not read function bodies yet.

**Pass 2: flow.** Follow `main()` and note the functions it calls in order. Sketch the input-to-output pipeline: where data enters, what transforms it, where it leaves.

**Pass 3: detail.** Only now read individual function bodies, starting with the ones on the data's path. Skip error handling and rare branches on the first read.

## Hand-Tracing with a Variable Table

When a function misbehaves, execute it on paper. Columns are variables, rows are steps:

```python
def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
```

Tracing `dedupe_preserve_order(["b", "a", "b"])`:

| step | item | seen | result |
| --- | --- | --- | --- |
| 1 | "b" | {b} | [b] |
| 2 | "a" | {b, a} | [b, a] |
| 3 | "b" | (already in seen, skip) | [b, a] |

Return value: `["b", "a"]`. The table forces you to be the interpreter; wrong mental models show up immediately as rows you cannot explain.

## Strategic Printing

The fastest debugger is a well-placed print - used with intent, not sprayed everywhere:

```python
def count_by_ip(lines):
    counts = {}
    for i, line in enumerate(lines):
        ip = extract_ip(line)
        if ip is None:
            print(f"DEBUG line {i}: no IP in {line[:60]!r}")   # temporary
            continue
        counts[ip] = counts.get(ip, 0) + 1
    return counts
```

Rules that keep print-debugging useful:

- Print **labels and values** (`f"DEBUG {i=} {ip=}"` - the `=` specifier prints name and value together), not bare numbers you cannot attribute.
- Print at **boundaries**: where data enters a function, after each transformation.
- Mark temporary prints (`DEBUG` prefix) so they are trivial to find and remove - or use `logging` (module 16 lesson 2) from the start.

## Reading Error Output

Combine reading with the traceback skill from module 11: locate the failing line, then hand-trace backward to where the bad value was born. The error is where it *surfaced*; the bug is where the value went wrong - often several frames earlier.

## Common Mistakes

- Reading line 1 to line 500 in order and drowning; purpose first, details last.
- Tracing in your head instead of on paper for anything longer than five lines.
- Twenty unlabeled prints whose output cannot be told apart.
- Fixing the line the traceback names without checking where its inputs came from.

## Key Takeaways

- Read in passes: purpose, flow, then detail; let `main()` be your map.
- Hand-trace with a variable table when behavior is surprising.
- Print with labels at data boundaries, using `f"{var=}"`, and clean up after.

## Practice Exercises

**Exercise 1.** Hand-trace this on paper before running it, writing the table for `total`, `count`, and `value`:

```python
total, count = 0, 0
for value in [4, -1, 8, -2]:
    if value < 0:
        continue
    total += value
    count += 1
print(total, count)
```

<details>
<summary>Show answer</summary>

| step | value | total | count |
| --- | --- | --- | --- |
| 1 | 4 | 4 | 1 |
| 2 | -1 (skipped) | 4 | 1 |
| 3 | 8 | 12 | 2 |
| 4 | -2 (skipped) | 12 | 2 |

Output: `12 2` - the negatives never reach the accumulation lines.
</details>

**Exercise 2.** Add labeled debug prints to the `dedupe_preserve_order` function so each iteration shows the item and whether it was kept, then run it on `["x", "y", "x", "z", "y"]`.

<details>
<summary>Show a worked solution</summary>

```python
def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        keep = item not in seen
        print(f"DEBUG {item=} {keep=}")
        if keep:
            seen.add(item)
            result.append(item)
    return result

print(dedupe_preserve_order(["x", "y", "x", "z", "y"]))
```

```text
DEBUG item='x' keep=True
DEBUG item='y' keep=True
DEBUG item='x' keep=False
DEBUG item='z' keep=True
DEBUG item='y' keep=False
['x', 'y', 'z']
```
</details>

**Exercise 3.** A teammate's script crashes with `KeyError: 'admin'` inside `report(counts)`. Using the three-pass method, describe what you check first, second, and third.

<details>
<summary>Show a worked solution</summary>

First: confirm what the program does and what `report` expects (a dict of user to count). Second: trace where `counts` is built - which lines add keys, and why 'admin' might be read but never inserted (for example, a lookup with `counts["admin"]` before any `counts.get("admin", 0)` insertion). Third: read the exact failing function body and the construction site of the key. The bug is where the key should have been created, not where it was read.
</details>

## Check Yourself

**What are the three passes of reading unfamiliar code?**

<details>
<summary>Show answer</summary>

Purpose (docstrings, main, names), flow (the call and data pipeline), then detail (individual bodies, starting on the data path).
</details>

**What does `print(f"{ip=}")` output that `print(ip)` does not?**

<details>
<summary>Show answer</summary>

The variable name with its value (`ip='10.0.0.5'`), so output from many prints stays attributable.
</details>

**The traceback points at a line in `report()`. Where is the bug?**

<details>
<summary>Show answer</summary>

Not necessarily there - the traceback shows where the bad value surfaced; trace backward to where that value was created or should have been validated.
</details>
