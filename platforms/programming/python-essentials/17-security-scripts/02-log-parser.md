# Log Parser

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

Sample format: `timestamp,severity,source_ip,event`. Parse line by line, count severity and IP occurrences, count failed logins, and skip malformed records. This example summarizes supplied data; it is not a complete intrusion detection system.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
from collections import Counter
from pathlib import Path

def parse_log(path):
    severities, ips = Counter(), Counter()
    failed = malformed = 0
    try:
        with Path(path).open(encoding="utf-8") as file:
            for number, raw in enumerate(file, 1):
                line = raw.strip()
                if not line:
                    continue
                fields = line.split(",")
                if len(fields) != 4:
                    malformed += 1
                    print(f"Skipping malformed line {number}")
                    continue
                timestamp, severity, ip, event = fields
                severities[severity] += 1
                ips[ip] += 1
                if event == "login-failed":
                    failed += 1
    except FileNotFoundError:
        print(f"Missing file: {path}")
        return None
    return severities, ips, failed, malformed
```

## Practical Exercise

Create a sample log with valid and malformed rows. Report repeated IPs and failed logins. For real CSV, use `csv.reader` instead of simple splitting.

**Hints**
1. Write down the expected input and output first.
2. Break the task into small steps or functions.
3. Test a normal case, a boundary case, and invalid input where relevant.

## Common Mistakes

- Copying code without understanding the values and types.
- Assuming input, files, or network services are always available.
- Ignoring error messages or catching every exception indiscriminately.
- Forgetting resource cleanup or safe authorization boundaries.

## Key Takeaways

- Choose the simplest construct that clearly expresses the task.
- Validate assumptions at program boundaries.
- Test the behavior, not merely whether the program starts.

## Further Practice

Modify the example, explain each line in your own words, and link the exercise to the next module.
