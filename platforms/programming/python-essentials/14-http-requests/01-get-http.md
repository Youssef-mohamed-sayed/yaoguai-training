# HTTP and GET Requests

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

HTTP clients send requests containing a method, target, headers, and optionally a body. Servers return a status code, headers, and a body. 2xx indicates success, 3xx redirection, 4xx client-side issue, and 5xx server-side issue. `requests` is third-party: install with `python -m pip install requests`.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import requests
try:
    response = requests.get(
        "https://httpbin.org/get",
        params={"topic": "python"},
        timeout=5,
    )
    print(response.status_code)
    print(response.headers.get("Content-Type"))
except requests.Timeout:
    print("Timed out")
except requests.RequestException as error:
    print(f"Request failed: {error}")
```

## Practical Exercise

Use a local or instructor-authorized endpoint. Add query parameters, display selected headers, and handle timeouts. Do not rely on a public test service being available.

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
