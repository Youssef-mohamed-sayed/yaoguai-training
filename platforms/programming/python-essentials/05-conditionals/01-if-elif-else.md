# if, elif, and else

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Conditions choose which block executes. Python checks branches from top to bottom and runs the first true branch. Nested conditions are useful when a decision depends on an earlier decision; conditional expressions suit short choices.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
code = 404
if 200 <= code < 300:
    label = "success"
elif 300 <= code < 400:
    label = "redirect"
elif 400 <= code < 500:
    label = "client error"
else:
    label = "other"
print(label)
```

## Practical Exercise

Read a status code and classify 2xx, 3xx, 4xx, and 5xx responses. Add a fallback for values outside those ranges.

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
