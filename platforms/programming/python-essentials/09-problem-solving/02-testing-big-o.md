# Testing Basics and Big-O Thinking

## Learning Objectives

- Test functions with assertions and a case matrix (normal, boundary, invalid).
- Estimate how a solution scales using big-O notation.
- Choose the simpler algorithm when it is fast enough, and know when it is not.

## Introduction

"Works on my input" is not tested. A minimal testing habit has two parts: **assertions** that check expected results automatically, and a **case matrix** that covers normal, boundary, and invalid inputs.

```python
def is_valid_port(p):
    return isinstance(p, int) and 1 <= p <= 65535

cases = [
    (22, True),       # normal
    (1, True),        # lower boundary
    (65535, True),    # upper boundary
    (0, False),       # just outside
    (65536, False),
    ("443", False),   # wrong type
]
for given, expected in cases:
    assert is_valid_port(given) == expected, f"failed for {given!r}"
print("all tests passed")
```

```text
all tests passed
```

Run the file; silence-free output means every case passed. Real projects graduate to `pytest` (same asserts, nicer reports, auto-discovery of `test_*.py` files), but the habit starts here: **write the cases before or right after the function, and keep them.**

## Big-O: How Cost Grows

Big-O describes how runtime or memory grows with input size n:

| Notation | Name | Example |
| --- | --- | --- |
| O(1) | constant | dict/set lookup, list append |
| O(log n) | logarithmic | binary search in a sorted list |
| O(n) | linear | one pass over a list, `in` on a list |
| O(n log n) | linearithmic | good sorting (`sorted`) |
| O(n^2) | quadratic | comparing every item with every other |

```python
# O(n^2): does any pair sum to target?
def pair_sum_slow(items, target):
    for a in items:
        for b in items:
            if a + b == target:
                return True
    return False

# O(n): the same answer with a set
def pair_sum_fast(items, target):
    seen = set()
    for a in items:
        if target - a in seen:
            return True
        seen.add(a)
    return False
```

At n = 100 the difference is invisible. At n = 1,000,000 the quadratic version does ~10^12 operations (hours) while the set version does ~10^6 (a blink). Log files, packet captures, and password lists reach those sizes casually, which is why the instinct matters for security tooling.

## Rules of Thumb

1. **Make it correct, then make it fast** - and only if measurement says it is slow (`time.perf_counter()` around the hot part).
2. Replacing a list with a set or dict for lookups is the most common real-world optimization.
3. Nested loops over the same data are the quadratic smell; ask whether a set, dict, or sort kills the inner loop.
4. Reading a whole file when you could stream it line by line is an O(n) memory choice that bites first.

## Common Mistakes

- Testing only the happy path; boundary values (0, 1, empty, max) and wrong types are where bugs live.
- Optimizing before measuring, and making the code worse for no real gain.
- Quadratic loops over large logs "because it worked on the sample."

## Key Takeaways

- Assert expected results over a matrix of normal, boundary, and invalid cases; keep the tests next to the code.
- Big-O ranks growth: prefer O(1)/O(n) structures (dict, set) for lookups; beware nested loops over the same data.
- Measure before optimizing; simple and correct beats clever and fast.

## Practice Exercises

**Exercise 1.** Write a case matrix (at least 5 cases: normal, two boundaries, invalid, wrong-type) for a function `def clamp(x, lo, hi)` that pins x into [lo, hi], then implement it so all cases pass.

<details>
<summary>Show a worked solution</summary>

```python
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

cases = [
    ((5, 1, 10), 5),     # normal
    ((1, 1, 10), 1),     # lower boundary
    ((10, 1, 10), 10),   # upper boundary
    ((-3, 1, 10), 1),    # below
    ((99, 1, 10), 10),   # above
]
for (x, lo, hi), expected in cases:
    assert clamp(x, lo, hi) == expected
print("all tests passed")
```
</details>

**Exercise 2.** What is the big-O of `"x" in my_list` inside a `for` loop over n items? Rewrite the pattern to be O(n) overall.

<details>
<summary>Show a worked solution</summary>

Each `in` on a list is O(n), inside an n-iteration loop gives O(n^2). Convert once:

```python
targets = set(target_list)     # O(n) once
for item in items:             # O(n) loop with O(1) lookups
    if item in targets:
        ...
```
</details>

**Exercise 3.** Time `pair_sum_slow` and `pair_sum_fast` on `list(range(2000))` with target 3999 using `time.perf_counter()` and report both durations.

<details>
<summary>Show a worked solution</summary>

```python
import time

items = list(range(2000))
for fn in (pair_sum_slow, pair_sum_fast):
    start = time.perf_counter()
    fn(items, 3999)
    print(fn.__name__, round(time.perf_counter() - start, 4), "s")
```

```text
pair_sum_slow 0.1821 s
pair_sum_fast 0.0001 s
```

Exact numbers vary; the gap of ~1000x is the lesson.
</details>

## Check Yourself

**Why include boundary and invalid cases in a test matrix?**

<details>
<summary>Show answer</summary>

Bugs concentrate at edges: off-by-one at limits, wrong types, empty input. Happy-path tests rarely catch them.
</details>

**What is the big-O of sorting with Python's `sorted()`?**

<details>
<summary>Show answer</summary>

O(n log n) - Timsort, which is why "sort first, then binary-search or merge" often beats quadratic scans.
</details>

**What is the first thing to do before optimizing slow code?**

<details>
<summary>Show answer</summary>

Measure it (e.g. with `time.perf_counter()` or a profiler) so effort goes to the actual bottleneck, not a guessed one.
</details>
