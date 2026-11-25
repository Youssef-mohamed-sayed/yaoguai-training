# Installing Python 3

## Learning Objectives

- Install a current Python 3 on Linux, macOS, or Windows.
- Verify the installation and tell Python 2 apart from Python 3.
- Understand what `python` versus `python3` and `py` point to on each platform.

## Introduction

Every example in this course assumes Python 3.10 or newer. Python 2 reached end of life in January 2020 and must never be used for new work; if a tutorial shows `print "hello"` without parentheses, it is Python 2 and you should close it.

## Linux

Most distributions ship Python 3 preinstalled. Check first:

```text
$ python3 --version
Python 3.12.3
```

If it is missing or too old, install through your package manager:

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install python3 python3-pip python3-venv

# Fedora / RHEL
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

The `python3-venv` package matters: Debian and Ubuntu split it out, and without it you cannot create virtual environments (module 02 lesson 3).

## macOS

The cleanest route is Homebrew:

```bash
brew install python@3.12
```

This provides `python3` and `pip3` without touching the Python that macOS keeps for its own tools. Never modify or delete the system Python at `/usr/bin/python3`.

## Windows

Install from python.org or the Microsoft Store. The python.org installer has one critical checkbox:

- **Check "Add python.exe to PATH"** on the first screen. If you skip it, the terminal will not find Python.

Windows also installs the `py` launcher, which is often the most reliable command:

```text
C:\> py --version
Python 3.12.4
C:\> py -3.11 --version
Python 3.11.9
```

`py` can select among installed versions, which is why many Windows users prefer it over `python`.

## Verify the Installation

Three commands should all work:

```text
$ python3 --version
Python 3.12.3
$ python3 -c "import sys; print(sys.executable)"
/usr/bin/python3
$ python3 -m pip --version
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

The second tells you *which* interpreter you are actually running - essential once several versions coexist. The third confirms pip belongs to the same Python; always run pip as `python3 -m pip` rather than a bare `pip`, so packages land in the interpreter you think they do.

## Common Mistakes

- Installing Python but forgetting "Add to PATH" on Windows, then concluding the install failed.
- Using `pip install` and `python3 script.py` from different installations, so the script cannot find the package it just installed. `python3 -m pip` prevents this.
- Running scripts with `python` and silently getting Python 2 on an older system.

## Key Takeaways

- Python 3.10+ is required; Python 2 is dead and should be avoided entirely.
- Verify with `--version`, `sys.executable`, and `python3 -m pip --version` so you know which interpreter and which pip you have.
- On Windows, tick "Add to PATH" and learn the `py` launcher.

## Practice Exercises

**Exercise 1.** Print your Python version, the interpreter's full path, and your pip version. Record all three.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 --version
Python 3.12.3
$ python3 -c "import sys; print(sys.executable)"
/usr/bin/python3
$ python3 -m pip --version
pip 24.0 from ... (python 3.12)
```

On Windows use `py` in place of `python3` if `python` is not on PATH.
</details>

**Exercise 2.** Start the REPL and print `sys.version_info`. Confirm the major version is 3 and the minor version is 10 or higher.

<details>
<summary>Show a worked solution</summary>

```text
>>> import sys
>>> sys.version_info
sys.version_info(major=3, minor=12, micro=3, releaselevel='final', serial=0)
>>> sys.version_info >= (3, 10)
True
```
</details>

**Exercise 3.** Find out how many Python interpreters your system has: run `which -a python3 python` (Linux/macOS) or `where python py` (Windows) and explain each path listed.

<details>
<summary>Show a worked solution</summary>

```text
$ which -a python3 python
/usr/bin/python3
```

One entry means a single system Python. Multiple entries (for example `/usr/local/bin/python3` before `/usr/bin/python3`) mean several installs; the first one wins because the shell searches PATH left to right.
</details>

## Check Yourself

**Why should you run pip as `python3 -m pip` instead of plain `pip`?**

<details>
<summary>Show answer</summary>

It guarantees the packages install into the same interpreter you run scripts with, avoiding the classic "installed but ImportError" mismatch.
</details>

**What is the `py` command on Windows for?**

<details>
<summary>Show answer</summary>

It is the Python launcher: it finds installed Pythons even without PATH entries and can select a version explicitly (`py -3.11`).
</details>

**A tutorial's example shows `print "hello"`. What does that tell you?**

<details>
<summary>Show answer</summary>

It is Python 2 code. Python 3 requires `print("hello")` with parentheses; the tutorial is outdated.
</details>
