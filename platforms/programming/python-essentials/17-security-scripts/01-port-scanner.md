# Basic TCP Port Scanner

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Use only localhost or an explicitly authorized lab target. This beginner tool checks a small configurable range sequentially; it is not a replacement for Nmap. A successful TCP connection means the handshake succeeded at that moment. A failed attempt does not prove the port is closed: filtering, routing, or timeout may explain it.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import socket

def check_port(host, port, timeout=0.5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except OSError as error:
        print(f"Check failed: {error}")
        return False

def scan(host, start, end):
    if not (1 <= start <= end <= 65535):
        raise ValueError("invalid port range")
    for port in range(start, end + 1):
        if check_port(host, port):
            print(f"{port}: open (connection succeeded)")
        else:
            print(f"{port}: no successful connection")

if __name__ == "__main__":
    scan("127.0.0.1", 1, 1024)
```

## Practical Exercise

Change to a three-port localhost range. Start a local test service on one port and observe the result. Keep the range small and do not scan third-party hosts.

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
