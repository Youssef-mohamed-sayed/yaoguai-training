# Built-in Types and Conversion

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Common types include `int`, `float`, `str`, `bool`, `None`, `list`, `tuple`, `dict`, and `set`. Inspect values with `type()` and `isinstance()`. Convert deliberately with `int()`, `float()`, and `str()`. `input()` always returns a string.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
raw = input("Count: ")
try:
    count = int(raw)
except ValueError:
    print("Enter a whole number.")
else:
    print(f"Twice the count is {count * 2}")
```

## Practical Exercise

Ask for a number and print its square. Test invalid input. Explain why `int(input(...))` can raise `ValueError`.

**Hints**
1. Write down the expected input and output first.
2. Break the task into small steps or functions.
3. Test a normal case, a boundary case, and invalid input where relevant.

## Common Mistakes

- Copying code without understanding the values and types.
- Assuming input, files, or network services are always available.
- Ignoring error messages or catching every exception indiscriminately.
- Forgetting resource cleanup or safe authorization boundaries.

## Key Takeaways

- Choose the simplest construct that clearly expresses the task.
- Validate assumptions at program boundaries.
- Test the behavior, not merely whether the program starts.

## Further Practice

Modify the example, explain each line in your own words, and link the exercise to the next module.
