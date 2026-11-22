# HTTP Request Inspector

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Inspect one authorized endpoint. Display status and selected headers; handle timeout and connection errors; parse JSON only when appropriate. Do not include credential theft, session hijacking, or unauthorized scanning.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import requests

def inspect(url):
    try:
        response = requests.get(url, timeout=5)
    except requests.Timeout:
        print("Timed out")
        return
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return
    print("URL:", response.url)
    print("Status:", response.status_code)
    for name in ("Content-Type", "Content-Length", "Server"):
        print(name, response.headers.get(name, "[not supplied]"))
```

## Practical Exercise

Test a local or approved endpoint, a refused local connection, and a JSON response. Do not print cookies or authorization headers.

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
