# Sockets, TCP, and UDP

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

A socket is a communication endpoint. An IP address identifies a host/interface; a port identifies an application endpoint. TCP is connection-oriented and provides a reliable ordered byte stream. UDP sends datagrams without guarantees of delivery or ordering. Use localhost for exercises.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

| TCP | UDP |
|---|---|
| Connection setup | No connection setup |
| Reliable ordered byte stream | No delivery/order guarantee |
| `SOCK_STREAM` | `SOCK_DGRAM` |

## Practical Exercise

Resolve `localhost`; explain host versus port; choose TCP or UDP for a reliable ordered request/response service.

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
