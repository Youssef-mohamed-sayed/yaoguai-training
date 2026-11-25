# Lab: Fix the Broken Code

## Learning Objectives

- Apply tracebacks, hand-tracing, and pdb to real bugs.
- Fix five classic bug species: syntax, name, type, logic, and off-by-one.
- Verify fixes with assertions, not vibes.

## Introduction

This lab is deliberately broken code. Each snippet has one or more bugs of a species you have met. For each: **predict** what it does wrong, **run** it to confirm, **fix** it, and **prove** the fix with a test. That loop - reproduce, diagnose, fix, verify - is the whole job.

## Bug 1: The Quiet Shadow

```python
def total_open(ports):
    total = 0
    for port in ports:
        total = port        # supposed to accumulate
    return total

print(total_open([22, 80, 443]))   # prints 443, expected 545
```

Diagnosis: `total = port` overwrites instead of accumulating. The symptom ("answer is the last item") points at the loop body.

Fix: `total += port`. Verify: `assert total_open([22, 80, 443]) == 545` and `assert total_open([]) == 0`.

## Bug 2: The Off-by-One

```python
def first_n(items, n):
    return [items[i] for i in range(1, n + 1)]

print(first_n(["a", "b", "c"], 2))   # IndexError
```

Diagnosis: `range(1, n + 1)` starts at 1 (skipping index 0) and reaches `n` (out of range for short lists). Hand-trace the indexes: for n=2 it touches 1 and 2, but "first 2" means indexes 0 and 1.

Fix: `return items[:n]` (slicing also tolerates n larger than the list). Verify with n = 0, 2, 10 on a 3-item list.

## Bug 3: The Wrong Type

```python
port = input("port: ")
if 1 <= port <= 65535:
    print("valid")
```

Diagnosis: `input` returns a string; comparing `int <= str` raises `TypeError` in Python 3. Even before that, `"80" <= "65535"` style comparisons would be lexicographic, not numeric.

Fix: convert and validate -

```python
raw = input("port: ")
if raw.isdigit() and 1 <= int(raw) <= 65535:
    print("valid")
```

Verify with `22`, `0`, `99999`, `abc`.

## Bug 4: The Mutable Default

```python
def add_finding(findings, found=[]):
    found.append(findings)
    return found

print(add_finding("xss"))     # ['xss']
print(add_finding("sqli"))    # ['xss', 'sqli']  <- remembers the last call!
```

Diagnosis: the default list is created once at definition time and shared (module 07).

Fix:

```python
def add_finding(finding, found=None):
    if found is None:
        found = []
    found.append(finding)
    return found
```

Verify: two fresh calls each return one item.

## Bug 5: The Unreachable Branch

```python
def severity(count):
    if count > 0:
        return "low"
    elif count > 10:
        return "high"
    return "none"
```

Diagnosis: branch order. Every count > 10 is also > 0, so "high" never fires. Hand-trace count = 50 to see it return "low".

Fix: test the strictest condition first (`count > 10` before `count > 0`). Verify: 0 -> "none", 5 -> "low", 50 -> "high".

## Verification Habit

Bundle the fixes with their tests so regressions announce themselves:

```python
assert total_open([22, 80, 443]) == 545
assert first_n(["a", "b", "c"], 2) == ["a", "b"]
assert first_n(["a"], 10) == ["a"]
assert add_finding("a") == ["a"] and add_finding("b") == ["b"]
assert severity(50) == "high"
print("all fixes verified")
```

## Key Takeaways

- Reproduce, diagnose (traceback + hand-trace), fix, then prove with assertions.
- The five species: overwrite-instead-of-accumulate, off-by-one, str/int confusion, mutable defaults, misordered branches.
- Keep the tests; the same bug families come back.

## Practice Exercises

**Exercise 1.** Fix: `def average(nums): return sum(nums) / len(nums)` crashes on an empty list. Decide the empty-case behavior yourself and test it.

<details>
<summary>Show a worked solution</summary>

```python
def average(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)

assert average([]) == 0
assert average([2, 4]) == 3.0
```

(Returning 0 is one defensible choice; raising ValueError with a message is another - the point is to decide explicitly.)
</details>

**Exercise 2.** This countdown never ends. Find why and fix it:

```python
n = 10
while n != 0:
    print(n)
    n -= 2
```

<details>
<summary>Show a worked solution</summary>

Starting at 10 and stepping by 2, `n` hits ..., 4, 2, 0 - actually that one terminates. The trap is `n -= 2` from an odd start (or `n -= 1` from a negative start): it skips 0 forever. Robust fix:

```python
n = 10
while n > 0:
    print(n)
    n -= 2
```

Inequalities as exit tests tolerate any start value.
</details>

**Exercise 3.** `greet` prints the wrong name. Explain and fix:

```python
def greet(name="world"):
    print("hello", name)

name = "alice"
greet()
```

<details>
<summary>Show a worked solution</summary>

The module-level `name = "alice"` is never passed in; the default `"world"` is used. Fix by passing it explicitly: `greet(name)`. Defaults only apply when the caller supplies nothing.
</details>

## Check Yourself

**Why does "the answer equals the last item" suggest an overwrite bug?**

<details>
<summary>Show answer</summary>

Because assignment inside the loop replaces the accumulator each pass, leaving only the final iteration's value - accumulation requires `+=` (or append).
</details>

**Why is `items[:n]` a better "first n" than a range-based index loop?**

<details>
<summary>Show answer</summary>

Slicing starts at 0 and tolerates n beyond the list length - no off-by-one and no IndexError.
</details>

**What is the verification step after each fix in this lab?**

<details>
<summary>Show answer</summary>

An assertion (or case matrix) covering the original failing input plus boundaries, kept with the code so regressions surface immediately.
</details>
