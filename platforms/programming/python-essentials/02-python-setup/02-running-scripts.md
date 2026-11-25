# Running Scripts and Programs

## Learning Objectives

- Run Python code as a saved script, from the REPL, and with command-line arguments.
- Read command-line arguments with `sys.argv`.
- Understand exit codes and why scripts return them.

## Introduction

The REPL is for exploring; scripts are for keeping. A Python script is a plain text file, conventionally ending in `.py`, executed with the interpreter:

```bash
python3 hello.py
```

Save this as `hello.py` and run it:

```python
print("Hello from a file")
name = input("Your name: ")
print(f"Welcome, {name}")
```

```text
$ python3 hello.py
Hello from a file
Your name: Youssef
Welcome, Youssef
```

Three things to notice: `print` writes to standard output, `input()` reads a line from standard input and always returns a string, and the f-string `f"Welcome, {name}"` inserts the variable into the text.

## Passing Arguments on the Command Line

Real tools take arguments: `nmap scanme.nmap.org`, `grep error app.log`. Python exposes them through `sys.argv`, a list of strings where element 0 is the script name:

```python
import sys

print("Script:", sys.argv[0])
print("Arguments:", sys.argv[1:])
```

```text
$ python3 echo_args.py alpha beta
Script: echo_args.py
Arguments: ['alpha', 'beta']
```

Everything in `sys.argv` is a string, even numbers. Convert explicitly and validate before use:

```python
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} PORT", file=sys.stderr)
    sys.exit(2)

try:
    port = int(sys.argv[1])
except ValueError:
    print("PORT must be a number", file=sys.stderr)
    sys.exit(2)

print(f"Would connect to port {port}")
```

```text
$ python3 port.py 8080
Would connect to port 8080
$ python3 port.py
Usage: port.py PORT
```

For anything beyond one or two arguments, the standard library's `argparse` module builds real command-line interfaces with `--flags`, help text, and validation. You will meet it in later projects.

## Exit Codes

When a script ends, it reports an integer *exit code* to the shell: 0 means success, anything else means failure. Other programs (cron, CI, shell scripts) rely on this:

```bash
python3 check_host.py && echo "host is up"
```

`sys.exit(2)` above sets the code explicitly; an unhandled exception exits with 1 and prints a traceback. Check the last code in bash with `echo $?`.

## Executable Scripts on Linux and macOS

Add a shebang line and the execute bit to run a script directly:

```python
#!/usr/bin/env python3
print("runs like a program")
```

```bash
chmod +x tool.py
./tool.py
```

`#!/usr/bin/env python3` tells the kernel which interpreter to use; `env` finds `python3` on PATH so the script works across machines.

## Common Mistakes

- Forgetting `sys.argv` values are strings and comparing `sys.argv[1] > 1024`, which compares text lexicographically and misbehaves on numbers like `"80"`.
- Indexing `sys.argv[1]` without checking `len(sys.argv)` first, producing an unhelpful `IndexError` for the user.
- Using `input()` for passwords. It echoes to the screen; use `getpass.getpass()` for secrets.

## Key Takeaways

- Scripts are plain `.py` files run with `python3 file.py`; `print` and `input` cover basic I/O.
- `sys.argv` carries command-line arguments as strings; validate count and type, and print usage to stderr.
- Exit code 0 means success; set nonzero codes with `sys.exit()` so shells can react.

## Practice Exercises

**Exercise 1.** Write `greet.py` that takes exactly one argument, a name, and prints `Hello, NAME!`. With no argument it must print a usage line and exit with code 2.

<details>
<summary>Show a worked solution</summary>

```python
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} NAME", file=sys.stderr)
    sys.exit(2)

print(f"Hello, {sys.argv[1]}!")
```

```text
$ python3 greet.py Youssef
Hello, Youssef!
$ python3 greet.py; echo "exit=$?"
Usage: greet.py NAME
exit=2
```
</details>

**Exercise 2.** Write `add.py` that accepts two integer arguments and prints their sum. Handle non-numeric input with a clear error instead of a traceback.

<details>
<summary>Show a worked solution</summary>

```python
import sys

try:
    a, b = int(sys.argv[1]), int(sys.argv[2])
except (IndexError, ValueError):
    print(f"Usage: {sys.argv[0]} INT INT", file=sys.stderr)
    sys.exit(2)

print(a + b)
```

```text
$ python3 add.py 19 23
42
$ python3 add.py 19 x
Usage: add.py INT INT
```
</details>

**Exercise 3.** Make `add.py` executable with a shebang and `chmod +x`, then run it as `./add.py 1 2`.

<details>
<summary>Show a worked solution</summary>

Add as the first line:

```python
#!/usr/bin/env python3
```

Then:

```text
$ chmod +x add.py
$ ./add.py 1 2
3
```

On Windows there is no execute bit; keep running scripts with `py add.py 1 2`.
</details>

## Check Yourself

**What is `sys.argv[0]`?**

<details>
<summary>Show answer</summary>

The script's name as it was invoked. The actual user arguments start at index 1.
</details>

**Why does `int(sys.argv[1])` need a try/except for robust tools?**

<details>
<summary>Show answer</summary>

`sys.argv` holds strings, and `int()` raises `ValueError` on non-numeric input; without handling, the user sees a raw traceback instead of a useful message.
</details>

**What exit code does an unhandled exception produce?**

<details>
<summary>Show answer</summary>

1. Explicit `sys.exit(n)` lets you choose meaningful codes; 0 signals success.
</details>
