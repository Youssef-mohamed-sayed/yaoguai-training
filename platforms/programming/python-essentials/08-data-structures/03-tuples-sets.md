# Tuples and Sets

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Tuples are ordered and immutable; unpack them into names. A one-item tuple needs a comma. Sets contain unique hashable values and support union (`|`), intersection (`&`), difference (`-`), and membership tests. An empty set is `set()`, not `{}`.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
observed = {"192.0.2.1", "192.0.2.2"}
known = {"192.0.2.2", "192.0.2.3"}
print(observed & known)
```

## Practical Exercise

Unpack a username/role tuple. Find unique IPs and the intersection of two IP sets. Explain when a list, dictionary, tuple, or set is the clearest choice.

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
