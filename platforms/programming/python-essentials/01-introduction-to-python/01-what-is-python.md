# What Is Python?

## Learning Objectives

- Explain what Python is and what "interpreted, high-level, dynamically typed" means in practice.
- Describe the execution model: source code, bytecode, and the interpreter.
- Recognize where Python is a strong choice and where it is not.

## Introduction

Python is a general-purpose programming language created by Guido van Rossum and first released in 1991. Three properties define how it feels to work with:

- **Interpreted.** You run a source file directly and the Python interpreter executes it line by line. There is no separate compile-and-link step in your workflow, so the feedback loop from "edit" to "run" is seconds.
- **High-level.** You work with concepts like "read this file" or "sort this list" instead of managing memory addresses. The interpreter handles allocation and garbage collection for you.
- **Dynamically typed.** Types belong to values, not to variable names. A name can refer to an integer on one line and a string later, and type errors surface at runtime rather than at compile time.

These traits make Python fast to write and easy to read, at the cost of raw speed compared to compiled languages like C or Rust.

## How Python Actually Runs Your Code

When you run `python script.py`, the interpreter (almost always CPython, the reference implementation written in C) does two things:

1. **Compiles** your source into *bytecode*, a lower-level set of instructions. You can see this cached in `__pycache__` directories as `.pyc` files.
2. **Executes** the bytecode in the CPython virtual machine, a loop that reads one bytecode instruction at a time and performs it.

```text
script.py  --(compile)-->  bytecode (.pyc)  --(CPython VM)-->  output
```

This is why Python is "interpreted" but still has a compile step: the compilation is automatic and in-memory, not a separate command you run.

You can inspect the bytecode yourself with the `dis` module:

```python
import dis

def greet(name):
    return "Hello, " + name

dis.dis(greet)
```

```text
  2           2 LOAD_CONST               1 ('Hello, ')
              4 LOAD_FAST                0 (name)
              6 BINARY_ADD
              8 RETURN_VALUE
```

You will never need to read bytecode for daily work, but knowing it exists explains error messages, `.pyc` files, and why "compiling Python" questions come up in interviews.

## The REPL: Your Scratchpad

Running `python` with no file opens the interactive interpreter (the REPL: Read, Evaluate, Print, Loop). It evaluates each line immediately and prints the result:

```text
$ python3
Python 3.12.3 (main, ...)
>>> 2 + 3
5
>>> "port " + str(8080)
'port 8080'
>>> len("yaoguai")
7
```

Use the REPL constantly while learning: test one expression, check a method's behavior, explore a module with `dir()` and `help()`. Exit with `exit()` or Ctrl-D (Ctrl-Z then Enter on Windows).

## Where Python Excels, and Where It Does Not

Python is a strong default for:

- **Automation and scripting** - file processing, log parsing, renaming batches, scheduled jobs.
- **Security work** - quick network tools, protocol experiments, exploit proofs of concept, glue between other tools. Most of the security ecosystem (pwntools, scapy, impacket) is Python.
- **Web backends** - Django, Flask, and FastAPI power large production systems.
- **Data analysis and machine learning** - pandas, NumPy, and PyTorch are the industry standard stack.

It is a weaker choice for:

- **CPU-bound number crunching** in pure Python (solved by calling C extensions, which is what NumPy does).
- **Mobile apps and games**, where other toolchains dominate.
- **Hard real-time systems**, where garbage collection pauses are unacceptable.

## Common Mistakes

- Thinking "interpreted" means there is no error checking until the line runs. Syntax errors are caught at the compile-to-bytecode step, before anything executes.
- Confusing the `python` and `python3` commands. On many systems `python` is Python 2 or missing entirely; this course always means Python 3.
- Editing a file, then running a different file by accident and wondering why nothing changed.

## Key Takeaways

- Python is interpreted, high-level, and dynamically typed; CPython compiles your source to bytecode and executes it in a VM.
- The REPL gives instant feedback and is the fastest way to test an idea.
- Python trades raw speed for development speed, which is usually the right trade for scripts, tools, and backends.

## Practice Exercises

Do these in your own terminal. Try each task before opening the solution.

**Exercise 1.** Start the REPL. Evaluate an arithmetic expression, a string expression, and call a built-in function. Then exit.

<details>
<summary>Show a worked solution</summary>

```text
$ python3
>>> 17 * 24
408
>>> "bandit" * 2
'banditbandit'
>>> abs(-42)
42
>>> exit()
```

Any correct expressions count. The point is to get comfortable typing into `>>>` and leaving again.
</details>

**Exercise 2.** In the REPL, run `import this` and read the output. Pick one line of the Zen of Python and write down what you think it means.

<details>
<summary>Show a worked solution</summary>

```text
>>> import this
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
...
```

For example, "Explicit is better than implicit" means code should say what it does in plain sight rather than relying on hidden behavior, so the next reader does not have to guess.
</details>

**Exercise 3.** Use `dis.dis()` on a one-line function you write yourself, as shown above. Find the `RETURN_VALUE` instruction in the output.

<details>
<summary>Show a worked solution</summary>

```python
import dis

def double(x):
    return x * 2

dis.dis(double)
```

```text
  2           2 LOAD_FAST                0 (x)
              4 LOAD_CONST               1 (2)
              6 BINARY_MULTIPLY
              8 RETURN_VALUE
```

The exact opcode names vary slightly between Python versions; finding `RETURN_VALUE` at the end is the goal.
</details>

## Check Yourself

**What are the two stages CPython performs when you run a script?**

<details>
<summary>Show answer</summary>

It compiles the source to bytecode, then executes that bytecode in the CPython virtual machine.
</details>

**In Python, do types belong to variables or to values?**

<details>
<summary>Show answer</summary>

To values. A name is just a label and can be rebound to an object of a different type at any time.
</details>

**You type `python` and get "command not found", but Python is installed. What is the most likely fix?**

<details>
<summary>Show answer</summary>

Use `python3` instead. Many systems do not link the plain `python` name to Python 3.
</details>
