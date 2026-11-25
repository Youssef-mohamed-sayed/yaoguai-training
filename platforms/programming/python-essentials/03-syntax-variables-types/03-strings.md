# Strings and Text Processing

## Learning Objectives

- Create, index, and slice strings confidently.
- Use the core string methods for searching, splitting, joining, and cleaning text.
- Format output with f-strings and convert between strings and bytes.

## Introduction

Text is the most common data a script touches: log lines, URLs, usernames, file contents, protocol banners. Python strings are **immutable sequences of Unicode characters**. Immutable means every "modification" method returns a new string; the original never changes:

```python
host = "Example.COM"
print(host.lower())   # example.com
print(host)           # Example.COM - unchanged
```

## Indexing and Slicing

Positions count from 0; negative indexes count from the end. Slices are `start:stop:step`, with `stop` excluded:

```python
s = "GET /admin HTTP/1.1"
print(s[0])        # G
print(s[-7:])      # HTTP/1.1
print(s[4:11])     # /admin
print(s[::2])      # GTadm TP1.
print(s[::-1])     # 1.1/PTTH nimda/ TEG - reversed
```

Slicing never raises `IndexError` for out-of-range bounds; it just returns what overlaps. That makes `line[:80]` a safe way to truncate anything.

## The Methods You Will Use Daily

```python
line = "  192.168.1.10 - Failed password for admin  "
line.strip()                    # '192.168.1.10 - Failed password for admin'
line.strip().split(" - ")       # ['192.168.1.10', 'Failed password for admin']
" ".join(["perm", "denied"])    # 'perm denied'
line.count("a")                 # 4
"error" in line.lower()         # False (substring test)
line.strip().startswith("192")  # True
"user=alice".split("=")         # ['user', 'alice']
"abc".replace("b", "X")         # 'aXc'
```

The `split`/`join` pair is the workhorse of log parsing: split a line into fields, pick the ones you want, join results back for output. For fixed-format or messy text, regular expressions (the `re` module) take over; there is a dedicated treatment in the log-parser project in module 17.

## f-Strings: Formatting Done Right

Prefixed with `f`, a string interpolates any expression inside braces:

```python
user = "alice"
fails = 5
print(f"{user} failed {fails} times ({fails / 10:.1%})")
print(f"{'host':<12} {'port':>5}")
print(f"{'web-1':<12} {443:>5}")
```

```text
alice failed 5 times (50.0%)
host          port
web-1           443
```

Format specifiers after `:` control width, alignment (`<` left, `>` right, `^` center), and precision (`.2f` two decimals, `.1%` percent). Aligned columns make scan output and reports readable.

## Strings and Bytes

Networks and files often deal in **bytes**, not text. A `bytes` literal looks like `b"GET"`. Convert with `.encode()` (str to bytes) and `.decode()` (bytes to str); UTF-8 is the default and the right choice almost always:

```python
data = "hello".encode()       # b'hello'
text = data.decode()          # 'hello'
payload = "user=admin".encode("utf-8")
```

Mixing them without converting raises `TypeError`. When a socket hands you bytes, decode once at the boundary and work in text inside the program.

## Common Mistakes

- Forgetting strings are immutable: calling `line.strip()` and then using `line` again unchanged. Capture the return value: `line = line.strip()`.
- Splitting on a single space when data has runs of whitespace. Bare `.split()` (no argument) splits on any whitespace run and drops empties, which is usually what you want for logs.
- Building big strings with `+` in a loop. Collect pieces in a list and `"".join(pieces)` once; it is faster and cleaner.

## Key Takeaways

- Strings are immutable; methods like `strip`, `lower`, `replace` return new strings.
- Slicing (`s[4:11]`, `s[::-1]`) plus `split`/`join` handles most text wrangling.
- f-strings format and align output; encode/decode at the boundary between text and bytes.

## Practice Exercises

**Exercise 1.** From the log line `"192.168.1.10 - - [10/Oct/2024] \"GET /admin HTTP/1.1\" 403"`, extract the IP address and the requested path `/admin` using `split`.

<details>
<summary>Show a worked solution</summary>

```python
line = '192.168.1.10 - - [10/Oct/2024] "GET /admin HTTP/1.1" 403'
ip = line.split(" ")[0]
path = line.split('"')[1].split(" ")[1]
print(ip)    # 192.168.1.10
print(path)  # /admin
```

Fragile splits like this are fine for quick scripts; a real parser would use a regular expression.
</details>

**Exercise 2.** Join the list `["23", "skidoo", "!"]` into one hyphen-separated string, then split it back into the original three items.

<details>
<summary>Show a worked solution</summary>

```python
parts = ["23", "skidoo", "!"]
joined = "-".join(parts)
print(joined)            # 23-skidoo-!
print(joined.split("-")) # ['23', 'skidoo', '!']
```
</details>

**Exercise 3.** Print a small aligned table of three hosts and their open port counts using f-string width specifiers.

<details>
<summary>Show a worked solution</summary>

```python
rows = [("web-1", 3), ("db-1", 1), ("vpn-gw", 2)]
print(f"{'HOST':<10}{'OPEN PORTS':>11}")
for host, count in rows:
    print(f"{host:<10}{count:>11}")
```

```text
HOST      OPEN PORTS
web-1             3
db-1              1
vpn-gw            2
```
</details>

## Check Yourself

**Why does `s.upper()` not change `s`?**

<details>
<summary>Show answer</summary>

Strings are immutable; `upper()` returns a new string. You must assign it back (`s = s.upper()`) to keep the change.
</details>

**What does `"a b  c".split()` return, and how is that different from `.split(" ")`?**

<details>
<summary>Show answer</summary>

`['a', 'b', 'c']`. With no argument, split treats any run of whitespace as one separator; with an explicit `" "`, the double space produces an empty-string element.
</details>

**How do you turn the bytes `b'OK'` into a string?**

<details>
<summary>Show answer</summary>

`b'OK'.decode()` (UTF-8 by default). The reverse is `'OK'.encode()`.
</details>
