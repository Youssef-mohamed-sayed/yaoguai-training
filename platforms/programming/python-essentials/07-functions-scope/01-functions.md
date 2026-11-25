# Defining and Calling Functions

## Learning Objectives

- Define functions with parameters, defaults, and return values.
- Explain what a function returns when there is no `return`, and use docstrings.
- Decompose a script into small, testable functions.

## Introduction

A function packages a named, reusable piece of logic. Define with `def`, call with parentheses:

```python
def classify_port(port):
    if port == 22:
        return "ssh"
    if port == 80:
        return "http"
    if port == 443:
        return "https"
    return "unknown"

print(classify_port(22))    # ssh
print(classify_port(9000))  # unknown
```

`return` ends the function immediately and hands a value back; code after it in the same block never runs. A function with no `return` (or a bare `return`) gives back `None`:

```python
def log(msg):
    print("LOG:", msg)

result = log("scan started")
print(result)   # None
```

## Parameters, Defaults, and Keyword Calls

```python
def scan(host, ports=(80, 443), timeout=1.5):
    for port in ports:
        print(f"{host}:{port} (timeout {timeout}s)")

scan("web-1")                        # uses defaults
scan("web-1", (22, 80))              # positional
scan("web-1", timeout=3)             # keyword: readable, order-free
```

Rules that matter:

- Parameters with defaults must come after those without.
- Keyword arguments (`timeout=3`) document the call site; use them once a function takes more than two parameters.
- **Never use a mutable default.** `def f(items=[])` creates one list shared by every call:

```python
def bad(items=[]):
    items.append(1)
    return items

print(bad())  # [1]
print(bad())  # [1, 1] - same list remembered!

def good(items=None):
    if items is None:
        items = []
    items.append(1)
    return items

print(good())  # [1]
print(good())  # [1] - fresh list each time
```

## Docstrings and Small Functions

The first string inside a function is its docstring, surfaced by `help()`:

```python
def parse_status(line):
    """Extract the HTTP status code from a log line, or None."""
    ...
```

Functions should do one thing and fit on a screen. When a script grows, split it: one function to read input, one to transform, one to output. Each becomes testable in isolation and the main flow reads like a table of contents:

```python
def main():
    lines = read_lines("app.log")
    errors = find_errors(lines)
    report(errors)

main()
```

## Common Mistakes

- Printing inside a function that should return a value, so callers cannot reuse the result. Compute and `return`; let the caller print.
- The mutable-default trap (`def f(x=[])`).
- Calling `my_func` without parentheses and wondering why nothing happens - that references the function object; the call is `my_func()`.
- Giant 100-line functions that mix parsing, logic, and output.

## Key Takeaways

- `def` defines, `return` sends back exactly one object (or `None`); functions are values themselves.
- Default and keyword arguments make calls flexible; mutable defaults are a shared-state bug - use `None` and build inside.
- Docstrings document; small single-purpose functions keep scripts testable.

## Practice Exercises

**Exercise 1.** Write `is_valid_port(p)` that returns `True` for integers 1-65535 and `False` otherwise, then test it with 22, 0, 70000, and "abc" (wrap the call in try/except or check type first - your choice).

<details>
<summary>Show a worked solution</summary>

```python
def is_valid_port(p):
    return isinstance(p, int) and 1 <= p <= 65535

for p in (22, 0, 70000, "abc"):
    print(p, is_valid_port(p))
```

```text
22 True
0 False
70000 False
abc False
```
</details>

**Exercise 2.** Write `repeat(msg, times=2)` that returns `msg` joined by spaces `times` times. Show that `repeat("hi")` and `repeat("hi", 3)` both work.

<details>
<summary>Show a worked solution</summary>

```python
def repeat(msg, times=2):
    return " ".join([msg] * times)

print(repeat("hi"))     # hi hi
print(repeat("hi", 3))  # hi hi hi
```
</details>

**Exercise 3.** Demonstrate the mutable-default bug: call a `def track(items=[])` function twice and print the result both times. Then fix it with the `None` pattern.

<details>
<summary>Show a worked solution</summary>

```python
def track(items=[]):
    items.append("x")
    return items

print(track())  # ['x']
print(track())  # ['x', 'x']  <- bug: remembered

def track_fixed(items=None):
    if items is None:
        items = []
    items.append("x")
    return items

print(track_fixed())  # ['x']
print(track_fixed())  # ['x']   <- correct
```
</details>

## Check Yourself

**What does a function with no `return` statement give its caller?**

<details>
<summary>Show answer</summary>

`None`. Printing inside a function and returning a value are different things; only `return` hands data back.
</details>

**Why is `def f(items=[])` dangerous?**

<details>
<summary>Show answer</summary>

The default list is created once at definition time and shared by every call, so mutations accumulate across calls. Use `items=None` and create the list inside.
</details>

**What is the difference between `my_func` and `my_func()`?**

<details>
<summary>Show answer</summary>

The first is the function object itself (no code runs); the second calls it and evaluates to its return value.
</details>
