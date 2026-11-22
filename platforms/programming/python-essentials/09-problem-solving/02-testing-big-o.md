# Testing and Big-O Intuition

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Test normal, empty, boundary, and invalid inputs. `assert` checks development assumptions but is not a security validation mechanism. Big-O describes growth: O(1) constant, O(n) linear, O(n²) quadratic, O(log n) logarithmic. A list membership check is generally O(n); set membership is average-case O(1).

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
def is_even(number):
    return number % 2 == 0

assert is_even(4)
assert not is_even(5)
```

## Practical Exercise

Test a port validator at 1, 65535, 0, 65536, and a wrong type. Explain how a nested loop may scale as input grows.

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
