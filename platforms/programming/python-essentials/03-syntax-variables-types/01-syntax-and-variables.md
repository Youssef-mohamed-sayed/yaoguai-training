# Syntax, Variables, and Assignment

## Learning Objectives

- Read and write Python's block structure: indentation, colons, and comments.
- Assign and reassign variables, and follow Python's naming rules and conventions.
- Understand assignment as name-binding, not copying.

## Introduction

Python's most visible design decision is that **indentation is syntax**. Where other languages wrap blocks in braces, Python uses a colon followed by a consistently indented block:

```python
attempts = 3

if attempts > 2:
    print("many attempts")   # inside the if-block
    print("still inside")    # same indentation level
print("always runs")         # back at the top level
```

```text
many attempts
still inside
always runs
```

The convention is **4 spaces per level**, and mixing tabs with spaces is an error in Python 3. Any decent editor inserts 4 spaces when you press Tab; configure yours once and never think about it again. Comments start with `#` and run to the end of the line.

## Variables Are Names Bound to Objects

Assignment with `=` binds a name to an object. It does not copy anything:

```python
ports = [22, 80, 443]
services = ports          # both names refer to the SAME list
services.append(8080)
print(ports)              # [22, 80, 443, 8080] - changed too!
```

```text
[22, 80, 443, 8080]
```

`services` is not a copy; it is a second label on the same list. Mutating through one name is visible through the other. To get an independent copy of a list, use `ports.copy()` or `ports[:]`.

This model explains a classic surprise:

```python
a = 500
b = a
b = b + 1
print(a)   # 500 - ints are immutable, so b = b + 1 binds b to a NEW object
```

Numbers, strings, and tuples are immutable, so "changing" them actually creates a new object and rebinds the name. Lists and dictionaries are mutable, so methods like `.append()` change the object in place. Knowing which is which prevents most aliasing bugs.

## Naming Rules and Conventions

Rules (the interpreter enforces these):

- Letters, digits, and underscore; cannot start with a digit.
- Case-sensitive: `port` and `Port` are different names.
- Reserved keywords (`if`, `for`, `class`, `import`, ...) cannot be names.

Conventions (the community enforces these, and tools like linters check them):

- `snake_case` for variables and functions: `failed_logins`, `parse_log`.
- `UPPER_SNAKE` for constants: `MAX_RETRIES = 5`.
- `CapWords` for classes (module 08+).
- Never shadow built-ins: naming a variable `list`, `str`, or `id` breaks that built-in for the rest of the scope and produces deeply confusing errors.

Multiple assignment and swapping are pleasantly direct:

```python
host, port = "scanme.nmap.org", 80
a, b = b, a          # swap without a temp variable
```

## Common Mistakes

- Inconsistent indentation, especially after pasting code. Python raises `IndentationError` or, worse, silently runs the line in the wrong block.
- Expecting `b = a` to copy a list, then "fixing" data through one name and corrupting it through the other.
- Long lines of "clever" one-liners. Python culture values the boring, readable version.

## Key Takeaways

- Indentation defines blocks: 4 spaces, never mixed with tabs; `#` starts a comment.
- Assignment binds a name to an object; mutating a shared object is visible through every name bound to it.
- Use `snake_case`, avoid shadowing built-ins, and prefer readable code over clever code.

## Practice Exercises

**Exercise 1.** Predict the output, then run it:

```python
x = [1, 2, 3]
y = x
y.append(4)
print(x, y)
z = x[:]
z.append(5)
print(x, z)
```

<details>
<summary>Show answer</summary>

```text
[1, 2, 3, 4] [1, 2, 3, 4]
[1, 2, 3, 4] [1, 2, 3, 4, 5]
```

`y` is the same object as `x`, so the append shows through both. `z` is a shallow copy via slicing, so its append affects only `z`.
</details>

**Exercise 2.** Fix this script so it runs (two indentation problems):

```python
score = 90
if score >= 50:
print("passed")
  print("well done")
```

<details>
<summary>Show a worked solution</summary>

```python
score = 90
if score >= 50:
    print("passed")
    print("well done")
```

Both lines in the if-block need exactly 4 spaces.
</details>

**Exercise 3.** Write three lines that assign a host string, a port integer, and then swap two variables `a = "first"` and `b = "second"` in one line. Print all values.

<details>
<summary>Show a worked solution</summary>

```python
host = "scanme.nmap.org"
port = 80
a, b = "first", "second"
a, b = b, a
print(host, port, a, b)
```

```text
scanme.nmap.org 80 second first
```
</details>

## Check Yourself

**Why does modifying a list through one variable sometimes change what another variable "contains"?**

<details>
<summary>Show answer</summary>

Both names are bound to the same list object. Assignment never copies; only explicit copying (`.copy()`, slicing) creates an independent object.
</details>

**What is wrong with naming a variable `list`?**

<details>
<summary>Show answer</summary>

It shadows the built-in `list` type within that scope, so later calls like `list("abc")` fail with a confusing error.
</details>

**How many spaces per indentation level does the Python community standardize on?**

<details>
<summary>Show answer</summary>

4 spaces. The interpreter accepts other consistent widths, but 4 spaces is the near-universal standard (PEP 8).
</details>
