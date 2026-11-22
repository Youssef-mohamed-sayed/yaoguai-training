# Installing Python

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Install Python 3 from python.org on Windows or from your Linux distribution's package manager. Verify the interpreter before configuring an editor. PATH is the list of directories a shell searches when resolving commands.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

Windows PowerShell:
```powershell
py --version
python --version
```
Linux:
```bash
python3 --version
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

## Practical Exercise

Install Python 3 and record the command that works. If `python` is not found, try `py` on Windows or `python3` on Linux, reopen the terminal, and check PATH.

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
