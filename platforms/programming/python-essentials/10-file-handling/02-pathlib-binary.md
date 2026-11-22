# pathlib and Binary Files

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

`pathlib.Path` represents portable paths. Use `/` to join components, `.exists()`, `.is_file()`, `.is_dir()`, `.iterdir()`, and `.stat()`. Binary mode (`rb`, `wb`) works with bytes, useful for hashing and file signatures. Common errors include `FileNotFoundError`, `PermissionError`, and decoding errors.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
from pathlib import Path

root = Path("practice")
root.mkdir(exist_ok=True)
for item in root.iterdir():
    if item.is_file():
        print(item.name, item.stat().st_size)
```

## Practical Exercise

Create a practice directory, list files, and read the first 16 bytes of a supplied binary sample. Explain why bytes are not strings.

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
