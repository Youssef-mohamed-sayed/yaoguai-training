# if, elif, and else

## Learning Objectives

- Structure decisions with `if` / `elif` / `else` and understand evaluation order.
- Choose between nested conditions, chained comparisons, and conditional expressions.
- Handle edge cases deliberately instead of hoping inputs are well-behaved.

## Introduction

A conditional runs the **first** branch whose test is truthy, then skips the rest. Order is therefore part of the logic: put specific cases before general ones.

```python
code = 404

if 200 <= code < 300:
    label = "success"
elif 300 <= code < 400:
    label = "redirect"
elif 400 <= code < 500:
    label = "client error"
elif 500 <= code < 600:
    label = "server error"
else:
    label = "not an HTTP status"

print(f"{code}: {label}")
```

```text
404: client error
```

The `else` branch is the catch-all. Leaving it out means "do nothing if nothing matched," which is fine when that is truly the intent - and a silent bug when you actually forgot a case.

## Nested Conditions and Early Structure

Conditions can nest, and sometimes a decision genuinely depends on an earlier one:

```python
if user:
    if user.is_admin:
        show_admin_panel()
    else:
        show_dashboard()
else:
    show_login()
```

Two structural habits keep nesting shallow:

1. **Combine with boolean operators** when the branches share a body:
   `if user and user.is_admin:` replaces one level.
2. **Guard clauses**: handle the failing/edge case first and exit (with `return` in a function, module 07), so the main path stays at low indentation. Deep pyramids of `if` inside `if` inside `if` are where bugs hide.

## Conditional Expressions

For picking between two values, the inline form is clearer than a four-line `if`:

```python
status = "open" if result == 0 else "closed"
severity = "high" if fails > 10 else "normal"
```

Use it for simple either/or values only. If the condition or the branches need explanation, a normal `if` block reads better.

## Defensive Branching

Real input is hostile or sloppy. Branch on *validated* data:

```python
raw = input("Port: ")
if not raw.isdigit():
    print("port must be numeric")
else:
    port = int(raw)
    if 1 <= port <= 65535:
        print(f"checking port {port}")
    else:
        print("port out of range")
```

Checking `isdigit()` before `int()` is a common and readable validation pattern for interactive scripts. (For non-interactive tools, `try`/`except ValueError` around `int()` is equally good; module 11 compares the two styles.)

## Common Mistakes

- Ordering ranges wrong: testing `code < 500` before `code < 400` makes the 4xx branch unreachable. Specific conditions first.
- Repeating `or` with implicit subjects: `if code == 404 or 403:` is always truthy (see module 04). Use `in (404, 403)`.
- Using nested `if`s three levels deep when a guard clause or a combined condition would flatten the logic.
- Forgetting that an empty `elif` chain without `else` silently does nothing on unexpected input.

## Key Takeaways

- `if`/`elif`/`else` evaluates top to bottom and runs only the first match; order branches from specific to general.
- Flatten with combined conditions and guard clauses; keep nesting shallow.
- Use conditional expressions for simple either/or values, and validate input before branching on it.

## Practice Exercises

**Exercise 1.** Classify an HTTP status code read from input into "success", "redirect", "client error", "server error", or "not an HTTP status". Reject non-numeric input with a clear message.

<details>
<summary>Show a worked solution</summary>

```python
raw = input("Status code: ")
if not raw.isdigit():
    print("status must be a number")
else:
    code = int(raw)
    if 200 <= code < 300:
        label = "success"
    elif 300 <= code < 400:
        label = "redirect"
    elif 400 <= code < 500:
        label = "client error"
    elif 500 <= code < 600:
        label = "server error"
    else:
        label = "not an HTTP status"
    print(f"{code}: {label}")
```

```text
Status code: 503
503: server error
```
</details>

**Exercise 2.** Given `age` and `has_id` variables, print "entry allowed" only when `age >= 18` **and** `has_id` is true - first as nested `if`s, then as one combined condition.

<details>
<summary>Show a worked solution</summary>

```python
# nested
if age >= 18:
    if has_id:
        print("entry allowed")

# combined (preferred here: same body)
if age >= 18 and has_id:
    print("entry allowed")
```

Both work; the combined version is shorter when both branches do the same thing.
</details>

**Exercise 3.** Using a conditional expression, set `verdict` to `"weak"` when `len(pw) < 12` and `"ok"` otherwise, then print it for three test passwords.

<details>
<summary>Show a worked solution</summary>

```python
for pw in ("letmein", "Str0ng!Passw0rd", "aaaaaaaaaaaaa"):
    verdict = "weak" if len(pw) < 12 else "ok"
    print(f"{pw:>16}: {verdict}")
```

```text
        letmein: weak
 Str0ng!Passw0rd: ok
  aaaaaaaaaaaaa: ok
```
</details>

## Check Yourself

**Why does the 5xx check come after the 4xx check in the status classifier?**

<details>
<summary>Show answer</summary>

Branches run in order, and each `elif` only sees values all previous tests rejected. Ordering ascending ranges (2xx, 3xx, 4xx, 5xx) keeps each condition simple and every branch reachable.
</details>

**What is a guard clause?**

<details>
<summary>Show answer</summary>

An early branch that handles the invalid or trivial case and exits (or continues), so the main logic is not wrapped in extra indentation.
</details>

**Rewrite `x = "yes" if ok else "no"` as a normal if statement.**

<details>
<summary>Show answer</summary>

```python
if ok:
    x = "yes"
else:
    x = "no"
```
</details>
