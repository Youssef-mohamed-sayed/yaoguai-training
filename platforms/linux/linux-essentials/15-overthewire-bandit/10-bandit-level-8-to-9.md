# Bandit Level 8 to Level 9: Find a Unique Line


## Level objective
Identify the line that occurs only once in the supplied data.

## Concepts practiced
Sorting, adjacent duplicate detection, and counting.

## Relevant commands
```bash
sort data.txt | uniq -u
sort data.txt | uniq -c
```

## Hints (in increasing order)
1. The file contains repeated lines.
2. `uniq` compares adjacent lines, so sort the input first.
3. `uniq -u` prints lines that occur exactly once in the sorted stream.

## Solution explanation
Sort the file and pass it to `uniq -u`. Confirm the resulting line matches the official condition.

## Why it works
Sorting places identical lines next to each other, allowing `uniq` to identify repeated and unique records.

## Lessons learned
Understand each pipeline stage; `uniq` alone does not find duplicates that are separated by other lines.

## Official verification
[Bandit Level 8 → Level 9](https://overthewire.org/wargames/bandit/bandit9.html)
