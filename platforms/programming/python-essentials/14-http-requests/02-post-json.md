# POST, JSON, and Sessions

## Learning Objectives

- Send form and JSON bodies with POST and read the responses.
- Work with JSON data using `response.json()` and the `json` module.
- Reuse connections and carry cookies with `requests.Session`.

## Introduction

GET asks; POST sends. APIs today speak JSON in both directions, and `requests` makes the common cases one-liners - the skill is in knowing what actually travels on the wire and what can go wrong.

## Sending Data

```python
import requests

# JSON body (APIs):
r = requests.post("https://httpbin.org/post",
                  json={"user": "alice", "role": "admin"}, timeout=5)

# Classic HTML form fields:
r = requests.post("https://httpbin.org/post",
                  data={"user": "alice", "role": "admin"}, timeout=5)
```

`json=` serializes the dict and sets `Content-Type: application/json`; `data=` sends form encoding (`application/x-www-form-urlencoded`). They are not interchangeable - an API expecting JSON will misread form fields. Check the echo:

```python
body = r.json()
print(body["json"])    # {'user': 'alice', 'role': 'admin'}  (when json= was used)
print(body["headers"]["Content-Type"])
```

## Working with JSON

`response.json()` parses the body into dicts/lists. The `json` module handles JSON from anywhere (files, sockets, strings):

```python
import json

payload = {"ports": [22, 80], "tls": True}
text = json.dumps(payload)          # object -> string
print(text)                          # {"ports": [22, 80], "tls": true}
back = json.loads(text)             # string -> object

with open("findings.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)  # readable file output
```

Note `true` lowercase on the wire - JSON is not Python. `dumps`/`loads` work on strings; `dump`/`load` work on files. JSON supports only objects, arrays, strings, numbers, booleans, and null - Python tuples come back as lists, and sets/datetimes need converting first.

## Sessions: Cookies, Headers, and Keep-Alive

A `Session` persists cookies across requests, applies shared headers, and reuses the TCP connection (faster for many requests to one host):

```python
s = requests.Session()
s.headers.update({"User-Agent": "audit-script/1.0"})

s.post("https://httpbin.org/cookies/set/session/abc123", timeout=5)
r = s.get("https://httpbin.org/cookies", timeout=5)
print(r.json())   # {'cookies': {'session': 'abc123'}} - cookie persisted
```

Login flows work the same way: POST credentials once, and the session carries the authenticated cookie to every later request. When scraping or testing several pages on one site, a session is both faster and more polite.

## Common Mistakes

- Sending `data=` to a JSON API and debugging "missing field" errors on the server side.
- Trusting `response.json()` without checking status first - error pages are often HTML.
- Printing or logging full request bodies that contain credentials or tokens.
- Creating a new connection per request in a loop instead of using one `Session`.

## Key Takeaways

- `json=` for API JSON bodies, `data=` for form posts; the server cares about the difference.
- `response.json()` parses replies; the `json` module converts strings/files with `dumps`/`loads`/`dump`/`load`.
- `requests.Session` persists cookies and headers and reuses connections - use it for multi-request flows.

## Practice Exercises

**Exercise 1.** POST a JSON payload `{"name": "test", "tags": ["a", "b"]}` to `https://httpbin.org/post` and print the `json` field of the echo.

<details>
<summary>Show a worked solution</summary>

```python
import requests

r = requests.post("https://httpbin.org/post",
                  json={"name": "test", "tags": ["a", "b"]}, timeout=5)
print(r.json()["json"])
```

```text
{'name': 'test', 'tags': ['a', 'b']}
```
</details>

**Exercise 2.** Save the echo from exercise 1 to `echo.json` with `json.dump(..., indent=2)`, then load it back and print one nested value.

<details>
<summary>Show a worked solution</summary>

```python
import json

data = r.json()
with open("echo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

with open("echo.json", encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded["json"]["tags"][0])   # a
```
</details>

**Exercise 3.** Use a `Session` to set a cookie at `https://httpbin.org/cookies/set/token/xyz` and then read it back from `https://httpbin.org/cookies`.

<details>
<summary>Show a worked solution</summary>

```python
import requests

s = requests.Session()
s.get("https://httpbin.org/cookies/set/token/xyz", timeout=5)
r = s.get("https://httpbin.org/cookies", timeout=5)
print(r.json()["cookies"])
```

```text
{'token': 'xyz'}
```
</details>

## Check Yourself

**What two things does `json=` do that `data=` does not?**

<details>
<summary>Show answer</summary>

It serializes the object to a JSON string and sets the `Content-Type: application/json` header; `data=` sends form encoding instead.
</details>

**What is the difference between `json.dumps` and `json.dump`?**

<details>
<summary>Show answer</summary>

`dumps` returns a string; `dump` writes to a file object. Same for `loads` (string) vs `load` (file).
</details>

**Name two benefits of `requests.Session`.**

<details>
<summary>Show answer</summary>

Persistent cookies/headers across requests and TCP connection reuse (keep-alive), which speeds up repeated calls to one host.
</details>
