# Raising Exceptions and Custom Errors

## Learning Objectives

- Signal failures from your own code with `raise`.
- Design small custom exception classes for a module or tool.
- Chain exceptions to preserve root causes.

## Introduction

So far you caught exceptions; this lesson is about producing them. Functions signal "I cannot do what you asked" with `raise`, which is more useful than returning `None` or -1 because it cannot be silently ignored and it carries a message and type:

```python
def parse_port(text):
    """Return text as a valid TCP/UDP port number."""
    try:
        port = int(text)
    except ValueError:
        raise ValueError(f"port must be numeric, got {text!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"port out of range: {port}")
    return port
```

Callers now get one clear contract: a valid port or a `ValueError` explaining exactly why not. The `from None` hides the internal `int()` traceback so the caller sees only the message meant for them.

## Custom Exception Classes

When a module can fail in several distinguishable ways, define your own exception types so callers can catch precisely:

```python
class ScanError(Exception):
    """Base class for scan failures."""

class HostUnreachable(ScanError):
    """The target did not respond."""

class ScanTimeout(ScanError):
    """The scan exceeded its time budget."""
```

```python
def ping(host):
    if not reachable(host):
        raise HostUnreachable(f"no response from {host}")

try:
    ping("10.0.0.99")
except ScanTimeout:
    print("too slow, skipping")
except ScanError as error:      # catches HostUnreachable too - it is a subclass
    print("scan failed:", error)
```

Subclassing a common base lets callers choose granularity: catch the specific case, the family, or let it propagate. Built-in exceptions work the same way (`FileNotFoundError` is a subclass of `OSError`).

## Chaining: Keeping the Root Cause

When you convert a low-level error into a higher-level one, keep the original attached:

```python
class ConfigError(Exception):
    pass

def load_config(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as error:
        raise ConfigError(f"cannot load config {path}") from error
```

The traceback then shows both: "The above exception was the direct cause of the following exception" - the operator sees your clear message *and* the underlying `PermissionError`. Use `from error` to chain, `from None` to deliberately hide internals.

## Common Mistakes

- Returning sentinel values (`None`, `-1`, `"error"`) that callers forget to check; `raise` cannot be ignored by accident.
- Raising generic `Exception("message")` everywhere, which forces callers into `except Exception` - the blanket catch from lesson 1.
- Losing the root cause by raising a new exception without `from`.

## Key Takeaways

- `raise SomeError("clear message")` signals failure at the exact point it is detected.
- Custom exception classes under a shared base let callers catch at the granularity they need.
- `raise NewError(...) from error` preserves the root cause; `from None` hides internals on purpose.

## Practice Exercises

**Exercise 1.** Write `require_even(n)` that returns `n` if even and raises `ValueError` with a message otherwise. Test both paths.

<details>
<summary>Show a worked solution</summary>

```python
def require_even(n):
    if n % 2:
        raise ValueError(f"{n} is not even")
    return n

print(require_even(4))        # 4
try:
    require_even(7)
except ValueError as e:
    print("caught:", e)       # caught: 7 is not even
```
</details>

**Exercise 2.** Define `AuthError(Exception)` with subclasses `BadPassword` and `AccountLocked`. Write `login(user, pw)` that raises `AccountLocked` for user "locked" and `BadPassword` for any password other than "s3cret", then catch them separately.

<details>
<summary>Show a worked solution</summary>

```python
class AuthError(Exception):
    pass

class BadPassword(AuthError):
    pass

class AccountLocked(AuthError):
    pass

def login(user, pw):
    if user == "locked":
        raise AccountLocked(f"{user} is locked out")
    if pw != "s3cret":
        raise BadPassword("wrong password")
    return True

for user, pw in (("locked", "x"), ("alice", "nope"), ("alice", "s3cret")):
    try:
        login(user, pw)
        print(user, "logged in")
    except AccountLocked as e:
        print(user, "locked:", e)
    except BadPassword as e:
        print(user, "failed:", e)
```

```text
locked locked: locked is locked out
alice failed: wrong password
alice logged in
```
</details>

**Exercise 3.** Convert a failing `int()` into a `ConfigError("invalid worker count")` that preserves the original error, and read both parts of the traceback.

<details>
<summary>Show a worked solution</summary>

```python
class ConfigError(Exception):
    pass

def worker_count(text):
    try:
        return int(text)
    except ValueError as error:
        raise ConfigError("invalid worker count") from error

worker_count("many")
```

```text
Traceback (most recent call last):
  ...
ValueError: invalid literal for int() with base 10: 'many'

The above exception was the direct cause of the following exception:
...
ConfigError: invalid worker count
```
</details>

## Check Yourself

**Why is raising better than returning `None` to signal failure?**

<details>
<summary>Show answer</summary>

A returned sentinel can be ignored or mishandled silently; an exception forces the caller to deal with it or let the program stop with a clear traceback.
</details>

**What does `raise NewError(...) from error` add to the traceback?**

<details>
<summary>Show answer</summary>

Exception chaining: the original error is shown as the direct cause of the new one, preserving the root cause for debugging.
</details>

**Why give custom exceptions a shared base class?**

<details>
<summary>Show answer</summary>

Callers can catch a specific subclass when they handle one case, or the base class when they handle the whole family, without resorting to `except Exception`.
</details>
