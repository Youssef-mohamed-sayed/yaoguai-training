# Why Python for Cybersecurity

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Python is useful for repeatable defensive workflows: parsing logs, comparing file hashes, inventorying directories, inspecting authorized HTTP endpoints, and automating lab tasks. The script's purpose and authorization determine whether an activity is appropriate.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

| Task | Useful tools |
|---|---|
| Parse logs | strings, dictionaries, `Counter` |
| File integrity | `hashlib`, file handling |
| HTTP inspection | `requests` |
| TCP checks | `socket` |
| Inventory | `pathlib`, `os` |

## Practical Exercise

Choose one workflow. Identify its input, output, required Python features, and one safety boundary. Use only supplied data or systems you are authorized to test.

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
