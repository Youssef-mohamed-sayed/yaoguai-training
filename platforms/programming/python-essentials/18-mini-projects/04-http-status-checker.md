# HTTP Status Checker

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Build a one-URL command-line utility using `requests.get(url, timeout=5)`. Report final URL, status code, and elapsed time. A 404 is an HTTP response, not a connection failure.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import requests

def check(url):
    try:
        response = requests.get(url, timeout=5)
        return response.url, response.status_code, response.elapsed.total_seconds()
    except requests.Timeout:
        return "timeout"
    except requests.RequestException as error:
        return f"request error: {error}"
```

## Practical Exercise

Add command-line argument validation, require `http://` or `https://`, and test a reachable endpoint and a refused local connection.

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
