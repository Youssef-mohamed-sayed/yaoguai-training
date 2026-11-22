# Interpreter and Scripts

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Interactive mode is useful for experiments; saved `.py` files are repeatable programs. The current working directory affects relative file paths.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
message = "Learning Python"
print(message)
```
Run with `py hello.py` on Windows or `python3 hello.py` on Linux. Start an interactive prompt with `py` or `python3`; leave it with `exit()`.

## Practical Exercise

Calculate `17 * 4` interactively, then save and run a script. Use `pwd` (Linux) or `Get-Location` (PowerShell) to inspect the current directory.

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
