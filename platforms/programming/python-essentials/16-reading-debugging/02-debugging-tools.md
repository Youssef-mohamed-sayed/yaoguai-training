# Tracebacks, print, pdb, and Assertions

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Use tracebacks to find the failing line and call stack. Temporary `print()` statements reveal state but must not expose secrets. Run `python -m pdb script.py`; useful commands include `n`, `s`, `c`, `p expression`, and `q`. `breakpoint()` pauses execution. Assertions are development checks, not security validation.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
assert isinstance(records, list)
```
Run:
```bash
python -m pdb script.py
```

## Practical Exercise

Debug a wrong counter, use pdb to inspect a variable, and add regression tests. Explain why assertions should not validate untrusted user input.

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
