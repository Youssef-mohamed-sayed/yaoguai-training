# Tuples and Sets

## Learning Objectives

- Use tuples for fixed records and understand immutability and unpacking.
- Use sets for membership, deduplication, and set algebra.
- Pick the right structure among list, tuple, and set for a given job.

## Introduction

Tuples and sets round out the built-in containers. A **tuple** is an ordered, immutable sequence; a **set** is an unordered collection of unique, hashable items with fast membership tests.

## Tuples: Fixed Records

```python
finding = ("10.0.0.5", 22, "ssh")
host, port, service = finding     # unpacking
print(port)                       # 22
pair = 1, 2                       # parentheses optional
single = (1,)                     # trailing comma REQUIRED for one item
```

Tuples communicate "this shape is fixed": a coordinate, a database row, a function returning host-plus-port. Immutability means no `append` or item assignment - but it also makes tuples hashable, so they can be dict keys and set members:

```python
connections = {("10.0.0.5", 22), ("10.0.0.5", 443), ("10.0.0.9", 22)}
counts = {("10.0.0.5", 22): 14}   # compound key
```

`namedtuple` (from `collections`) gives tuple fields names when plain indexes get cryptic:

```python
from collections import namedtuple
Finding = namedtuple("Finding", ["host", "port", "service"])
f = Finding("10.0.0.5", 22, "ssh")
print(f.service)   # ssh - self-documenting
```

## Sets: Uniqueness and Membership

```python
open_ports = {22, 80, 443, 80}
print(open_ports)        # {80, 22, 443} - duplicates dropped
open_ports.add(8080)
open_ports.discard(21)   # remove if present, no error if absent
print(443 in open_ports) # True - O(1) even for millions of entries
```

Set algebra reads like the math it is:

```python
scanned = {22, 80, 443, 8080}
expected = {22, 80, 443}
print(scanned & expected)   # {80, 22, 443}  intersection: in both
print(scanned | expected)   # union: in either
print(scanned - expected)   # {8080}  difference: unexpected extras
print(expected - scanned)   # set()  missing services
```

That difference pattern - "what appeared that I did not expect" - is exactly how you diff two scans, two user lists, or two firewall exports.

Sets are unordered: do not index them or rely on print order. Convert with `sorted(my_set)` when you need stable output.

## Choosing Among list, tuple, set

| Need | Use |
| --- | --- |
| Ordered collection that changes | `list` |
| Fixed-shape record, dict key | `tuple` |
| Membership tests, dedupe, set math | `set` |
| Key-value lookup | `dict` |

## Common Mistakes

- Writing `(1)` for a one-element tuple - that is just `1`; write `(1,)`.
- Expecting set order to be stable or meaningful.
- Putting a mutable list inside a set (`TypeError: unhashable type`) - use a tuple.
- Using a list for `in` checks inside a big loop when a set would be O(1).

## Key Takeaways

- Tuples are immutable ordered records; they unpack cleanly and can serve as dict keys.
- Sets deduplicate and answer membership in O(1); `&`, `|`, `-` perform diff-style analysis.
- Match the structure to the job; reach for `namedtuple` when positions lose meaning.

## Practice Exercises

**Exercise 1.** Given `scan1 = {22, 80, 443}` and `scan2 = {22, 25, 443}`, print ports that are new, closed since scan1, and common to both.

<details>
<summary>Show a worked solution</summary>

```python
print("new:", scan2 - scan1)       # new: {25}
print("closed:", scan1 - scan2)    # closed: {80}
print("common:", scan1 & scan2)    # common: {22, 443}
```
</details>

**Exercise 2.** Deduplicate `["a.example", "b.example", "a.example"]` while keeping alphabetical order.

<details>
<summary>Show a worked solution</summary>

```python
hosts = ["a.example", "b.example", "a.example"]
print(sorted(set(hosts)))
```

```text
['a.example', 'b.example']
```
</details>

**Exercise 3.** Store `("alice", "sudo")` and `("bob", "users")` tuples in a dict mapping username to group using unpacking in a loop.

<details>
<summary>Show a worked solution</summary>

```python
records = [("alice", "sudo"), ("bob", "users")]
groups = {}
for user, group in records:
    groups[user] = group
print(groups)   # {'alice': 'sudo', 'bob': 'users'}
```

(Or in one line: `dict(records)`.)
</details>

## Check Yourself

**Why can a tuple be a dict key but a list cannot?**

<details>
<summary>Show answer</summary>

Dict keys must be hashable, which requires immutability; tuples are immutable, lists are not.
</details>

**What does `set_a - set_b` give you?**

<details>
<summary>Show answer</summary>

The items present in `set_a` but absent from `set_b` - the difference, useful for "what changed" comparisons.
</details>

**How do you write a tuple containing only the number 5?**

<details>
<summary>Show answer</summary>

`(5,)` - the trailing comma is what makes it a tuple; `(5)` is just parenthesized 5.
</details>
