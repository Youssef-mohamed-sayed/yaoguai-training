# Parsing Authentication Logs with Regex

## Learning Objectives

- Extract structured data from messy log lines with regular expressions.
- Count and rank indicators (IPs, users) from an auth log.
- Produce a small incident-style report.

## Introduction

Module 09 built an auth-log analyzer with string splitting. Real logs are messier: usernames with spaces, IPv6, "invalid user" variants. **Regular expressions** match the *pattern* of a line instead of its exact layout, and Python's `re` module makes them practical.

## Regex Essentials for Logs

```python
import re

line = "Oct 10 03:14:15 srv sshd[812]: Failed password for invalid user admin from 203.0.113.7 port 51122 ssh2"

ip = re.search(r"\d{1,3}(?:\.\d{1,3}){3}", line)
print(ip.group())    # 203.0.113.7

match = re.search(r"Failed password for (?:invalid user )?(\S+) from (\S+)", line)
print(match.group(1), match.group(2))   # admin 203.0.113.7
```

The vocabulary that covers log work:

- `\d` digit, `\w` word char, `\s` whitespace; `\S` non-space. `{1,3}` repeats, `+` one or more, `*` zero or more.
- `(...)` captures a group; `(?:...)` groups without capturing; `?` makes the previous piece optional.
- Raw strings (`r"..."`) keep backslashes literal - always use them for regex.
- `re.search` finds the first match anywhere; `re.findall` returns all matches; `re.fullmatch` requires the whole string to match.

Compile once when the pattern runs in a hot loop: `FAIL = re.compile(r"...")` then `FAIL.search(line)`.

## From Lines to a Report

```python
import re
from collections import Counter

FAIL = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+)")

def analyze(path):
    users, ips = Counter(), Counter()
    total = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            match = FAIL.search(line)
            if not match:
                continue
            total += 1
            user, ip = match.groups()
            users[user] += 1
            ips[ip] += 1
    return total, users, ips

total, users, ips = analyze("auth.log")
print(f"{total} failed logins")
print("\nTop source IPs:")
for ip, n in ips.most_common(5):
    print(f"  {ip:<16} {n}")
print("\nTop targeted users:")
for user, n in users.most_common(5):
    print(f"  {user:<16} {n}")
```

```text
412 failed logins

Top source IPs:
  203.0.113.7      301
  198.51.100.23     97

Top targeted users:
  root             280
  admin             76
```

A single source hammering `root` hundreds of times is the brute-force signature this report surfaces. Natural next steps: flag IPs above a threshold, convert counts to a blocklist, or timestamp the first/last attempt per IP.

## Common Mistakes

- Forgetting raw strings, so `\d` becomes an escape-sequence accident.
- Greedy `.*` swallowing more than intended; prefer specific classes (`\S+`) or non-greedy `.*?`.
- Assuming every line matches; always handle `match is None`.
- Recompiling the pattern inside the loop.

## Key Takeaways

- Regex matches shape, not layout; `re.search` + capture groups extract fields from irregular lines.
- Compile patterns once, use raw strings, and always handle non-matching lines.
- `Counter.most_common` turns extracted fields into a ranked report in one line.

## Practice Exercises

**Exercise 1.** Write a regex that captures the user and IP from both "Failed password for root from 1.2.3.4 ..." and "Failed password for invalid user bob from 5.6.7.8 ...". Test it on both.

<details>
<summary>Show a worked solution</summary>

```python
import re

FAIL = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+)")
for line in ("Failed password for root from 1.2.3.4 port 1 ssh2",
             "Failed password for invalid user bob from 5.6.7.8 port 2 ssh2"):
    print(FAIL.search(line).groups())
```

```text
('root', '1.2.3.4')
('bob', '5.6.7.8')
```
</details>

**Exercise 2.** Extract every IPv4-looking address from a line with `findall`.

<details>
<summary>Show a worked solution</summary>

```python
import re

line = "denied from 10.0.0.5 to 10.0.0.1 via 192.168.1.1"
print(re.findall(r"\d{1,3}(?:\.\d{1,3}){3}", line))
```

```text
['10.0.0.5', '10.0.0.1', '192.168.1.1']
```

(This pattern accepts impossible octets like 999; tightening it is a nice follow-up exercise.)
</details>

**Exercise 3.** Extend the analyzer to print only IPs with more than 100 failures, labeled "BRUTE FORCE SUSPECT".

<details>
<summary>Show a worked solution</summary>

```python
for ip, n in ips.most_common():
    if n <= 100:
        break
    print(f"BRUTE FORCE SUSPECT {ip:<16} {n}")
```

`most_common` is already sorted, so `break` at the first miss keeps it O(results).
</details>

## Check Yourself

**What does `(?:invalid user )?` do in the pattern?**

<details>
<summary>Show answer</summary>

It optionally matches the literal "invalid user " without capturing it, so both log variants yield the same two captured groups.
</details>

**Why compile a regex that runs inside a loop?**

<details>
<summary>Show answer</summary>

`re.compile` parses the pattern once; the loop then reuses the compiled object instead of re-parsing the pattern for every line.
</details>

**What does `Counter.most_common(5)` return?**

<details>
<summary>Show answer</summary>

A list of the five `(item, count)` pairs with the highest counts, in descending order.
</details>
