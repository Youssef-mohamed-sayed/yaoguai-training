# Problem Decomposition

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Before coding, identify inputs, outputs, constraints, and examples. Write pseudocode, choose data structures, implement, test edge cases, and refactor for readability. Break large tasks into smaller functions.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

Problem: count failed statuses.
Pseudocode:
1. Set count to zero.
2. Visit each status.
3. If it equals "failed", increase count.
4. Return count.

```python
def count_failed(statuses):
    return sum(1 for status in statuses if status == "failed")
```

## Practical Exercise

Solve: largest of three numbers, count vowels, identify duplicate values, and count events by severity. For each, write inputs, outputs, pseudocode, and three tests.

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
