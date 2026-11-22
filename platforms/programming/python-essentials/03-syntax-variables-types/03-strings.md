# String Formatting and Methods

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Strings are immutable Unicode text sequences. Useful methods include `strip`, `lower`, `upper`, `replace`, `split`, `join`, `startswith`, and `endswith`. Use f-strings for readable interpolation.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
raw_name = "  Analyst "
name = raw_name.strip().lower()
parts = "INFO,192.0.2.5,login".split(",")
print(f"user={name}; source={parts[1]}")
```

## Practical Exercise

Normalize a username, split a simple comma-separated record, and join words with spaces. For real CSV with quoted commas, use the `csv` module.

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
