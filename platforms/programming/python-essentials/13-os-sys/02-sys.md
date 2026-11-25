# The sys Module: Arguments, Streams, and the Interpreter

## Learning Objectives

- Use `sys.argv`, `sys.stdin/stdout/stderr`, and `sys.exit` correctly.
- Read piped input like a proper Unix tool.
- Inspect interpreter facts: version, path, and platform.

## Introduction

`sys` exposes the interpreter itself: how your program was launched, where its input and output flow, and when it stops. You met `sys.argv` in module 02; this lesson completes the picture with streams and exits.

## The Three Streams

Every process has stdin, stdout, and stderr. `print()` writes to stdout; errors belong on stderr so pipelines stay clean:

```python
import sys

print("normal output")
print("something failed", file=sys.stderr)
```

```text
$ python3 tool.py > results.txt
something failed        # still visible: only stdout was redirected
$ python3 tool.py 2> errors.txt > results.txt   # split them
```

**Reading piped input** is what makes a script composable with other Unix tools:

```python
import sys

for line in sys.stdin:
    if "error" in line.lower():
        print(line.strip())
```

```text
$ cat app.log | python3 only_errors.py
ERROR disk full
$ grep . app.log | python3 only_errors.py | wc -l
41
```

This one loop turns your script into a filter that plugs into `cat`, `grep`, `tail -f`, and `wc` - the Unix philosophy in five lines. A common refinement accepts a filename argument *or* stdin:

```python
import sys

source = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
with source:
    for line in source:
        ...
```

## Exits and Interpreter Facts

```python
sys.exit(0)          # success
sys.exit("message")  # prints to stderr, exits with code 1
sys.exit(2)          # convention: usage error

print(sys.version)          # full version string
print(sys.platform)         # 'linux', 'darwin', 'win32'
print(sys.executable)       # which interpreter is running this
print(sys.path[:3])         # module search path (first entries)
```

`sys.platform` gates OS-specific code:

```python
import sys

if sys.platform == "win32":
    config_dir = Path.home() / "AppData"
else:
    config_dir = Path.home() / ".config"
```

And `sys.executable` is the answer to "which Python am I really on?" - worth printing in bug reports and sanity checks inside scripts that must run under a specific interpreter.

## Common Mistakes

- Printing errors to stdout, so they contaminate piped data files.
- Reading all of stdin with `sys.stdin.read()` when line iteration would stream it; the read blocks until EOF on a pipe.
- Hardcoding OS assumptions (`/etc/...` paths) without a `sys.platform` check.
- Deep-fiddling `sys.path` to make imports work instead of fixing the project layout or venv.

## Key Takeaways

- stdout is for results, stderr for diagnostics; redirect them independently.
- `for line in sys.stdin` makes any script a pipeline citizen; support "file argument or stdin" for flexibility.
- `sys.exit` sets the exit code, and `sys.version`/`platform`/`executable` answer interpreter questions.

## Practice Exercises

**Exercise 1.** Write a filter that passes through only lines containing a keyword given as `sys.argv[1]`, reading from stdin. Test it with `cat app.log | python3 filter.py error`.

<details>
<summary>Show a worked solution</summary>

```python
import sys

if len(sys.argv) != 2:
    sys.exit(f"usage: {sys.argv[0]} KEYWORD")

keyword = sys.argv[1].lower()
for line in sys.stdin:
    if keyword in line.lower():
        print(line, end="")
```

```text
$ printf 'ok\nError one\nok2\n' | python3 filter.py error
Error one
```
</details>

**Exercise 2.** Write a script that prints its version info and platform, then exits with code 0 if the platform is linux and 3 otherwise. Check the code with `echo $?`.

<details>
<summary>Show a worked solution</summary>

```python
import sys

print(sys.version.split()[0], "on", sys.platform)
sys.exit(0 if sys.platform == "linux" else 3)
```

```text
$ python3 plat.py; echo "exit=$?"
3.12.3 on linux
exit=0
```
</details>

**Exercise 3.** Make a script that writes "OK" to stdout and "WARN disk low" to stderr, then run it redirecting only stdout to `/dev/null` so the warning still shows.

<details>
<summary>Show a worked solution</summary>

```python
import sys

print("OK")
print("WARN disk low", file=sys.stderr)
```

```text
$ python3 warn.py > /dev/null
WARN disk low
```
</details>

## Check Yourself

**Why do errors belong on stderr rather than stdout?**

<details>
<summary>Show answer</summary>

So redirected or piped output stays clean machine-readable data while diagnostics still reach the user's terminal.
</details>

**What does `sys.exit("msg")` do exactly?**

<details>
<summary>Show answer</summary>

Prints the message to stderr and exits with status code 1.
</details>

**How does a script accept either a filename argument or piped stdin?**

<details>
<summary>Show answer</summary>

Check `len(sys.argv)`: open the named file if present, otherwise iterate `sys.stdin`. One loop then handles both sources.
</details>
