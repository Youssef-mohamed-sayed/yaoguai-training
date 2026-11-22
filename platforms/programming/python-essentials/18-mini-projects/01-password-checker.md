# CLI Password Strength Checker

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Build a local heuristic that checks length, lowercase, uppercase, digits, and symbols. It is not a security guarantee and must not store, print, or transmit the password. Use `getpass` to hide terminal input.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import getpass

def evaluate(password):
    return {
        "12+ characters": len(password) >= 12,
        "lowercase": any(c.islower() for c in password),
        "uppercase": any(c.isupper() for c in password),
        "digit": any(c.isdigit() for c in password),
        "symbol": any(not c.isalnum() for c in password),
    }

password = getpass.getpass("Test password: ")
for label, passed in evaluate(password).items():
    print(("OK" if passed else "Improve") + ": " + label)
```

## Practical Exercise

Add checks for all-whitespace and repeated-character-only input. Never log the entered password.

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
