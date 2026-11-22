# Reading and Writing Files

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Use `open()` or `Path.open()` with `with` so files close reliably. Modes: `r` read, `w` truncate/write, `a` append, `x` create exclusively, `b` binary. Specify an encoding such as UTF-8 for text. Iterate line by line for large files.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
from pathlib import Path

path = Path("notes.txt")
with path.open("w", encoding="utf-8") as file:
    file.write("first line\n")

with path.open("a", encoding="utf-8") as file:
    file.write("second line\n")
```

## Practical Exercise

Create a configuration file, read it line by line, append a record, and explain why `w` would destroy existing contents.

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
