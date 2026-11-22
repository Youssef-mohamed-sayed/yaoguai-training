# Reading and Tracing Code

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Read imports and constants, find the entry point, follow function calls, track variables, and identify side effects such as file writes, network requests, or global-state changes. Imports execute module-level statements, so inspect them before running unfamiliar code.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
def add_tax(price, rate):
    total = price * (1 + rate)
    return total

print(add_tax(100, 0.1))
```

## Practical Exercise

Trace values line by line. Draw a call sequence for a function calling two helpers. List side effects in an unfamiliar script before executing it.

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
