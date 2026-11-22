# while and Loop Controls

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

A `while` loop repeats while its condition is true. `break` exits the nearest loop; `continue` skips to its next iteration; `pass` does nothing. Ensure the condition changes or the loop has an exit to avoid accidental infinite loops.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
attempts = 0
while attempts < 3:
    print(f"Attempt {attempts + 1}")
    attempts += 1

for value in ["a", "", "b"]:
    if not value:
        continue
    print(value)
```

## Practical Exercise

Ask repeatedly until a positive integer is entered. Search a list and stop at the first match. Identify the state change that guarantees termination.

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
