# Syntax and Variables

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Python uses indentation to define blocks. Use four spaces consistently. A variable name refers to an object; assignment binds a name to a value. Python is dynamically typed. Use descriptive `snake_case` names; uppercase names indicate constants by convention.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
# A useful comment
username = "analyst"
attempts = 3
attempts += 1
MAX_RETRIES = 5

if attempts < MAX_RETRIES:
    print(f"{username}: {attempts}")
```

## Practical Exercise

Create variables for a filename, byte count, and Boolean file-exists flag. Update the byte count and print a formatted summary.

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
