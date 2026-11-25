# for Loops and range()

## Learning Objectives

- Iterate over sequences, files, and enumerations with `for`.
- Use `range`, `enumerate`, and `zip` to control what you loop over.
- Build transformed collections with comprehensions.

## Introduction

Python's `for` is a **for-each** loop: it visits each item of an iterable in order. There is no C-style `for (i=0; i<n; i++)` - when you need numbers, you iterate over a `range`:

```python
for port in (22, 80, 443):
    print("checking", port)

for i in range(3):        # 0, 1, 2
    print("attempt", i)

for i in range(10, 0, -2):  # 10, 8, 6, 4, 2
    print(i)
```

```text
checking 22
checking 80
checking 443
attempt 0
attempt 1
attempt 2
10
8
6
4
2
```

`range(start, stop, step)` excludes `stop` and is lazy: `range(10**9)` costs no memory because values are produced on demand.

## Looping with Index and in Parallel

Need the position as well as the value? Use `enumerate`, not a manual counter:

```python
hosts = ["web-1", "db-1", "vpn-gw"]
for i, host in enumerate(hosts, start=1):
    print(f"{i}. {host}")
```

```text
1. web-1
2. db-1
3. vpn-gw
```

Loop over two lists in lockstep with `zip`:

```python
ports = [22, 80, 443]
services = ["ssh", "http", "https"]
for port, service in zip(ports, services):
    print(f"{service} runs on {port}")
```

`zip` stops at the shorter input; `zip(strict=True)` raises instead if lengths differ.

## Iterating Dictionaries and Files

Dictionaries iterate keys by default; `.items()` gives pairs. Files iterate line by line without loading everything into memory:

```python
scores = {"alice": 9, "bob": 4}
for name, score in scores.items():
    print(name, score)

with open("app.log") as f:
    for line_number, line in enumerate(f, start=1):
        if "error" in line.lower():
            print(line_number, line.strip())
```

Line-by-line file iteration is the pattern behind every log analyzer in this course: it handles a 10 GB log in constant memory.

## Comprehensions

When a loop exists only to build a list, a comprehension says it in one expression:

```python
codes = [200, 301, 404, 500, 204]
errors = [c for c in codes if c >= 400]          # [404, 500]
labels = {c: ("error" if c >= 400 else "ok") for c in codes}
squares = [n * n for n in range(5)]               # [0, 1, 4, 9, 16]
```

Shape: `[expression for item in iterable if condition]`. Keep comprehensions to one idea; if the expression needs a second line or a nested condition tree, a plain loop is clearer.

## Common Mistakes

- Modifying a list while iterating over it (removing matches mid-loop skips elements). Build a new list with a comprehension instead.
- Writing `for i in range(len(hosts)): hosts[i]` when `for host in hosts:` or `enumerate` is available.
- Nesting comprehensions three deep to look clever. Nobody, including future you, will debug it happily.

## Key Takeaways

- `for` iterates items directly; `range(start, stop, step)` supplies number sequences and is lazy.
- `enumerate` adds positions, `zip` pairs sequences, files iterate line by line.
- Comprehensions turn "filter/transform into a new collection" loops into one readable expression.

## Practice Exercises

**Exercise 1.** Print the first 12 TCP ports as `port N` using `range`, starting at port 1 and including port 12.

<details>
<summary>Show a worked solution</summary>

```python
for n in range(1, 13):
    print("port", n)
```

`range(1, 13)` because the stop value is excluded.
</details>

**Exercise 2.** Given `paths = ["/admin", "/login", "/robots.txt"]` and `codes = [403, 200, 200]`, print `/admin -> 403`-style lines using `zip`.

<details>
<summary>Show a worked solution</summary>

```python
for path, code in zip(paths, codes):
    print(f"{path} -> {code}")
```

```text
/admin -> 403
/login -> 200
/robots.txt -> 200
```
</details>

**Exercise 3.** From `lines = ["ok", "ERROR disk", "ok", "Error net"]`, build a list containing only the error lines, uppercased, using a comprehension.

<details>
<summary>Show a worked solution</summary>

```python
errors = [line.upper() for line in lines if "error" in line.lower()]
print(errors)
```

```text
['ERROR DISK', 'ERROR NET']
```

The condition filters case-insensitively; the expression uppercases what survives.
</details>

## Check Yourself

**What values does `range(2, 10, 3)` produce?**

<details>
<summary>Show answer</summary>

2, 5, 8. It starts at 2, steps by 3, and stops before 10.
</details>

**Why prefer `enumerate(hosts)` over `range(len(hosts))`?**

<details>
<summary>Show answer</summary>

It gives index and value directly without manual indexing, is shorter, and works on any iterable, including ones with no len() or indexing.
</details>

**What is wrong with deleting items from a list inside a `for item in items:` loop over that same list?**

<details>
<summary>Show answer</summary>

Removal shifts positions while the iterator tracks an index, so the element after each removed one gets skipped. Build a filtered copy instead.
</details>
