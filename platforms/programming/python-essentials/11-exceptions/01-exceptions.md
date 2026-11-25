# Handling Exceptions

## Learning Objectives

- Catch specific exceptions with `try`/`except` and structure `else`/`finally`.
- Read a traceback from the bottom up to find the real fault.
- Decide when to handle, when to convert, and when to let a crash happen.

## Introduction

An exception is how Python reports that something could not proceed: a missing file, a bad cast, a dropped connection. Unhandled, it kills the program with a **traceback**; handled well, it becomes a controlled fallback or a clean error message.

```python
try:
    port = int(input("Port: "))
except ValueError:
    print("that was not a number")
else:
    print(f"port {port} accepted")   # runs only if no exception
finally:
    print("(input step finished)")    # always runs
```

The shape rules:

- Catch **specific** exceptions (`ValueError`, `FileNotFoundError`), not everything.
- Keep the `try` block small - only the lines that can raise the exception you mean to catch.
- `else` holds code that needs the attempt to have succeeded; `finally` holds cleanup that must happen either way (closing resources, though `with` usually covers that).

## Reading a Traceback

```text
Traceback (most recent call last):
  File "scan.py", line 14, in <module>
    main()
  File "scan.py", line 9, in main
    count = int(fields[2])
IndexError: list index out of range
```

Read **bottom to top**: the last line says what happened (`IndexError`) and the line above shows where (`int(fields[2])` in `main`, line 9). The frames above it are the call chain that got there. The fix almost always belongs at the bottom frame, not the top.

## Common Exceptions You Will Meet

| Exception | Raised when |
| --- | --- |
| `ValueError` | right type, wrong value: `int("abc")` |
| `TypeError` | wrong type entirely: `"a" + 1` |
| `KeyError` | missing dict key |
| `IndexError` | sequence index out of range |
| `FileNotFoundError` | opening a path that does not exist |
| `PermissionError` | access denied |
| `ZeroDivisionError` | `1 / 0` |
| `ConnectionError`/`TimeoutError` | network failures (also `socket`/`requests` variants) |

## Handle, Convert, or Crash?

Three legitimate strategies:

1. **Handle and continue** when the failure is expected and survivable: skip a malformed log line, retry a flaky connection.
2. **Convert to a friendly message** at the program boundary: catch low-level errors and `sys.exit("could not read config: missing file")`.
3. **Let it crash** when the situation is a programming bug - you *want* the traceback during development. Silencing a bug makes it invisible, not fixed.

```python
# expected failure, handled locally
malformed = 0
for line in open("app.log"):
    try:
        code = int(line.split()[8])
    except (IndexError, ValueError):
        malformed += 1
        continue
```

The anti-pattern to avoid is the bare or blanket catch:

```python
try:
    everything()
except:            # or except Exception: with no logging
    pass           # errors vanish; bugs become unfindable
```

## Common Mistakes

- `except:` or `except Exception: pass` swallowing every error including the typo you just made.
- Wrapping twenty lines in `try`, so an unexpected error gets "handled" by the wrong `except`.
- Catching an exception and retrying forever with no backoff or limit.

## Key Takeaways

- `try`/`except SpecificError` small and targeted; `else` for success paths, `finally` for guaranteed cleanup.
- Tracebacks read bottom-up: last line is the fault, the line above it is the location.
- Handle expected failures, convert at boundaries, and let genuine bugs crash loudly.

## Practice Exercises

**Exercise 1.** Write a loop that asks for a number until the user enters a valid integer, printing a retry message on `ValueError`.

<details>
<summary>Show a worked solution</summary>

```python
while True:
    raw = input("Number: ")
    try:
        value = int(raw)
    except ValueError:
        print("not an integer, try again")
        continue
    break
print("got", value)
```

```text
Number: abc
not an integer, try again
Number: 12
got 12
```
</details>

**Exercise 2.** Parse `"host,port"` lines from a file, counting and skipping malformed lines without crashing.

<details>
<summary>Show a worked solution</summary>

```python
bad = 0
targets = []
for line in open("targets.txt"):
    try:
        host, port = line.strip().split(",")
        targets.append((host, int(port)))
    except ValueError:
        bad += 1
print(f"loaded {len(targets)}, skipped {bad} malformed")
```

Both unpacking failure and `int()` failure raise `ValueError`, so one handler covers the line's shape and content.
</details>

**Exercise 3.** Given the traceback from this lesson, state the exception type, the failing line number, and the function it occurred in.

<details>
<summary>Show answer</summary>

`IndexError: list index out of range`, at line 9 of scan.py, inside `main()`, on the expression `int(fields[2])`. `fields` had fewer than 3 elements, meaning the split produced fewer fields than the parser assumed.
</details>

## Check Yourself

**Why is `except Exception: pass` dangerous?**

<details>
<summary>Show answer</summary>

It hides every failure, including bugs you did not anticipate, making them silent and unfixable. Catch specific exceptions and log or act on them.
</details>

**What code belongs in the `else` block of a try statement?**

<details>
<summary>Show answer</summary>

Code that should run only when the `try` block raised nothing - keeping it out of `try` prevents accidentally catching its errors.
</details>

**When is letting a program crash the right choice?**

<details>
<summary>Show answer</summary>

When the exception signals a programming bug rather than an expected runtime condition - the traceback is valuable diagnostic information during development.
</details>
