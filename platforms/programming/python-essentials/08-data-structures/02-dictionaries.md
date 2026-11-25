# Dictionaries

## Learning Objectives

- Store and retrieve key-value data with dicts, and handle missing keys safely.
- Count and group data - the two jobs dicts do better than anything else.
- Know what can be a key and how dict views and iteration behave.

## Introduction

A dictionary maps **keys to values** - the structure behind counts, lookups, configuration, and JSON. Lookup by key is O(1) on average:

```python
services = {22: "ssh", 80: "http", 443: "https"}
print(services[443])            # https
services[53] = "dns"            # insert or overwrite
del services[80]                # remove
print(22 in services)           # True - tests KEYS
```

Reading a missing key raises `KeyError`. The safe forms:

```python
services.get(25)                # None - no exception
services.get(25, "unknown")     # 'unknown' - custom default
name = services.setdefault(3306, "mysql")   # insert if missing, then return
```

Keys must be **hashable**: strings, numbers, tuples (of hashables) work; lists and dicts do not.

## Counting and Grouping

Counting occurrences is the single most common dict pattern in log analysis:

```python
counts = {}
for line in open("app.log"):
    if "Failed password" in line:
        user = line.rsplit(" for ", 1)[-1].strip()
        counts[user] = counts.get(user, 0) + 1
print(counts)   # {'admin': 12, 'root': 31, 'alice': 2}
```

Two refinements from the standard library:

```python
from collections import Counter, defaultdict

counts = Counter(usernames)          # one line; counts.most_common(3) ranks
by_status = defaultdict(list)        # missing key auto-creates an empty list
by_status[code].append(url)
```

Grouping - collecting items under a category - is the same pattern with lists as values, and `defaultdict(list)` removes the `setdefault` ceremony.

## Iteration and Views

```python
for port in services:                # keys (insertion order, guaranteed)
    ...
for port, name in services.items():  # pairs
    ...
list(services.keys()); list(services.values())
```

Since Python 3.7, dicts preserve insertion order. Changing a dict's size *while iterating it* raises `RuntimeError`; iterate over `list(services)` when deleting entries. `keys()`, `values()`, and `items()` return live views that reflect later changes.

Merging and building:

```python
defaults = {"timeout": 3, "retries": 2}
config = {**defaults, "retries": 5}   # later wins -> {'timeout': 3, 'retries': 5}
squares = {n: n * n for n in range(4)}  # dict comprehension
```

## Common Mistakes

- `services[25]` on a key that might not exist; use `.get()` when absence is normal.
- Forgetting `in` tests keys, not values.
- Using a list or dict as a key (`TypeError: unhashable type`) - use a tuple for compound keys.
- Mutating a dict during iteration over the dict itself.

## Key Takeaways

- Dicts map hashable keys to values with O(1) lookup; `.get()` and `setdefault()` handle missing keys gracefully.
- `counts[k] = counts.get(k, 0) + 1` counts; `defaultdict(list)` groups; `Counter` does both faster.
- Iteration yields keys in insertion order; `.items()` yields pairs; never resize a dict mid-loop.

## Practice Exercises

**Exercise 1.** Count word frequencies in `"the cat sat on the mat the cat ran"` and print the two most common words with their counts.

<details>
<summary>Show a worked solution</summary>

```python
from collections import Counter

words = "the cat sat on the mat the cat ran".split()
counts = Counter(words)
print(counts.most_common(2))
```

```text
[('the', 3), ('cat', 2)]
```

Without Counter: `counts[w] = counts.get(w, 0) + 1` in a loop.
</details>

**Exercise 2.** Given log entries like `"200 /index"`, `"404 /admin"`, `"200 /about"`, group paths by status code into a dict of lists.

<details>
<summary>Show a worked solution</summary>

```python
from collections import defaultdict

entries = ["200 /index", "404 /admin", "200 /about"]
by_status = defaultdict(list)
for entry in entries:
    code, path = entry.split()
    by_status[code].append(path)
print(dict(by_status))
```

```text
{'200': ['/index', '/about'], '404': ['/admin']}
```
</details>

**Exercise 3.** Merge `{"a": 1, "b": 2}` and `{"b": 99, "c": 3}` so the second dict wins on conflicts, without mutating either original.

<details>
<summary>Show a worked solution</summary>

```python
first = {"a": 1, "b": 2}
second = {"b": 99, "c": 3}
merged = {**first, **second}
print(merged)   # {'a': 1, 'b': 99, 'c': 3}
print(first)    # {'a': 1, 'b': 2} - untouched
```
</details>

## Check Yourself

**What happens on `d[missing_key]`, and what does `d.get(missing_key, default)` do instead?**

<details>
<summary>Show answer</summary>

Indexing raises `KeyError`; `.get()` returns the default (or `None` if none is given) without raising.
</details>

**Which types can serve as dict keys?**

<details>
<summary>Show answer</summary>

Hashable (immutable) types: strings, numbers, tuples containing hashables. Lists, dicts, and sets cannot.
</details>

**What does `for k in d:` iterate over?**

<details>
<summary>Show answer</summary>

The keys, in insertion order. Use `d.items()` for key-value pairs and `d.values()` for values only.
</details>
