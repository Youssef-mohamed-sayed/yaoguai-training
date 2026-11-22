# Arguments, Scope, and Docstrings

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Positional arguments match by position; keyword arguments by name; defaults apply when omitted. `*args` collects extra positional arguments in a tuple and `**kwargs` collects keyword arguments in a dictionary. Local names belong to a function scope. `global` and `nonlocal` rebind outer names but should be used sparingly. Docstrings document functions; lambdas are short anonymous functions.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
def report(*items, severity="info", **metadata):
    """Display a compact event summary."""
    print(items, severity, metadata)

report("login", "file", severity="low", source="lab")
```

## Practical Exercise

Write a function accepting any number of numeric positional arguments and returning their sum. Add a docstring. Explain why mutable default arguments such as `items=[]` can be surprising.

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
