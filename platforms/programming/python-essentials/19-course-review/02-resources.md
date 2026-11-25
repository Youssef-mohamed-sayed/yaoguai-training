# Resources and Next Steps

## Learning Objectives

- Know where to look for authoritative answers (and how to read official documentation).
- Choose the next skills to learn after this course.
- Keep a personal practice routine going.

## Introduction

A course ends; the documentation habit is what replaces it. This lesson collects the course's reference links, explains how to read the official Python docs without drowning, and lays out a concrete next-steps path.

## The Course's Reference List

Supplementary resources:

- **Python Introduction Video** - https://youtu.be/eeRw__TlgmQ
- **W3Schools Python Tutorial** - https://www.w3schools.com/python/
- **Python Practice Playlist** - https://www.youtube.com/watch?v=CnFaB06cHH0&list=PLDoPjvoNmBAxCjHi-HIfNoZrMkfbuvVDY
- **W3Schools Python Exercises** - https://www.w3schools.com/python/python_exercises.asp

Official references:

- Python 3 documentation - https://docs.python.org/3/
- The official tutorial - https://docs.python.org/3/tutorial/
- socket module - https://docs.python.org/3/library/socket.html
- os module - https://docs.python.org/3/library/os.html
- sys module - https://docs.python.org/3/library/sys.html
- requests library - https://requests.readthedocs.io/

The videos are listed as resources; this course does not claim to have watched or verified them.

## How to Read Official Documentation

The Python docs are the authority - tutorials (including this course) simplify; the docs define. A practical approach:

1. **Start at the module's top page.** The first paragraphs state the purpose and the two or three functions everyone needs. For `socket`, that is `create_connection` and the socket families.
2. **Use the tutorial for learning, the library reference for answers.** The tutorial (link above) teaches; the library reference is for "what are this function's parameters exactly?"
3. **Check the version.** Docs pages have a version selector; behavior and available functions differ between 3.8 and 3.13. Match it to your interpreter (`python3 --version`).
4. **Search within the page** for the method name; module pages are long by design.

When a third-party answer (Stack Overflow, a blog) disagrees with the docs, the docs win. When the docs and your interpreter disagree, your interpreter is right about *your* machine - recheck versions.

## What to Learn Next

In rough order of payoff for security-oriented scripting:

1. **Testing with `pytest`** - real test files, fixtures, and reports. Your assert matrices already transfer.
2. **argparse in depth** - subcommands (`tool scan ...`, `tool report ...`), which is how professional CLIs are shaped.
3. **The `logging` module's handlers and files** - rotating logs for long-running tools.
4. **Secure configuration** - keeping tokens in environment variables or files with strict permissions, never in code.
5. **Deeper networking** - threading versus asyncio for concurrent I/O, and the scapy/pwntools ecosystems when you are ready for packet crafting and exploit development.
6. **Object-oriented Python** - classes, when a tool outgrows functions and dicts.

## A Sustainable Practice Loop

- One small finished tool per week beats five abandoned ones.
- Keep a `scripts/` directory of everything you build; re-reading your own code in three months is the cheapest progress meter there is.
- Practice platforms (OverTheWire, PicoCTF, TryHackMe) supply legal, structured problems when your own ideas run dry.

## Key Takeaways

- Official docs are the authority; match their version to your interpreter.
- Next skills: pytest, argparse subcommands, logging handlers, secure config, concurrency, then OOP.
- Small finished tools on a steady cadence are the practice that sticks.

## Practice Exercises

**Exercise 1.** Pick one unfamiliar standard-library module (`ipaddress`, `tomllib`, `sqlite3`, or `statistics` are good), read its docs top section, and write a ten-line program demonstrating one feature.

<details>
<summary>Show a worked solution</summary>

```python
import ipaddress

net = ipaddress.ip_network("192.168.1.0/24")
print("hosts:", net.num_addresses - 2)
print("first:", net.network_address + 1)
print("is private:", net.is_private)
print("10.0.0.5 in net:", ipaddress.ip_address("10.0.0.5") in net)
```

```text
hosts: 254
first: 192.168.1.1
is private: True
10.0.0.5 in net: False
```
</details>

**Exercise 2.** Find in the official docs how `requests`-free file downloads could be done with `urllib.request.urlretrieve`, and note one caveat the docs mention.

<details>
<summary>Show a worked solution</summary>

The `urllib.request` docs page documents `urlretrieve(url, filename)` and notes it is a legacy interface that may become deprecated, with `urlopen` recommended for control (headers, timeouts). The exercise is finding this on the page yourself - that navigation is the skill.
</details>

**Exercise 3.** Write your personal next-three-skills list with one concrete mini-project for each.

<details>
<summary>Show a worked solution</summary>

Example: (1) pytest - convert the password checker's asserts into test files; (2) argparse subcommands - merge the scanner and header inspector into one `nettool scan/headers` CLI; (3) logging to files - add rotating logs to the status checker. Yours will differ; the requirement is that each skill gets a project small enough to finish.
</details>

## Check Yourself

**When documentation and a blog post disagree, which wins?**

<details>
<summary>Show answer</summary>

The official docs. And when docs and your interpreter disagree, trust the interpreter and re-check the docs version selector.
</details>

**What is the difference between the Python tutorial and the library reference?**

<details>
<summary>Show answer</summary>

The tutorial teaches concepts in learning order; the library reference is the complete, precise specification you consult for exact behavior and signatures.
</details>

**Why "one small finished tool per week" rather than a big project?**

<details>
<summary>Show answer</summary>

Completion is the skill multiplier: finished tools teach scoping, testing, and polish, while abandoned large projects mostly teach abandonment.
</details>
