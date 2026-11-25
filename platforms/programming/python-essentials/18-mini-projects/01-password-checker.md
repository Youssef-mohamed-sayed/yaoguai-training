# Project: CLI Password Strength Checker

## Learning Objectives

- Build a heuristic password checker with `getpass` input.
- Score multiple criteria and report them clearly.
- Handle secrets responsibly: never echo, log, or store them.

## Introduction

This project rates a password's *local* strength: length and character variety. Two rules are absolute: the password never appears on screen (use `getpass`, which hides typing), and it is never written to a file or log. A checker that leaks its input is worse than no checker.

Heuristics are not guarantees - a 16-character passphrase of random words beats `Tr0ub4dor&3`, and real strength checking includes breach lists (HaveIBeenPwned's k-anonymity API) and entropy estimates. This project builds the safe local core.

## The Build, Step by Step

**Step 1: criteria as data.** Each check is a label and a test:

```python
import getpass

def evaluate(password):
    return {
        "12+ characters": len(password) >= 12,
        "lowercase letter": any(c.islower() for c in password),
        "uppercase letter": any(c.isupper() for c in password),
        "digit": any(c.isdigit() for c in password),
        "symbol": any(not c.isalnum() for c in password),
        "not all one character": len(set(password)) > 1,
        "no whitespace": not any(c.isspace() for c in password),
    }
```

`any(...)` with a generator expression tests each character lazily and stops at the first success.

**Step 2: score and report.**

```python
def main():
    password = getpass.getpass("Password to evaluate: ")
    results = evaluate(password)
    passed = sum(results.values())       # bools sum as 1/0
    for label, ok in results.items():
        print(f"  {'OK     ' if ok else 'MISSING'} {label}")
    print(f"score: {passed}/{len(results)} -",
          "strong" if passed == len(results) else
          "fair" if passed >= 5 else "weak")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```text
Password to evaluate:
  OK      12+ characters
  OK      lowercase letter
  MISSING uppercase letter
  OK      digit
  OK      symbol
  OK      not all one character
  OK      no whitespace
score: 6/7 - fair
```

**Step 3: edge cases.** Empty input, all-spaces, and 200-character strings should all produce sensible output without crashing - add them to a test list and run through each.

## Extensions

- Entropy estimate: `len(pw) * log2(pool_size)` where the pool grows with each character class present.
- Reject the 10,000 most common passwords from a local wordlist file.
- Compare against a personal passphrase policy (e.g. 4+ words).

## Key Takeaways

- `getpass.getpass` reads secrets without echoing; never print or persist the password itself.
- Criteria-as-a-dict plus `sum(results.values())` makes scoring trivial and extensible.
- Heuristics guide users; they do not prove a password is safe.

## Practice Exercises

**Exercise 1.** Build the checker as shown and test it with a weak password, a strong one, and an empty one.

<details>
<summary>Show a worked solution</summary>

```text
Password to evaluate:            # (typed: abc)
  MISSING 12+ characters
  OK      lowercase letter
  MISSING uppercase letter
  MISSING digit
  MISSING symbol
  OK      not all one character
  OK      no whitespace
score: 2/7 - weak
```

Empty input: every `any()` is False and `len(set("")) == 0`, so it scores 0/7 weak without errors.
</details>

**Exercise 2.** Add a check rejecting passwords present in a local `common.txt` wordlist (one per line).

<details>
<summary>Show a worked solution</summary>

```python
from pathlib import Path

COMMON = set(Path("common.txt").read_text(encoding="utf-8").split())

def evaluate(password):
    checks = { ... }   # as before
    checks["not a common password"] = password.lower() not in COMMON
    return checks
```

Load the set once at module level; membership is O(1).
</details>

**Exercise 3.** Write assertions for `evaluate` covering: strong password passes all checks, `"aaaaaaaaaaaa"` fails "not all one character", `"with space"` fails "no whitespace".

<details>
<summary>Show a worked solution</summary>

```python
r = evaluate("Str0ng!Passw0rd")
assert all(r.values())
assert not evaluate("aaaaaaaaaaaa")["not all one character"]
assert not evaluate("with space1!A")["no whitespace"]
print("checker tests passed")
```
</details>

## Check Yourself

**Why `getpass` instead of `input()` for passwords?**

<details>
<summary>Show answer</summary>

`input()` echoes typed characters to the terminal (and scrollback); `getpass` hides them.
</details>

**How does `sum(results.values())` score the checks?**

<details>
<summary>Show answer</summary>

Dict values are booleans, and `True`/`False` behave as 1/0 in arithmetic, so the sum counts passed checks.
</details>

**Why is a local heuristic not proof of password safety?**

<details>
<summary>Show answer</summary>

It cannot know about breach lists, predictable patterns, or site-specific throttling; it only measures shape (length, variety).
</details>
