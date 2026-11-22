# pip and Virtual Environments

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

A virtual environment isolates dependencies for one project. `pip` installs third-party packages; use `python -m pip` to associate pip with the selected interpreter.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

Windows:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install `requests` with `python -m pip install requests`. Save dependencies using `python -m pip freeze > requirements.txt`; restore with `python -m pip install -r requirements.txt`. Deactivate with `deactivate`.

## Practical Exercise

Create `.venv`, install `requests`, save `requirements.txt`, deactivate, and reactivate. If PowerShell activation is restricted, use `.\.venv\Scripts\python.exe -m pip install requests` without changing system policy.

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
