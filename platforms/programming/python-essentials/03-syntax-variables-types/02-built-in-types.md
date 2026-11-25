# Built-in Types: Numbers, Booleans, and None

## Learning Objectives

- Use Python's numeric types (`int`, `float`, `complex`) and know when each applies.
- Work with booleans and truthiness in conditions.
- Use `None` correctly and convert between types safely.

## Introduction

Python's core types cover most everyday data. This lesson covers the scalar ones: numbers, booleans, and the `None` sentinel. Strings get their own lesson next; lists, dictionaries, tuples, and sets come in module 08.

## Integers and Floats

Python integers are **arbitrary precision**: they never overflow, they just get slower when astronomically large:

```python
big = 2 ** 100
print(big)
```

```text
1267650600228229401496703205376
```

Floats are 64-bit IEEE 754, like `double` in C, and carry the classic rounding artifacts:

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
```

```text
0.30000000000000004
False
```

Never compare floats for equality; compare within a tolerance (`math.isclose(a, b)`), and use the `decimal` module for money.

Division is the operator that surprises people most:

```python
print(7 / 2)    # 3.5   - / always returns a float
print(7 // 2)   # 3     - floor division, discards the fraction
print(7 % 2)    # 1     - remainder (modulo)
print(2 ** 10)  # 1024  - exponent
```

`%` shows up constantly in scripting: `n % 2 == 0` tests even numbers, and `i % 10 == 0` triggers something every tenth iteration.

## Booleans and Truthiness

`True` and `False` are the only two booleans. Comparisons produce them: `==`, `!=`, `<`, `<=`, `>`, `>=`, plus membership (`in`) and identity (`is`):

```python
port = 22
print(port == 22)              # True
print("ssh" in ["ssh", "http"])  # True
```

Every value also has an implicit truth value. **Falsy** values: `False`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`. Everything else is truthy. Conditions use this directly:

```python
findings = []
if findings:
    print("issues found")
else:
    print("clean")   # empty list is falsy, so this prints
```

```text
clean
```

Prefer `if findings:` over `if len(findings) > 0:` - it is the idiomatic spelling.

## None and Type Conversion

`None` is the single "no value" object. Functions that return nothing actually return `None`. Test for it with `is`, never `==`:

```python
result = None
if result is None:
    print("nothing yet")
```

Converting between types is explicit:

```python
int("443")        # 443
int("443", 10)    # same, base 10; base 16 parses hex strings
float("3.5")      # 3.5
str(443)          # '443'
bool("")          # False
```

`int("12.5")` raises `ValueError` (it is not an integer literal); go through `float` first if the input might have a decimal point. `int("0x1F", 16)` and `int("1F", 16)` both give 31 - useful when parsing hex from dumps and protocol output.

## Common Mistakes

- Comparing floats with `==` and chasing ghosts; use `math.isclose`.
- Testing `if x == None` instead of `if x is None`. It often works, but `==` can be overridden by classes while `is` checks identity.
- Expecting `/` to behave like integer division; in Python 3 it always yields a float, so use `//` when you want an integer quotient.

## Key Takeaways

- `int` never overflows; `float` has rounding error, so compare with `math.isclose`.
- `/` always divides to a float; `//` floors, `%` gives the remainder, `**` raises to a power.
- Empty containers, zero, `""`, and `None` are falsy; test `None` with `is`, and convert types explicitly with `int()`, `float()`, `str()`.

## Practice Exercises

**Exercise 1.** Compute how many whole 1024-byte blocks fit in 10,000 bytes, and how many bytes remain, using `//` and `%`.

<details>
<summary>Show a worked solution</summary>

```python
total = 10000
block = 1024
print(total // block, "full blocks")
print(total % block, "bytes left over")
```

```text
9 full blocks
784 bytes left over
```
</details>

**Exercise 2.** Parse the hex string `"0xff"` into an integer, then print it back as binary with `bin()` and as hex with `hex()`.

<details>
<summary>Show a worked solution</summary>

```python
value = int("0xff", 16)
print(value)      # 255
print(bin(value)) # 0b11111111
print(hex(value)) # 0xff
```

Parsing hex and binary output is a daily operation when reading packet dumps and memory addresses.
</details>

**Exercise 3.** Write a condition that prints "empty" when a variable named `data` is any falsy value. Test it with `""`, `[]`, `0`, and `"x"`.

<details>
<summary>Show a worked solution</summary>

```python
for data in ("", [], 0, "x"):
    if not data:
        print(repr(data), "-> empty")
    else:
        print(repr(data), "-> has content")
```

```text
'' -> empty
[] -> empty
0 -> empty
'x' -> has content
```
</details>

## Check Yourself

**What does `7 / 2` evaluate to in Python 3, and what is its type?**

<details>
<summary>Show answer</summary>

`3.5`, a `float`. True division always returns a float, even when the operands divide evenly (`6 / 3` is `2.0`).
</details>

**Why is `0.1 + 0.2 == 0.3` False?**

<details>
<summary>Show answer</summary>

Binary floating point cannot represent 0.1 or 0.2 exactly, so the sum is 0.30000000000000004. Use `math.isclose()` for float comparisons.
</details>

**Which values in Python count as falsy?**

<details>
<summary>Show answer</summary>

`False`, `0`, `0.0`, empty string `""`, empty containers (`[]`, `{}`, `set()`), and `None`. Everything else is truthy.
</details>
