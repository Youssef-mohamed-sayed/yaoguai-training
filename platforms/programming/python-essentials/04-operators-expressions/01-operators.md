# Operators and Expressions

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Python provides arithmetic (`+ - * / // % **`), comparison (`== != < <= > >=`), logical (`and or not`), assignment (`+=`), membership (`in`), and identity (`is`) operators. Parentheses clarify precedence. `==` compares values; `is` checks object identity. Use `is None` for a None check.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
port = 443
allowed = port == 80 or port == 443
print(allowed)       # True
print(29 // 5, 29 % 5)  # 5 4
print(None is None)  # True
```

## Practical Exercise

Check whether a port is 80 or 443; calculate quotient and remainder for 29 divided by 5; compare two separate equal lists using `==` and `is`.

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
