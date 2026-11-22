# TCP Client and Server

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

A TCP server binds, listens, and accepts a client. The accepted socket communicates with that client. TCP is a byte stream, so applications must define message framing. Use timeouts and context managers to close sockets.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

Server:
```python
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 50007))
    server.listen(1)
    conn, addr = server.accept()
    with conn:
        conn.settimeout(3)
        data = conn.recv(1024)
        conn.sendall(b"Received: " + data)
```
Client:
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.settimeout(3)
    client.connect(("127.0.0.1", 50007))
    client.sendall(b"hello")
    print(client.recv(1024).decode("utf-8"))
```

## Practical Exercise

Run the server first, then the client, both on the same machine. Change the message and handle bind/connect errors. Never expose the practice server to an untrusted network.

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
