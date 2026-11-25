# Project: JSON Log Analyzer

## Learning Objectives

- Parse line-delimited JSON logs and handle malformed entries.
- Aggregate fields into counts, rates, and rankings.
- Emit a summary report as aligned text and as JSON.

## Introduction

Modern services log in JSON - one object per line (JSONL). Each line is self-describing, so parsing is `json.loads` per line instead of regex archaeology. This project reads a JSONL access log and answers: how many requests, which paths are hit hardest, which status classes dominate, which clients talk most.

## Sample Data

Create `access.jsonl`:

```json
{"ts": "2024-10-10T03:14:15Z", "ip": "203.0.113.7", "method": "GET", "path": "/login", "status": 200, "bytes": 512}
{"ts": "2024-10-10T03:14:16Z", "ip": "203.0.113.7", "method": "POST", "path": "/login", "status": 401, "bytes": 128}
{"ts": "2024-10-10T03:14:19Z", "ip": "198.51.100.23", "method": "GET", "path": "/admin", "status": 404, "bytes": 64}
not json at all
{"ts": "2024-10-10T03:15:01Z", "ip": "203.0.113.7", "method": "POST", "path": "/login", "status": 401, "bytes": 128}
```

## The Analyzer

```python
import json
from collections import Counter

def load_events(path):
    events, bad = [], 0
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    return events, bad

def summarize(events):
    return {
        "requests": len(events),
        "by_status_class": Counter(f"{e['status'] // 100}xx" for e in events),
        "top_paths": Counter(e["path"] for e in events).most_common(5),
        "top_clients": Counter(e["ip"] for e in events).most_common(5),
        "failed_logins": sum(1 for e in events if e.get("path") == "/login" and e.get("status") == 401),
    }

events, bad = load_events("access.jsonl")
summary = summarize(events)
print(f"{summary['requests']} requests parsed, {bad} malformed lines skipped")
print("status classes:", dict(summary["by_status_class"]))
print("top paths:", summary["top_paths"])
print("top clients:", summary["top_clients"])
print("failed logins:", summary["failed_logins"])
```

```text
4 requests parsed, 1 malformed lines skipped
status classes: {'2xx': 1, '4xx': 3}
top paths: [('/login', 3), ('/admin', 1)]
top clients: [('203.0.113.7', 3), ('198.51.100.23', 1)]
failed logins: 2
```

Note the defensive details: malformed lines are counted, not fatal; `e.get(...)` guards optional fields; the status *class* is integer division (`401 // 100 == 4`).

## Structured Output

The same summary serializes straight to JSON for other tools:

```python
report = {
    "requests": summary["requests"],
    "by_status_class": dict(summary["by_status_class"]),
    "top_paths": summary["top_paths"],
    "failed_logins": summary["failed_logins"],
}
with open("report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
```

Text for humans, JSON for pipelines - one computation, two presentations.

## Common Mistakes

- Assuming every line parses; real log shippers emit partial lines on crash.
- Keying on fields that are sometimes absent without `.get()`.
- Loading a multi-GB JSONL with `readlines()`; stream line by line.

## Key Takeaways

- JSONL = one `json.loads` per line, with malformed lines counted and skipped.
- `Counter` plus generator expressions turn events into rankings and class totals.
- Present results as text for people and JSON for downstream tools.

## Practice Exercises

**Exercise 1.** Run the analyzer on the sample file and reproduce the output above.

<details>
<summary>Show a worked solution</summary>

Create `access.jsonl` exactly as shown (including the broken line), then run the script. You should see 4 parsed, 1 skipped, and the same counters.
</details>

**Exercise 2.** Add a metric: total bytes served per status class, printed as a dict.

<details>
<summary>Show a worked solution</summary>

```python
bytes_by_class = Counter()
for e in events:
    bytes_by_class[f"{e['status'] // 100}xx"] += e.get("bytes", 0)
print(dict(bytes_by_class))
```

```text
{'2xx': 512, '4xx': 320}
```
</details>

**Exercise 3.** Add a `--format json` flag that prints the report as JSON to stdout instead of text.

<details>
<summary>Show a worked solution</summary>

```python
import argparse, json

parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("--format", choices=["text", "json"], default="text")
args = parser.parse_args()

events, bad = load_events(args.path)
summary = summarize(events)
if args.format == "json":
    print(json.dumps({k: (dict(v) if isinstance(v, Counter) else v)
                      for k, v in summary.items()}, indent=2))
else:
    ...  # existing text output
```

Note Counters convert to dicts for JSON serialization.
</details>

## Check Yourself

**What is JSONL and why is it friendlier than one big JSON array for logs?**

<details>
<summary>Show answer</summary>

One JSON object per line: it streams (parse incrementally, no giant parse), and a corrupt line does not invalidate the whole file.
</details>

**Why use `e.get("bytes", 0)` instead of `e["bytes"]` in aggregations?**

<details>
<summary>Show answer</summary>

Log schemas drift; a missing optional field would otherwise raise KeyError and kill the whole run.
</details>

**What does `status // 100` compute?**

<details>
<summary>Show answer</summary>

The status class digit (4 for 401, 2 for 200), letting you group hundreds of codes into the five HTTP classes.
</details>
