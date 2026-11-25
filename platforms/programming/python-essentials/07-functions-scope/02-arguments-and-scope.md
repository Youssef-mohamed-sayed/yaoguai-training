# Arguments, Return Values, and Scope

## Learning Objectives

- Pass any number of positional or keyword arguments with `*args` and `**kwargs`.
- Return several values via tuples and unpack them at the call site.
- Predict how local, enclosing, and global names resolve (scope).

## Introduction

This lesson covers the remaining mechanics of functions: flexible argument lists, multiple return values, and where a name "lives." These show up constantly when you read library code or write utilities other functions build on.

## *args and **kwargs

Sometimes a function cannot know how many values it will receive:

```python
def summarize(*numbers):
    """Accept any count of positional values."""
    return sum(numbers), max(numbers), min(numbers)

total, high, low = summarize(3, 9, 4, 9, 1)
print(total, high, low)   # 26 9 1
```

`*numbers` gathers extra positional arguments into a tuple. `**options` gathers extra keyword arguments into a dict:

```python
def connect(host, **options):
    print("host:", host)
    for key, value in options.items():
        print(f"  {key} = {value}")

connect("web-1", port=443, tls=True, timeout=2)
```

```text
host: web-1
  port = 443
  tls = True
  timeout = 2
```

The names `args`/`kwargs` are convention; the stars do the work. You also use the stars at the call site to *spread* a collection into arguments: `f(*[1, 2, 3])` calls `f(1, 2, 3)`.

## Multiple Return Values

`return a, b, c` actually returns one tuple; callers unpack it:

```python
def parse_line(line):
    ip, _, status = line.partition(" ")
    return ip, status          # one tuple of two

ip, status = parse_line("10.0.0.5 200")
```

Unpacking fails loudly on a count mismatch, which is good - it means structure changes are caught early. If callers regularly ignore one value, name it `_`.

## Scope: Where Names Live

Names defined inside a function are **local** to it and vanish when it returns. Names at module top level are **global**. Reading follows the LEGB rule: Local, Enclosing, Global, Built-in - Python checks in that order:

```python
attempts = 0          # global

def try_login():
    attempts = 1      # creates a NEW local; the global is untouched
    print("inside:", attempts)

try_login()           # inside: 1
print("outside:", attempts)   # outside: 0
```

Assignment inside a function creates a local by default. To deliberately modify a global, declare `global attempts` first - but treat that as a design smell: passing values in as parameters and returning results keeps functions predictable and testable.

Closures are the useful side of scope: an inner function remembers the names from the function that created it.

```python
def make_checker(limit):
    def check(value):
        return value <= limit
    return check

under_1024 = make_checker(1024)
print(under_1024(443))    # True
print(under_1024(8080))   # False
```

`check` still sees `limit` after `make_checker` returned - that captured state is a closure, and it is how small configurable checkers get built without classes.

## Common Mistakes

- Assuming assignment inside a function updates the global; it shadows it instead. Use parameters and return values.
- `UnboundLocalError` from reading a name and assigning it later in the same function - Python marks it local for the whole function, so the earlier read fails.
- Overusing `*args/**kwargs` to dodge designing a real signature; explicit parameters document themselves.

## Key Takeaways

- `*args` and `**kwargs` collect variable arguments; stars also spread collections at call sites.
- Multiple returns are tuple packing/unpacking; name ignored values `_`.
- Assignment creates locals; read order is Local, Enclosing, Global, Built-in. Prefer parameters over `global`.

## Practice Exercises

**Exercise 1.** Write `average(*values)` that returns the mean of any number of numeric arguments, or `0` when called with none.

<details>
<summary>Show a worked solution</summary>

```python
def average(*values):
    if not values:
        return 0
    return sum(values) / len(values)

print(average(2, 4, 6))  # 4.0
print(average())         # 0
```
</details>

**Exercise 2.** Write `split_host("web-1:8443")` returning host and port as two values, defaulting the port to 443 when none is given. Unpack both at the call site.

<details>
<summary>Show a worked solution</summary>

```python
def split_host(target):
    host, sep, port = target.partition(":")
    return host, int(port) if sep else 443

print(split_host("web-1:8443"))  # ('web-1', 8443)
print(split_host("web-1"))       # ('web-1', 443)
```
</details>

**Exercise 3.** Predict the output, then run:

```python
count = 10
def bump():
    count = 5
    return count
print(bump(), count)
```

<details>
<summary>Show answer</summary>

```text
5 10
```

The assignment inside `bump` creates a local `count`; the global stays 10.
</details>

## Check Yourself

**What types do `*args` and `**kwargs` collect into?**

<details>
<summary>Show answer</summary>

A tuple for `*args`, a dict for `**kwargs`.
</details>

**What does `return a, b` actually return?**

<details>
<summary>Show answer</summary>

A single tuple `(a, b)`, which callers normally unpack in the same breath: `x, y = f()`.
</details>

**In what order does Python resolve a name inside a function?**

<details>
<summary>Show answer</summary>

Local, then enclosing function scopes, then module globals, then built-ins (LEGB).
</details>
