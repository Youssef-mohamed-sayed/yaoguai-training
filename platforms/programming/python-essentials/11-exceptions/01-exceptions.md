# Exceptions and Tracebacks

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Syntax errors prevent parsing; runtime errors occur during execution; logical errors produce wrong results. Read tracebacks for the exception type, message, source line, and call stack. Catch specific exceptions such as `ValueError`, `KeyError`, `IndexError`, `FileNotFoundError`, and `ZeroDivisionError`.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
raw = input("Integer: ")
try:
    number = int(raw)
except ValueError:
    print("Invalid integer")
else:
    print(number * 2)
finally:
    print("Finished")
```

## Practical Exercise

Handle invalid integer input, a missing file, and a missing dictionary key. Explain why `except Exception` can hide bugs.

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
