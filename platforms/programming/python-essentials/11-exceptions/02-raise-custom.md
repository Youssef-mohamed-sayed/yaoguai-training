# Raising and Custom Exceptions

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Use `raise` to report invalid inputs. `finally` runs whether an exception occurs or not; use context managers for resource cleanup when possible. Define custom exceptions by subclassing `Exception`.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
class InvalidRecordError(Exception):
    pass

def parse_record(line):
    fields = line.strip().split(",")
    if len(fields) != 3:
        raise InvalidRecordError("expected three fields")
    return fields
```

## Practical Exercise

Create a validator that raises `ValueError` for an invalid port. Create a custom malformed-record exception and skip only the bad record.

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
