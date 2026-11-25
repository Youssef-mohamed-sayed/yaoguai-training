# Modules and Imports

## Learning Objectives

- Import standard-library and third-party modules in their proper forms.
- Create your own module and understand how Python finds it.
- Choose between `import x`, `from x import y`, and aliased imports.

## Introduction

A **module** is just a `.py` file; importing one runs it and gives you access to its names. A **package** is a directory of modules with an `__init__.py`. The standard library ships hundreds of modules - you have already met `sys`, `os`, `re`, `socket`, `pathlib`, `collections`, `datetime`.

## The Three Import Forms

```python
import socket
socket.socket()                    # qualified use: clear where things come from

from pathlib import Path
Path("app.log")                    # short, but the origin is less visible

import datetime as dt
dt.datetime.now()                  # alias for long names
```

Guidelines:

- `import module` is the default; `module.function()` reads like a citation.
- `from module import name` for one or two heavily used names (`Path`, `Counter`, `defaultdict`).
- Aliases only for established conventions or long names.
- Avoid `from module import *`: it dumps unknown names into your file, shadows your own, and makes linters useless.

## Writing Your Own Module

Any file is importable. Given `netutil.py`:

```python
"""Small network helpers."""

COMMON_PORTS = {22: "ssh", 80: "http", 443: "https"}

def service_name(port):
    return COMMON_PORTS.get(port, "unknown")
```

A sibling file can use it:

```python
import netutil

print(netutil.service_name(443))   # https
```

Python searches for modules in this order: the script's own directory, then `PYTHONPATH`, then the installed `site-packages`. That order explains two classic puzzles: a local file named `random.py` or `socket.py` **shadows the standard library** (never name files after stdlib modules), and a module importable from one directory is invisible from another.

`import` executes the module top to bottom exactly once; later imports reuse the cached module from `sys.modules`. Top-level code in a module (prints, heavy work) therefore runs on import - keep modules quiet at import time and put executable behavior behind the `if __name__ == "__main__":` guard (next lesson).

## Third-Party Packages

Installed into a venv with pip (module 02), then imported like stdlib:

```bash
python -m pip install requests
```

```python
import requests
```

The import system does not distinguish them - only their origin differs. When an `ImportError`/`ModuleNotFoundError` appears, the causes are almost always: the package is not installed in *this* environment (`python -m pip show name` to check), the venv is not activated, or a local file shadows the name.

## Common Mistakes

- Naming a file `email.py`, `json.py`, or `test.py` and breaking the stdlib import of the same name.
- `from x import *` and then debugging names that appear from nowhere.
- Editing a module and re-importing in the same REPL session, wondering why nothing changed (imports are cached; restart the REPL).

## Key Takeaways

- Prefer `import module`; use `from module import name` sparingly; never `import *`.
- Any `.py` file is a module; search order is script directory, PYTHONPATH, site-packages - so local filenames can shadow the stdlib.
- Third-party packages install per-venv with pip and import identically to stdlib.

## Practice Exercises

**Exercise 1.** Import `math` three ways (plain, from-import, alias) and compute `sqrt(144)` with each.

<details>
<summary>Show a worked solution</summary>

```python
import math
print(math.sqrt(144))          # 12.0

from math import sqrt
print(sqrt(144))               # 12.0

import math as m
print(m.sqrt(144))             # 12.0
```
</details>

**Exercise 2.** Create `strutil.py` with a function `shout(text)` returning `text.upper() + "!"`, then import and use it from a second script in the same directory.

<details>
<summary>Show a worked solution</summary>

`strutil.py`:

```python
def shout(text):
    return text.upper() + "!"
```

`main.py`:

```python
import strutil

print(strutil.shout("hello"))   # HELLO!
```

Both files must be in the same directory (or the module must be on the path).
</details>

**Exercise 3.** Deliberately break an import: create `random.py` containing `print("mine!")`, then `import random` in the same directory. Explain what happens, then delete the file.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 -c "import random"
mine!
```

The local `random.py` shadows the standard library's `random` module because the current directory is searched first. Anything needing real randomness would get your file instead. Delete or rename it - never name files after stdlib modules.
</details>

## Check Yourself

**In what order does Python search for a module to import?**

<details>
<summary>Show answer</summary>

The script's directory, then directories on PYTHONPATH, then the installed site-packages.
</details>

**Why is `from module import *` discouraged?**

<details>
<summary>Show answer</summary>

It imports unknown names into your namespace, shadowing existing ones and hiding where each name came from, which breaks readability and static analysis.
</details>

**What happens when a module is imported a second time in the same program?**

<details>
<summary>Show answer</summary>

Nothing - Python serves the cached module object from sys.modules; the file is executed only on the first import.
</details>
