# POST, JSON, and API Errors

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Use `json=payload` to send JSON and `response.json()` to parse JSON. `raise_for_status()` raises for 4xx/5xx responses. A successful HTTP response can still contain unexpected JSON structure; validate types and keys. Avoid hardcoded secrets and never send sensitive data to public echo services.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
payload = {"event": "training", "severity": "info"}
response = requests.post("https://httpbin.org/post", json=payload, timeout=5)
response.raise_for_status()
data = response.json()
print(type(data).__name__)
```

## Practical Exercise

POST harmless sample data to a local test endpoint. Handle timeout, HTTP errors, invalid JSON, and unexpected response structure.

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
