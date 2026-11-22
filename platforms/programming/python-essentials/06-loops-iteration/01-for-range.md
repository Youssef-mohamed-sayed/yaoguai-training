# for Loops and range()

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

A `for` loop iterates over items in an iterable such as a list, string, or `range`. `range(stop)` excludes the stop value; `range(start, stop, step)` controls the sequence. Nested loops run the inner loop for each outer iteration.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
ports = [22, 80, 443, 8080]
for port in ports:
    if port <= 1024:
        print(port)

for number in range(1, 6):
    print(number)
```

## Practical Exercise

Filter a list to ports in 1..1024, count `.log` filenames, and print numbers from 10 down to 1.

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
