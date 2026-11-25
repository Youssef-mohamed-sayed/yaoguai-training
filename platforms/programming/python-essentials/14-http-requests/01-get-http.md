# HTTP GET with requests

## Learning Objectives

- Make GET requests with parameters, headers, and timeouts.
- Interpret status codes, headers, and response bodies.
- Handle network failures without crashing.

## Introduction

HTTP is a request-response protocol: the client sends a method, path, headers, and optional body; the server answers with a status code, headers, and a body. Status classes: 2xx success, 3xx redirect, 4xx your fault, 5xx their fault.

`requests` is the friendly third-party HTTP library (the stdlib's `urllib` works but is clunkier). It is the one non-stdlib dependency this course uses:

```bash
python -m pip install requests
```

## The Minimal Request - and the Timeout Rule

```python
import requests

response = requests.get("https://httpbin.org/get", timeout=5)
print(response.status_code)    # 200
print(response.headers["content-type"])  # application/json
print(response.json())         # parsed body, since httpbin answers JSON
```

**Every request gets a `timeout`.** Without one, `requests` waits forever - one hung server freezes your tool permanently. A connect+read timeout of a few seconds is the norm for scripts.

## Parameters, Headers, and Response Details

```python
response = requests.get(
    "https://httpbin.org/get",
    params={"q": "python", "page": 2},        # becomes ?q=python&page=2
    headers={"User-Agent": "study-script/1.0"},
    timeout=5,
)
print(response.url)            # https://httpbin.org/get?q=python&page=2
print(response.text[:80])      # raw body as text
print(response.elapsed)        # how long it took
```

Never build query strings by string concatenation (`url + "?" + key + "=" + value`): special characters break or - worse - smuggle extra parameters. `params=` encodes correctly.

Inspect what came back before using it:

```python
response = requests.get("https://httpbin.org/status/404", timeout=5)
if response.status_code == 200:
    data = response.json()
elif response.status_code == 404:
    print("not found")
else:
    response.raise_for_status()   # raises HTTPError for 4xx/5xx
```

`response.json()` raises `requests.exceptions.JSONDecodeError` when the body is not JSON - check `content-type` or wrap it.

## Handling Failure

Networks fail in ways that are not HTTP errors at all. Catch the request exceptions:

```python
import requests

try:
    response = requests.get("https://unreachable.example", timeout=5)
    response.raise_for_status()
except requests.Timeout:
    print("server too slow")
except requests.ConnectionError:
    print("host unreachable or DNS failed")
except requests.HTTPError as error:
    print("bad status:", error.response.status_code)
except requests.RequestException as error:
    print("request failed:", error)
```

Order matters: the specific exceptions come before the base `RequestException`, which catches everything `requests` raises.

## Common Mistakes

- No timeout - the number one production hang in Python scripts.
- Concatenating query strings by hand instead of using `params`.
- Calling `.json()` on error pages or non-JSON bodies without checking.
- Ignoring status codes; a 404 page is still a "successful" HTTP exchange unless you check.

## Key Takeaways

- `requests.get(url, params=..., headers=..., timeout=...)`; always set a timeout.
- Check `status_code` (or `raise_for_status`) before trusting the body; `.json()` only on JSON.
- Catch `Timeout`, `ConnectionError`, `HTTPError`, then `RequestException` as the catch-all.

## Practice Exercises

**Exercise 1.** GET `https://httpbin.org/get` with a custom User-Agent and print the JSON's `headers` field to confirm the server saw it.

<details>
<summary>Show a worked solution</summary>

```python
import requests

r = requests.get("https://httpbin.org/get",
                 headers={"User-Agent": "my-first-script/0.1"}, timeout=5)
print(r.json()["headers"]["User-Agent"])
```

```text
my-first-script/0.1
```
</details>

**Exercise 2.** Fetch `https://httpbin.org/status/418` and print a friendly message using `raise_for_status` inside a try/except.

<details>
<summary>Show a worked solution</summary>

```python
import requests

try:
    r = requests.get("https://httpbin.org/status/418", timeout=5)
    r.raise_for_status()
except requests.HTTPError as e:
    print(f"server said {e.response.status_code} - yes, 418 is 'I'm a teapot'")
```

```text
server said 418 - yes, 418 is 'I'm a teapot'
```
</details>

**Exercise 3.** Request `https://httpbin.org/delay/10` (which sleeps 10 seconds) with `timeout=2` and catch the timeout. Note how long your script actually waited.

<details>
<summary>Show a worked solution</summary>

```python
import time
import requests

start = time.perf_counter()
try:
    requests.get("https://httpbin.org/delay/10", timeout=2)
except requests.Timeout:
    print(f"gave up after {time.perf_counter() - start:.1f}s")
```

```text
gave up after 2.0s
```

Without the timeout, the script would wait the full 10 seconds (or forever on a dead host).
</details>

## Check Yourself

**What do the status classes 2xx, 4xx, and 5xx mean?**

<details>
<summary>Show answer</summary>

2xx success, 4xx client-side problem (bad request, auth, not found), 5xx server-side failure.
</details>

**Why pass `params=` a dict instead of building the query string manually?**

<details>
<summary>Show answer</summary>

requests URL-encodes keys and values correctly; manual concatenation breaks on special characters and invites parameter-smuggling bugs.
</details>

**What exception family covers all `requests` failures?**

<details>
<summary>Show answer</summary>

`requests.RequestException` - with `Timeout`, `ConnectionError`, and `HTTPError` as the commonly caught subclasses.
</details>
