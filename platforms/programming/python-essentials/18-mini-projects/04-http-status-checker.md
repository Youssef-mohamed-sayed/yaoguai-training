# Project: Website Status Checker

## Learning Objectives

- Check a list of URLs for reachability, status, and latency.
- Run checks concurrently and present an uptime-style table.
- Export results as CSV for reporting.

## Introduction

This project watches a list of URLs and reports which respond, how fast, and with what status - the skeleton of every uptime monitor. It combines module 14 (`requests`), concurrency with threads, and CSV output. Point it only at sites you own or have permission to monitor.

## Sequential Core

```python
import time
import requests

def check(url, timeout=5):
    started = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed = time.perf_counter() - started
        return {"url": url, "status": response.status_code,
                "ms": round(elapsed * 1000), "ok": response.status_code < 400, "error": ""}
    except requests.RequestException as error:
        elapsed = time.perf_counter() - started
        return {"url": url, "status": "", "ms": round(elapsed * 1000),
                "ok": False, "error": type(error).__name__}
```

One function, one dict per URL: status, latency in milliseconds, an ok flag, and the exception *type* as a compact error label (`Timeout`, `ConnectionError`).

## Concurrent Checks and a Table

```python
from concurrent.futures import ThreadPoolExecutor

URLS = ["https://example.com", "https://httpbin.org/status/503", "https://no-such-host.invalid"]

with ThreadPoolExecutor(max_workers=10) as pool:
    results = list(pool.map(check, URLS))

print(f"{'URL':<38} {'STATUS':>6} {'MS':>7}  RESULT")
for r in results:
    verdict = "OK" if r["ok"] else (r["error"] or "HTTP " + str(r["status"]))
    print(f"{r['url']:<38} {str(r['status']):>6} {r['ms']:>7}  {verdict}")
```

```text
URL                                     STATUS      MS  RESULT
https://example.com                        200      182  OK
https://httpbin.org/status/503             503      240  HTTP 503
https://no-such-host.invalid                        31  ConnectionError
```

Threads overlap the network waiting: ten slow sites take about as long as one. `max_workers=10` keeps the fan-out polite.

## CSV Export

The `csv` module handles quoting and commas correctly:

```python
import csv

with open("status-report.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "status", "ms", "ok", "error"])
    writer.writeheader()
    writer.writerows(results)
```

`newline=""` is required by the csv module's contract on all platforms. The result opens in any spreadsheet - the difference between a script and a report people use.

## Extensions

- Run it from cron every 5 minutes and append timestamped rows for trend data.
- Alert on *changes* only (module 17's diff pattern): store last state per URL, print/email when `ok` flips.
- Add response-time thresholds (`ms > 2000` -> SLOW verdict).

## Common Mistakes

- Treating any exception as "down" without recording *which* failure - a DNS error and a 503 mean different things.
- No timeout; one dead host stalls the whole batch in sequential mode.
- Writing CSV with f-strings and breaking on the first comma in a URL or title.

## Key Takeaways

- One `check()` returns a uniform result dict for success and failure alike.
- `ThreadPoolExecutor` overlaps network waits; bound the workers.
- `csv.DictWriter` produces real reports; never hand-format CSV.

## Practice Exercises

**Exercise 1.** Run the checker on the three sample URLs and reproduce the table.

<details>
<summary>Show a worked solution</summary>

The 503 row shows HTTP 503 (server reached, unhappy); the invalid host shows `ConnectionError` with an empty status - the table distinguishes "site down" from "site says no."
</details>

**Exercise 2.** Sort the output so failures appear first, then ascending latency.

<details>
<summary>Show a worked solution</summary>

```python
results.sort(key=lambda r: (r["ok"], r["ms"]))
```

`False` (failures) sorts before `True`, and equal groups order by milliseconds.
</details>

**Exercise 3.** Add a timestamp column to the CSV so repeated runs append a history.

<details>
<summary>Show a worked solution</summary>

```python
from datetime import datetime, timezone

stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
for r in results:
    r["ts"] = stamp

with open("history.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["ts", "url", "status", "ms", "ok", "error"])
    if f.tell() == 0:
        writer.writeheader()
    writer.writerows(results)
```

Appending plus the `f.tell() == 0` header trick builds a queryable history file.
</details>

## Check Yourself

**Why record the exception type name rather than the full message?**

<details>
<summary>Show answer</summary>

The class name (`Timeout`, `ConnectionError`) is a stable, compact category for reports; full messages vary and clutter tables (keep them in logs if needed).
</details>

**Why does `newline=""` matter when opening a CSV file for writing?**

<details>
<summary>Show answer</summary>

The csv module manages line endings itself; without it, Windows adds blank lines between rows.
</details>

**What does `pool.map(check, URLS)` give back?**

<details>
<summary>Show answer</summary>

A result per URL in the same order as the input list, with each URL checked on a worker thread.
</details>
