# Virtual Environments and pip

## Learning Objectives

- Explain what a virtual environment is and why every project gets one.
- Create, activate, and deactivate a venv on any platform.
- Install, pin, and reproduce dependencies with pip and `requirements.txt`.

## Introduction

Python packages install into the interpreter's `site-packages` directory. With a single global interpreter, two projects that need different versions of the same library collide, and `sudo pip install` can break your OS's own Python tools. The standard fix is a **virtual environment** (venv): a folder containing a private Python interpreter and its own `site-packages`, so each project's dependencies are isolated and disposable.

## Create and Activate

```bash
python3 -m venv .venv
```

This creates a `.venv` folder in the current directory (the name is a convention; `venv` and `env` are also common). Nothing is active yet. Activation rewrites your shell's PATH so `python` and `pip` resolve inside the environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows cmd
.venv\Scripts\activate.bat
```

The prompt changes to show the environment name:

```text
(.venv) $ which python
/home/you/project/.venv/bin/python
```

Deactivate with `deactivate`. Deleting the `.venv` folder removes the environment completely; your code is untouched. If PowerShell refuses the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

## Installing with pip

Inside an active venv, install packages without `sudo`:

```text
(.venv) $ python -m pip install requests
Collecting requests
  Downloading requests-2.32.3 ...
Successfully installed certifi-2024.8.30 charset-normalizer-3.4.0 idna-3.10 requests-2.32.3 urllib3-2.2.3
```

Useful daily commands:

```bash
python -m pip install requests        # latest version
python -m pip install requests==2.32.3  # exact version (pinning)
python -m pip install --upgrade requests
python -m pip show requests           # version, location, dependencies
python -m pip list                    # everything installed here
python -m pip uninstall requests
```

## Reproducing an Environment with requirements.txt

A project should record exactly what it needs so anyone (including future you and your CI) can rebuild it:

```bash
python -m pip freeze > requirements.txt
```

```text
certifi==2024.8.30
charset-normalizer==3.4.0
idna==3.10
requests==2.32.3
urllib3==2.2.3
```

A fresh machine recreates the whole setup in two commands:

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
```

Commit `requirements.txt` to git; never commit `.venv/` itself - add it to `.gitignore`.

## Common Mistakes

- Installing into the global Python because the venv was created but never activated. Check for the `(.venv)` prefix or `which python` before every `pip install`.
- Committing the `.venv` directory: thousands of machine-specific files that belong nowhere in git.
- `pip freeze` capturing every experiment ever installed in the venv. Keep one venv per project so freeze stays meaningful.
- Using `sudo pip install`, which can overwrite files the OS package manager owns.

## Key Takeaways

- A venv isolates a project's dependencies; create with `python3 -m venv .venv`, activate with `source .venv/bin/activate`.
- Always install with `python -m pip` inside the active environment, never with sudo.
- `pip freeze > requirements.txt` plus `pip install -r` makes environments reproducible.

## Practice Exercises

**Exercise 1.** Create a venv called `.venv`, activate it, and confirm `which python` (or `where python` on Windows) points inside it. Then deactivate and confirm it points back to the system interpreter.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ which python
/home/you/project/.venv/bin/python
(.venv) $ deactivate
$ which python
/usr/bin/python
```
</details>

**Exercise 2.** Inside the active venv, install `requests`, verify with `pip show requests`, then write `requirements.txt` with `pip freeze` and read it.

<details>
<summary>Show a worked solution</summary>

```text
(.venv) $ python -m pip install requests
Successfully installed ... requests-2.32.3 ...
(.venv) $ python -m pip show requests
Name: requests
Version: 2.32.3
...
(.venv) $ python -m pip freeze > requirements.txt
(.venv) $ cat requirements.txt
certifi==2024.8.30
charset-normalizer==3.4.0
idna==3.10
requests==2.32.3
urllib3==2.2.3
```
</details>

**Exercise 3.** Prove reproducibility: delete `.venv`, recreate it, reinstall from `requirements.txt`, and import requests in the REPL.

<details>
<summary>Show a worked solution</summary>

```text
$ rm -rf .venv
$ python3 -m venv .venv && source .venv/bin/activate
(.venv) $ python -m pip install -r requirements.txt
...
(.venv) $ python -c "import requests; print(requests.__version__)"
2.32.3
```

This is the same workflow a teammate or server follows with your project.
</details>

## Check Yourself

**What two things does activating a venv change about your shell?**

<details>
<summary>Show answer</summary>

It rewrites PATH so `python` and `pip` resolve inside the environment, and it changes the prompt to show the environment is active. (Technically it also sets `VIRTUAL_ENV`; the practical effects are the first two.)
</details>

**Why pin exact versions (`==`) in requirements.txt?**

<details>
<summary>Show answer</summary>

So every install gets identical package versions; otherwise a new upstream release can change behavior or break the project between two installs.
</details>

**Why is `sudo pip install` discouraged?**

<details>
<summary>Show answer</summary>

It writes into the OS-managed Python as root and can overwrite or conflict with packages the system's package manager owns, breaking system tools. A venv needs no root at all.
</details>
