# Defining Functions

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Functions package reusable tasks. Define with `def`; parameters receive inputs and `return` sends a result to the caller. `print()` displays output and is not equivalent to returning a value. Functions without an explicit return produce `None`.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
def is_valid_port(port):
    return isinstance(port, int) and not isinstance(port, bool) and 1 <= port <= 65535

print(is_valid_port(443))
```

## Practical Exercise

Write functions for username normalization, failed-event counting, and min/max calculation. Keep each function focused on one responsibility.

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
