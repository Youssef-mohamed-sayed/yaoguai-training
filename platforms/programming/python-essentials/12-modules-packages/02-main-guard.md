# The if __name__ == "__main__" Guard

## Learning Objectives

- Explain what `__name__` is and how it differs between running and importing a file.
- Structure scripts with a `main()` function behind the guard.
- Understand why the guard matters for testing and reuse.

## Introduction

Every module has a built-in `__name__` attribute. When you **run** a file directly, Python sets its `__name__` to the string `"__main__"`. When you **import** the same file, `__name__` is the module's real name. This one fact powers the standard script structure:

```python
def scan(host):
    return f"results for {host}"

def main():
    print(scan("web-1"))

if __name__ == "__main__":
    main()
```

Run it: `__name__` is `"__main__"`, so `main()` executes. Import it (`import scan_tool` in a test or another script): `__name__` is `"scan_tool"`, the guard is false, and nothing runs - the importing code gets the functions without the side effects.

## Why It Matters

Without the guard, top-level code runs on **every import**:

```python
# bad_tool.py
print("scanning...")        # runs even when another file imports this!
target = input("host? ")
```

A test file doing `import bad_tool` would print and then block waiting for input. With the guard, modules are both importable libraries and runnable programs:

```python
# tool.py
def add(a, b):
    return a + b

def main():
    print(add(2, 3))

if __name__ == "__main__":
    main()
```

```python
# test_add.py - imports cleanly, no side effects
from tool import add
assert add(2, 3) == 5
print("ok")
```

This is also the structure you will see in every mature Python codebase: functions and constants at the top, a `main()` orchestrating, the guard at the bottom. `sys.exit(main())` under the guard is a common refinement so `main`'s return value becomes the process exit code.

## argparse Under the Guard

Command-line parsing belongs inside `main` too, so imports never parse arguments:

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Tiny port checker")
    parser.add_argument("host", help="target host")
    parser.add_argument("-p", "--port", type=int, default=80)
    args = parser.parse_args()
    print(f"checking {args.host}:{args.port}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```text
$ python3 check.py web-1 -p 443
checking web-1:443
$ python3 check.py --help
usage: check.py [-h] [-p PORT] host
...
```

`argparse` gives you `--help`, type conversion, and defaults for free - the reason not to hand-roll `sys.argv` parsing once a tool grows past one argument.

## Common Mistakes

- No guard, so tests and imports trigger scans, prompts, or API calls.
- Putting `argparse` setup at module top level; importing the file then consumes the *test runner's* arguments.
- Believing the guard makes code private; it only controls execution on import, not access.

## Key Takeaways

- `__name__` is `"__main__"` only in the file being run directly.
- The guard `if __name__ == "__main__": main()` makes a file both an importable module and a runnable program.
- Keep argument parsing and side effects inside `main()`; return an exit code and pass it to `SystemExit`.

## Practice Exercises

**Exercise 1.** Write `temp.py` with a function `c_to_f(c)` and a guarded `main()` that converts 100 C. Then import `temp` from the REPL and call `c_to_f(0)` - confirm nothing printed on import.

<details>
<summary>Show a worked solution</summary>

```python
def c_to_f(c):
    return c * 9 / 5 + 32

def main():
    print(c_to_f(100))

if __name__ == "__main__":
    main()
```

```text
$ python3 temp.py
212.0
$ python3
>>> import temp          # (silence - nothing printed)
>>> temp.c_to_f(0)
32.0
```
</details>

**Exercise 2.** Add an `argparse` interface to a script that greets: a required `name` and an optional `--shout` flag that uppercases the greeting.

<details>
<summary>Show a worked solution</summary>

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Greeter")
    parser.add_argument("name")
    parser.add_argument("--shout", action="store_true")
    args = parser.parse_args()
    msg = f"Hello, {args.name}!"
    print(msg.upper() if args.shout else msg)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```text
$ python3 greet.py ada --shout
HELLO, ADA!
```
</details>

**Exercise 3.** Write a test file that imports a function from a guarded module and asserts two cases. Run it and confirm the module's `main()` did not execute.

<details>
<summary>Show a worked solution</summary>

```python
# test_temp.py
from temp import c_to_f

assert c_to_f(0) == 32
assert c_to_f(100) == 212
print("tests passed")
```

```text
$ python3 test_temp.py
tests passed
```

No conversion output appears because importing `temp` sets its `__name__` to `"temp"`, so the guard is false.
</details>

## Check Yourself

**What is `__name__` when a file is imported?**

<details>
<summary>Show answer</summary>

The module's name (the filename without `.py`), not `"__main__"`, so the guard block does not execute.
</details>

**Why should argument parsing live inside `main()`?**

<details>
<summary>Show answer</summary>

So importing the module (for tests or reuse) never consumes command-line arguments or produces side effects.
</details>

**What does `raise SystemExit(main())` accomplish?**

<details>
<summary>Show answer</summary>

It turns `main()`'s return value into the process exit code, so shells and CI can tell success (0) from failure.
</details>
