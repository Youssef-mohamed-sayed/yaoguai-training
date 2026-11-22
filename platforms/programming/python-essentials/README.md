# Python Programming Essentials

**Yaoguai Cybersecurity Learning Platform**

A beginner-friendly Python 3 course progressing from first programming concepts to practical, safe cybersecurity-oriented scripts.

## Audience and Prerequisites

For learners with little or no programming experience. Basic computer and file-management skills are helpful; no prior coding experience is required.

## Learning Outcomes

You will learn to write Python programs, use variables and data structures, control program flow, define functions, process files, handle exceptions, use modules and libraries, debug unfamiliar code, solve problems, and build small authorized security-analysis tools.

## Recommended Order

Complete modules in numerical order:

1. [Introduction to Python](01-introduction-to-python/README.md)
2. [Python Setup](02-python-setup/README.md)
3. [Syntax, Variables, and Types](03-syntax-variables-types/README.md)
4. [Operators and Expressions](04-operators-expressions/README.md)
5. [Conditional Statements](05-conditionals/README.md)
6. [Loops and Iteration](06-loops-iteration/README.md)
7. [Functions and Scope](07-functions-scope/README.md)
8. [Data Structures](08-data-structures/README.md)
9. [Problem-Solving](09-problem-solving/README.md)
10. [File Handling](10-file-handling/README.md)
11. [Exceptions and Error Handling](11-exceptions/README.md)
12. [Modules, Packages, and Libraries](12-modules-packages/README.md)
13. [Working with os and sys](13-os-sys/README.md)
14. [HTTP Requests with requests](14-http-requests/README.md)
15. [Network Programming with socket](15-sockets/README.md)
16. [Reading and Debugging Code](16-reading-debugging/README.md)
17. [Practical Cybersecurity Scripts](17-security-scripts/README.md)
18. [Python Mini Projects](18-mini-projects/README.md)
19. [Review and Further Learning](19-course-review/README.md)

## Quick Setup

Install Python 3 from https://www.python.org/downloads/ or your Linux distribution's package manager.

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

Install the third-party `requests` package when needed:

```bash
python -m pip install requests
```

Save dependencies with `python -m pip freeze > requirements.txt`; restore them with `python -m pip install -r requirements.txt`.

## Tools

- Python 3
- PowerShell or a Linux terminal
- A text editor or IDE
- A practice directory with disposable sample files
- `requests` for HTTP lessons (third-party)

## Practical Projects

TCP port checker for localhost/authorized labs; sample log parser; directory inventory; file hash calculator; safe backup utility; HTTP request inspector; password-strength heuristic; JSON analyzer; HTTP status checker.

## Safety

Only test systems you own or are explicitly authorized to assess. Keep network exercises on localhost or instructor-approved targets. Use narrow scope and timeouts. Make file automation non-destructive by default. Never hardcode or log secrets.

## Supplementary Resources

- **Python Introduction Video** — https://youtu.be/eeRw__TlgmQ
- **W3Schools Python Tutorial** — https://www.w3schools.com/python/
- **Python Practice Playlist** — https://www.youtube.com/watch?v=CnFaB06cHH0&list=PLDoPjvoNmBAxCjHi-HIfNoZrMkfbuvVDY
- **W3Schools Python Exercises** — https://www.w3schools.com/python/python_exercises.asp
- Python official documentation — https://docs.python.org/3/
- Python tutorial — https://docs.python.org/3/tutorial/
- `socket` — https://docs.python.org/3/library/socket.html
- `os` — https://docs.python.org/3/library/os.html
- `sys` — https://docs.python.org/3/library/sys.html
- Requests — https://requests.readthedocs.io/

The supplied videos are listed as supplementary resources; this course does not claim to have watched or verified them.

## Completion

Use [COURSE-CHECKLIST.md](COURSE-CHECKLIST.md) to track topic coverage and completion.
