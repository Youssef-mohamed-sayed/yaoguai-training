# JSON Data Analyzer

## Learning Objectives

- Understand the purpose and vocabulary of this topic.
- Read and modify the examples.
- Apply the concept in a small independent exercise.

## Introduction

`json.load()` parses a file into Python values. Parsing does not validate the application's schema. Check that the top-level object and each field have the expected type before using them.

## Core Concepts

Work through the explanation before running the example. Identify the input, the operation performed, and the output or side effect. Python is case-sensitive; indentation defines blocks; values have types; and errors should be handled at the point where the program can respond meaningfully.

## Syntax and Example

```python
import json
from collections import Counter

with open("events.json", encoding="utf-8") as file:
    data = json.load(file)
if not isinstance(data, list):
    raise ValueError("expected a JSON array")

counts = Counter()
for item in data:
    if isinstance(item, dict) and isinstance(item.get("severity"), str):
        counts[item["severity"].lower()] += 1
print(dict(counts))
```

## Practical Exercise

Analyze the supplied sample array, report repeated source IPs, and test invalid JSON and unexpected object shapes.

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
