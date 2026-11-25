# Decomposing Problems

## Learning Objectives

- Break a vague task into input, transformation, and output stages.
- Define small functions with clear contracts before writing their bodies.
- Use pseudocode and worked examples to drive implementation.

## Introduction

Beginners stare at a blank file; experienced programmers shrink the problem until the code is obvious. **Decomposition** is the skill: split a task into stages small enough that each one is a short function with a single job.

The universal shape of a script:

```text
INPUT  ->  TRANSFORM  ->  OUTPUT
(read)     (compute)      (report)
```

Name those three before writing anything. "Parse the auth log and report brute-force sources" becomes:

```text
INPUT:     lines from /var/log/auth.log
TRANSFORM: keep 'Failed password' lines, extract the source IP, count per IP
OUTPUT:    top 5 IPs with counts, printed as a table
```

## Contracts Before Bodies

Write the function signature and docstring first. The contract - what goes in, what comes out - forces the design:

```python
def extract_ip(line):
    """Return the source IPv4 address from a 'Failed password' line, or None."""

def count_by_ip(lines):
    """Return a dict mapping IP -> failure count for the given lines."""

def report_top(counts, limit=5):
    """Print the `limit` highest-count IPs as an aligned table."""
```

Now each body is a five-line problem. Test each in the REPL with one hand-made line before connecting them:

```python
line = "Oct 10 03:14:15 srv sshd[812]: Failed password for root from 203.0.113.7 port 51122 ssh2"
print(extract_ip(line))   # 203.0.113.7 - verified before moving on
```

## Worked Example: Wiring It Together

```python
def extract_ip(line):
    if "Failed password" not in line:
        return None
    marker = " from "
    if marker not in line:
        return None
    return line.split(marker)[1].split()[0]

def count_by_ip(lines):
    counts = {}
    for line in lines:
        ip = extract_ip(line)
        if ip:
            counts[ip] = counts.get(ip, 0) + 1
    return counts

def report_top(counts, limit=5):
    for ip, n in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]:
        print(f"{ip:<16} {n:>6}")
```

```python
counts = count_by_ip(open("auth.log"))
report_top(counts)
```

```text
203.0.113.7        412
198.51.100.23       97
```

Each function is testable alone, swappable (regex later), and reusable. That is the payoff of decomposing first.

## Pseudocode and Rubber-Duck Debugging

When a stage still feels big, write pseudocode comments and fill them in:

```python
# for each line
#     skip unless it's a failure
#     pull out the IP
#     bump that IP's counter
```

Explaining the plan line by line - to a comment block, a colleague, or the classic rubber duck - exposes the gaps while they are still cheap.

## Common Mistakes

- Writing the whole script top to bottom before running any of it; the first run then fails in five places at once.
- Functions that secretly do two stages (parse *and* print), which cannot be tested or reused.
- Designing in your head for ten minutes instead of writing one example input and its expected output.

## Key Takeaways

- Name the input, transformation, and output before coding; each stage becomes a small function.
- Write contracts (signature + docstring) first, then test each function on one hand-made example.
- Pseudocode comments turn a blurry stage into fill-in-the-blank lines.

## Practice Exercises

**Exercise 1.** Decompose "read a CSV of users and email everyone whose trial expires within 7 days" into input/transform/output stages with function contracts (no implementation needed).

<details>
<summary>Show a worked solution</summary>

```text
INPUT:     rows from users.csv
TRANSFORM: parse expiry dates, keep rows where 0 <= days_left <= 7
OUTPUT:    one email per selected user

def read_users(path)          -> list of dicts
def expiring_soon(users, days=7) -> filtered list
def send_notice(user)         -> None (prints/sends)
```
</details>

**Exercise 2.** Implement `extract_ip` from this lesson and test it on three lines: one failure, one successful login, and one unrelated line.

<details>
<summary>Show a worked solution</summary>

```python
lines = [
    "Oct 10 03:14:15 srv sshd[812]: Failed password for root from 203.0.113.7 port 51122 ssh2",
    "Oct 10 03:15:02 srv sshd[812]: Accepted password for alice from 198.51.100.9 port 51123 ssh2",
    "Oct 10 03:16:40 srv CRON[901]: (root) CMD (run-parts /etc/cron.hourly)",
]
for line in lines:
    print(extract_ip(line))
```

```text
203.0.113.7
None
None
```
</details>

**Exercise 3.** Write pseudocode comments for "find the longest word in a file", then fill them in with real code.

<details>
<summary>Show a worked solution</summary>

```python
# longest = empty string
# for each line in the file
#     for each word in the line
#         if word is longer than longest
#             longest = word
# print longest

longest = ""
for line in open("words.txt"):
    for word in line.split():
        if len(word) > len(longest):
            longest = word
print(longest)
```
</details>

## Check Yourself

**What are the three stages nearly every script can be split into?**

<details>
<summary>Show answer</summary>

Input (read data), transformation (compute), and output (report).
</details>

**Why write a function's signature and docstring before its body?**

<details>
<summary>Show answer</summary>

The contract forces you to decide inputs and outputs up front, shrinking the body to a small, testable problem.
</details>

**Why test each new function on one hand-made example before wiring the script together?**

<details>
<summary>Show answer</summary>

It isolates bugs to the function just written, instead of debugging five interacting stages on the first full run.
</details>
