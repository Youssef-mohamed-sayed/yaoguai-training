# Operators and Expressions

## Learning Objectives

- Use arithmetic, comparison, membership, and identity operators correctly.
- Combine conditions with `and`, `or`, `not` and predict short-circuit behavior.
- Read operator precedence well enough to write unambiguous expressions.

## Introduction

An *expression* is anything Python can evaluate to a value: `2 + 3`, `port == 22`, `"error" in line`. Operators are the verbs. Most behave as you expect from math and other languages; this lesson focuses on the parts Python does differently and the combinations real scripts lean on.

## Arithmetic and Assignment

Beyond `+ - * / // % **` (previous lesson), the augmented forms update in place:

```python
total = 0
total += 5     # same as total = total + 5
retries = 3
retries -= 1
mask = 0b1100
mask |= 0b0011 # bitwise OR assignment -> 0b1111
```

Bitwise operators (`&`, `|`, `^`, `~`, `<<`, `>>`) matter in security work: subnet masks, file permission bits, flags packed into integers, and simple obfuscation all use them.

```python
0b1100 & 0b1010   # 0b1000  (8) - bits set in both
0b1100 | 0b1010   # 0b1110  (14) - bits set in either
0b1100 ^ 0b1010   # 0b0110  (6) - bits set in exactly one
1 << 4            # 16 - shift left multiplies by powers of two
```

## Comparison, Membership, Identity

```python
code = 404
200 <= code < 500     # True - chained comparison, reads like math
"admin" in ["root", "admin"]   # True - membership
"GET" not in "POST / HTTP"     # True
a = None
a is None             # True - identity, the correct None test
```

Two traps live here:

1. `==` compares *values*; `is` compares *identity* (same object). Use `is` only for singletons: `None`, `True`, `False`.
2. Chained comparisons are evaluated pairwise: `200 <= code < 500` means `(200 <= code) and (code < 500)`.

## Boolean Operators and Short-Circuiting

`and` returns the first falsy operand or the last value; `or` returns the first truthy operand or the last value. Evaluation stops as soon as the result is known - this is **short-circuiting**, and it has practical uses:

```python
# Only calls expensive_check() if cached is empty:
if not cached and expensive_check():
    ...

# Default value pattern:
name = supplied_name or "anonymous"

# Guard pattern: len(parts) is only evaluated when parts is non-empty
if parts and len(parts) > 2:
    ...
```

Without short-circuiting, `len(parts) > 2` would still run on an empty list. With it, the guard and the use sit safely in one expression. `not` flips truthiness and always returns a real boolean.

## Precedence: When in Doubt, Parenthesize

The rough order, highest first: `**` → unary `-`, `not` → `* / // %` → `+ -` → comparisons, `in`, `is` → `and` → `or`. So:

```python
2 + 3 * 4          # 14, not 20
not 1 in [1, 2]    # False: parsed as not (1 in [1, 2])
True or False and False  # True: 'and' binds tighter than 'or'
```

Nobody memorizes the whole table. Write `a and (b or c)` when grouping matters; the parentheses cost nothing and save the next reader a bug.

## Common Mistakes

- Writing `if port == 22 or 80:` - this is always truthy because `80` is truthy. Say `if port in (22, 80):`.
- Using `is` to compare strings or numbers. CPython interns some small values so it *appears* to work, then fails on other values. Values: `==`. Identity: `is`.
- Forgetting that `and`/`or` return operands, not booleans: `"" or 0` is `0`, not `False`. Wrap in `bool()` if you need a strict boolean.

## Key Takeaways

- Augmented assignment (`+=`, `|=`) updates variables concisely; bitwise operators unpack flags and masks.
- `==` for values, `is` for `None`/singletons, `in` for membership; chained comparisons read like math.
- `and`/`or` short-circuit, enabling guard and default-value patterns; parenthesize mixed boolean logic.

## Practice Exercises

**Exercise 1.** A firewall flag byte uses bit 0 for "log", bit 1 for "block", bit 2 for "alert". Given `flags = 0b101`, test each bit and print which actions are enabled.

<details>
<summary>Show a worked solution</summary>

```python
flags = 0b101
if flags & 0b001:
    print("log enabled")
if flags & 0b010:
    print("block enabled")
if flags & 0b100:
    print("alert enabled")
```

```text
log enabled
alert enabled
```

`flags & mask` is nonzero (truthy) exactly when that bit is set.
</details>

**Exercise 2.** Rewrite `if port == 21 or port == 22 or port == 23:` using membership, then extend it to also allow port 80.

<details>
<summary>Show a worked solution</summary>

```python
if port in (21, 22, 23, 80):
    print("known service port")
```

Membership on a tuple is clearer and cannot fall into the `or 80` trap.
</details>

**Exercise 3.** Without running it, predict `True or False and False` and `0 or "" or "fallback"`, then verify in the REPL.

<details>
<summary>Show answer</summary>

```text
True
'fallback'
```

`and` binds tighter, so the first is `True or (False and False)`. In the second, both `0` and `""` are falsy, so `or` continues to `"fallback"`, the first truthy operand.
</details>

## Check Yourself

**What is the difference between `==` and `is`?**

<details>
<summary>Show answer</summary>

`==` compares values (what `__eq__` defines); `is` compares object identity. Use `is` for `None`, `True`, `False`; use `==` for everything else.
</details>

**Why does `if port == 22 or 80:` always pass?**

<details>
<summary>Show answer</summary>

It parses as `(port == 22) or (80)`, and `80` is truthy, so the whole expression is always truthy. The fix is `if port in (22, 80):`.
</details>

**What does `"0x10" and 16` evaluate to?**

<details>
<summary>Show answer</summary>

`16`. `and` returns the last operand when both are truthy; `"0x10"` is a non-empty string, hence truthy.
</details>
