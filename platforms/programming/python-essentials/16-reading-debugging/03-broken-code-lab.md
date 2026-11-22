# Broken Code Lab

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Debug by reproducing the problem, identifying the cause, making one focused change, and testing again. Example bug: `count =+ 1` assigns positive one; `count += 1` increments. Validate dictionary keys and types before using them.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

Broken:
```python
def count_errors(lines):
    count = 0
    for line in lines:
        if "ERROR" in line:
            count =+ 1
    return count
```
Correct:
```python
def count_errors(lines):
    count = 0
    for line in lines:
        if "ERROR" in line:
            count += 1
    return count
```

## Practical Exercise

Repair the counter, a missing-dictionary-key bug, and a file that is not closed with a context manager. Add tests that would catch each bug.

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
