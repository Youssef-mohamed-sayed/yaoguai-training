# Dictionaries

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Dictionaries map unique hashable keys to values. Use `d[key]` for required keys and `d.get(key, default)` for optional keys. Iterate with `.items()`. Dictionaries can contain nested dictionaries and support comprehensions.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
counts = {}
for severity in ["info", "warning", "info"]:
    counts[severity] = counts.get(severity, 0) + 1
print(counts)
```

## Practical Exercise

Create a log-event dictionary. Count severity values and build a dictionary containing only severities with counts greater than one.

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
