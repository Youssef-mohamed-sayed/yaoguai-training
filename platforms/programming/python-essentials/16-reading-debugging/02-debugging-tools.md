# Debugging Tools: pdb and logging

## Learning Objectives

- Step through running code with `pdb` breakpoints.
- Replace scattered prints with the `logging` module's levels and handlers.
- Know when prints, logging, or the debugger is the right tool.

## Introduction

Prints answer "what is this value?"; a debugger answers "what is *everything*, right now?"; logging answers "what happened last Tuesday in production?" This lesson adds `pdb` and `logging` to the print-debugging you already know.

## pdb: Pause and Inspect

Drop a breakpoint into code and run it:

```python
def count_by_ip(lines):
    counts = {}
    for line in lines:
        ip = extract_ip(line)
        breakpoint()          # execution pauses here
        counts[ip] = counts.get(ip, 0) + 1
    return counts
```

```text
$ python3 analyzer.py
> /home/you/analyzer.py(6)count_by_ip()
-> counts[ip] = counts.get(ip, 0) + 1
(Pdb) p ip
'203.0.113.7'
(Pdb) p counts
{}
(Pdb) n          # next line
(Pdb) c          # continue to next breakpoint
(Pdb) l          # list source around here
(Pdb) q          # quit
```

The essential commands: `p expr` (print), `n` (next line), `s` (step into a call), `c` (continue), `l` (list code), `w` (where am I - the stack), `q` (quit). You can also start post-mortem debugging after a crash: `python3 -m pdb script.py` drops you into the debugger at the unhandled exception, with all variables still alive.

## logging: Prints That Grow Up

`print` cannot be turned off, leveled, or redirected without editing code. `logging` can:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
)
log = logging.getLogger("analyzer")

log.debug("raw line: %r", line)        # hidden at INFO level
log.info("processed %d lines", n)
log.warning("skipped malformed line %d", i)
log.error("could not open %s", path)
```

```text
2024-10-10 03:14:15 INFO    processed 1200 lines
2024-10-10 03:14:15 WARNING skipped malformed line 87
```

The levels - DEBUG < INFO < WARNING < ERROR < CRITICAL - let one flag control verbosity: `level=logging.DEBUG` during development, `WARNING` in production, with zero code changes. Send output to a file by adding `filename="analyzer.log"` to `basicConfig`, and errors gain tracebacks with `log.exception("failed")` inside an except block.

## Choosing the Tool

- **One quick value, right now, code you'll delete:** print.
- **"Something is wrong and I don't know where":** pdb breakpoint at the suspicious spot; inspect everything.
- **Anything that must keep working next month, especially servers and cron jobs:** logging.

## Common Mistakes

- Leaving `breakpoint()` in committed code (CI and users will hit it).
- Logging secrets: passwords, tokens, and full request bodies do not belong in logs.
- Using f-strings in logging calls (`log.info(f"{x}")`) - the `%s` style defers formatting until the message is actually emitted.
- Setting no level and wondering where DEBUG messages went (default is WARNING).

## Key Takeaways

- `breakpoint()` + `p/n/s/c/l/w/q` in pdb inspects a live, paused program; `python3 -m pdb` catches crashes post-mortem.
- `logging` levels control verbosity without code edits; `log.exception` captures tracebacks; logs can go to files.
- Prints for the moment, the debugger for confusion, logging for anything that persists.

## Practice Exercises

**Exercise 1.** Put a `breakpoint()` inside a loop summing a list. At the `(Pdb)` prompt, print the running total (`p total`), step with `n` twice, then continue with `c`.

<details>
<summary>Show a worked solution</summary>

```python
total = 0
for x in [10, 20, 30]:
    breakpoint()
    total += x
print(total)
```

```text
(Pdb) p total
0
(Pdb) n
(Pdb) c
> ...breakpoint...
(Pdb) p total
10
```
</details>

**Exercise 2.** Convert a script's prints to logging: INFO for progress, WARNING for skipped lines, and run it once at default level and once with `level=logging.DEBUG`.

<details>
<summary>Show a worked solution</summary>

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-7s %(message)s")
log = logging.getLogger("demo")

lines = ["ok", "", "ok", "bad"]
for i, line in enumerate(lines):
    log.debug("line %d: %r", i, line)
    if line in ("", "bad"):
        log.warning("skipping line %d", i)
        continue
log.info("done")
```

At WARNING level only the two warnings show; at DEBUG everything shows.
</details>

**Exercise 3.** Trigger a `ZeroDivisionError` in a script, rerun it with `python3 -m pdb`, and use `w` and `p` to inspect the crash site.

<details>
<summary>Show a worked solution</summary>

```python
def ratio(a, b):
    return a / b

print(ratio(1, 0))
```

```text
$ python3 -m pdb div.py
...
ZeroDivisionError: division by zero
(Pdb) w
  div.py(4)<module>()
> div.py(2)ratio()
(Pdb) p b
0
```
</details>

## Check Yourself

**What do `n`, `s`, and `c` do in pdb?**

<details>
<summary>Show answer</summary>

`n` runs the next line, `s` steps into the function being called, `c` continues to the next breakpoint or the end.
</details>

**Why prefer `log.info("processed %d", n)` over an f-string in the call?**

<details>
<summary>Show answer</summary>

With %-style args, the string is only formatted if that log level is actually emitted, saving work when messages are suppressed.
</details>

**What is the default logging level, and what does that hide?**

<details>
<summary>Show answer</summary>

WARNING, so DEBUG and INFO messages are hidden until you lower the threshold with basicConfig.
</details>
