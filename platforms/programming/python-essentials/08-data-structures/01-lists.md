# Lists

## Learning Objectives

- Create, index, slice, and mutate lists without aliasing surprises.
- Use the core list methods and know their costs.
- Choose between lists and other sequences for a task.

## Introduction

A list is an ordered, mutable sequence - the default container in Python. It holds anything, keeps insertion order, and allows duplicates:

```python
ports = [22, 80, 443, 8080]
ports.append(9000)        # add at end -> [22, 80, 443, 8080, 9000]
ports.insert(1, 21)       # insert at index -> [22, 21, 80, 443, 8080, 9000]
ports.remove(21)          # remove first matching VALUE
last = ports.pop()        # remove and return the last item -> 9000
ports.sort()              # in place -> [22, 80, 443, 8080]
print(len(ports), 443 in ports)   # 4 True
```

Indexing and slicing work exactly like strings (module 03): `ports[0]`, `ports[-1]`, `ports[1:3]`, `ports[::-1]`.

## Methods, Sorted vs sort, and Copies

Two operations have a "mutate in place" version and a "return a new one" version; mixing them up is a classic bug:

```python
ports = [8080, 22, 443]
ports.sort()          # mutates ports itself, returns None
ordered = sorted(ports)   # returns a NEW sorted list, ports untouched
backwards = sorted(ports, reverse=True)
by_length = sorted(["bbb", "a", "cc"], key=len)   # ['a', 'cc', 'bbb']
```

Assigning `ports = ports.sort()` wipes the list to `None` - `sort()` returns nothing. Similarly `list(reversed(x))` vs `x.reverse()`.

Other daily tools:

```python
ports.index(443)       # 2 - position of first match (ValueError if absent)
ports.count(22)        # how many times a value appears
", ".join(map(str, ports))   # '22, 443, 8080' for display
ports.clear()          # empty it
copy = ports[:]        # shallow copy - aliasing rules from module 03 apply
```

## Cost and Choosing Structures

Appending and popping at the end are O(1) - effectively instant. Inserting or deleting at the front is O(n) because everything shifts; if a script pops from the front in a hot loop, use `collections.deque`, which is O(1) at both ends. Membership tests (`x in big_list`) scan linearly; for frequent membership checks on large collections, a `set` is the right tool (next lessons).

```python
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")     # right end
print(queue.popleft())     # task-1 - fast from the left
```

## Common Mistakes

- `my_list = my_list.sort()` - destroys the list (`sort` returns `None`).
- Removing items while iterating (module 06); build a filtered list instead.
- Using a list for thousands of `in` checks per second; that is what sets are for.
- `*` replication of nested lists: `[[0] * 3] * 3` creates three references to the same inner row. Use a comprehension: `[[0] * 3 for _ in range(3)]`.

## Key Takeaways

- Lists are ordered and mutable; learn `append`, `insert`, `remove`, `pop`, `index`, `count`.
- `sort()`/`reverse()` mutate in place and return `None`; `sorted()`/`reversed()` return new sequences.
- End operations are O(1); front operations and membership scans are O(n) - reach for `deque` or `set` when that matters.

## Practice Exercises

**Exercise 1.** Start with `[443, 22, 80, 22]` and produce a sorted list of unique ports `[22, 80, 443]` using `set` and `sorted`.

<details>
<summary>Show a worked solution</summary>

```python
ports = [443, 22, 80, 22]
unique_sorted = sorted(set(ports))
print(unique_sorted)   # [22, 80, 443]
```
</details>

**Exercise 2.** Print the last two elements of a list without knowing its length, then the list reversed.

<details>
<summary>Show a worked solution</summary>

```python
items = ["a", "b", "c", "d"]
print(items[-2:])    # ['c', 'd']
print(items[::-1])   # ['d', 'c', 'b', 'a']
```
</details>

**Exercise 3.** Show the difference: call `.sort()` and `sorted()` on the same starting list and print both results and the original after each.

<details>
<summary>Show a worked solution</summary>

```python
a = [3, 1, 2]
b = a.copy()
r = a.sort()
print(a, r)      # [1, 2, 3] None - mutated, no return
r2 = sorted(b, reverse=True)
print(b, r2)     # [3, 1, 2] [3, 2, 1] - original kept, new list returned
```
</details>

## Check Yourself

**What does `list.sort()` return?**

<details>
<summary>Show answer</summary>

`None`. It sorts the list in place. Use `sorted(list)` when you need a sorted copy.
</details>

**What is the time cost of `x in my_list` and what structure makes it fast?**

<details>
<summary>Show answer</summary>

O(n) - every element may be checked. A `set` gives O(1) average membership tests.
</details>

**Why does `row = [0] * 3; grid = [row] * 3; grid[0][0] = 1` change all three rows?**

<details>
<summary>Show answer</summary>

`[row] * 3` stores three references to the same inner list, so mutating one "row" mutates the shared object. Build rows in a comprehension.
</details>
