# while Loops, break, and continue

## Learning Objectives

- Loop on a condition with `while` and guarantee termination.
- Control iteration with `break`, `continue`, and the loop `else`.
- Recognize and avoid infinite loops and off-by-one errors.

## Introduction

`for` answers "for each item"; `while` answers "as long as this holds." It re-checks its condition before every pass:

```python
retries = 3
while retries > 0:
    print("trying...")
    retries -= 1
print("giving up")
```

```text
trying...
trying...
trying...
giving up
```

Two patterns dominate real scripts:

1. **Retry with a budget** (above): count down attempts until success or exhaustion.
2. **Read until done**: loop until input, a socket, or a stream signals the end.

```python
while True:
    line = input("cmd> ")
    if line == "quit":
        break
    print("echo:", line)
```

`while True` plus a `break` on a clear exit condition is idiomatic for interactive loops - but only when the exit is obvious and reachable.

## break, continue, and the Loop else

- `break` leaves the loop immediately.
- `continue` skips to the next iteration.
- A loop's `else:` block runs **only if the loop finished without `break`**. This is the least-known Python feature and perfect for search loops:

```python
ports = [21, 22, 80, 443]
target = 23
for port in ports:
    if port == target:
        print("found:", port)
        break
else:
    print(target, "not in the list")
```

```text
23 not in the list
```

Without the loop-`else`, you would need a `found = False` flag. The same structure works on `while`.

A practical `continue` example - skip noise lines when parsing:

```python
for line in open("app.log"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue          # skip blanks and comments
    process(line)
```

## Termination and Defensive Loops

Every `while` needs an argument for why it must end. Ask: *what changes each iteration, and does the condition eventually become false?*

```python
# BUG: countdown never changes if n starts negative... and never changes at all here
n = 5
while n != 0:
    print(n)
    n -= 1
```

This one terminates for positive `n`, but `while n != 0` with `n -= 1` loops forever if `n` starts at -1 (it skips past 0). The robust form is `while n > 0:`. Prefer inequalities over exact-equality exit tests; they tolerate unexpected starting values.

For network and retry code, always bound the loop: a maximum attempt count or a deadline (`time.monotonic()`), plus `sleep` between tries so you do not hammer the target:

```python
import time

deadline = time.monotonic() + 10   # give up after 10 seconds
while time.monotonic() < deadline:
    if try_connect():
        break
    time.sleep(0.5)
else:
    print("host unreachable")
```

## Common Mistakes

- `while True` with no reachable `break` - the script hangs forever and has to be killed (Ctrl-C).
- Updating the loop variable on only some paths, so certain inputs loop forever.
- Using `!=` as the exit test where `<`/`>` would be safe against skipped values.
- Polling in a tight loop with no sleep, burning CPU and tripping rate limits.

## Key Takeaways

- `while` repeats while its condition holds; `while True` + `break` suits read-until-done loops.
- `break` exits, `continue` skips ahead, and loop `else` runs only when no `break` happened - ideal for search loops.
- Guarantee termination: something must move toward the exit each pass, inequalities beat equality tests, and external waits need a deadline.

## Practice Exercises

**Exercise 1.** Write a countdown from 5 to 1 with `while`, then print "liftoff". Make the exit test an inequality.

<details>
<summary>Show a worked solution</summary>

```python
n = 5
while n > 0:
    print(n)
    n -= 1
print("liftoff")
```

```text
5
4
3
2
1
liftoff
```
</details>

**Exercise 2.** Loop over `["# comment", "", "user=alice", "# note", "host=web-1"]`; skip comments and blanks with `continue`, and print only real settings.

<details>
<summary>Show a worked solution</summary>

```python
lines = ["# comment", "", "user=alice", "# note", "host=web-1"]
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    print("setting:", line)
```

```text
setting: user=alice
setting: host=web-1
```
</details>

**Exercise 3.** Search `[3, 7, 11, 18]` for the value 12 using a `for`/`else`; print "found" with the value or "missing" without a flag variable.

<details>
<summary>Show a worked solution</summary>

```python
values = [3, 7, 11, 18]
for v in values:
    if v == 12:
        print("found", v)
        break
else:
    print("missing")
```

```text
missing
```
</details>

## Check Yourself

**When does a loop's `else` block execute?**

<details>
<summary>Show answer</summary>

When the loop condition becomes false (or iteration exhausts) without any `break` having run. A `break` skips the `else`.
</details>

**Why is `while n > 0` safer than `while n != 0` for a decrementing counter?**

<details>
<summary>Show answer</summary>

If `n` ever starts negative or steps past zero, `!=` never becomes false and the loop runs forever. `>` terminates for any non-positive value.
</details>

**What does `continue` do inside a file-parsing loop?**

<details>
<summary>Show answer</summary>

It abandons the current line immediately and moves to the next iteration, leaving the lines below it (the real processing) unindented and clean.
</details>
