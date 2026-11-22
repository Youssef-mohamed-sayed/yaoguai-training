# Bandit Level 5 to Level 6: Search by File Attributes


## Level objective
Find a file matching the exact attributes listed on the official level page.

## Concepts practiced
`find`, file type, size, permissions, and recursive search.

## Relevant commands
```bash
find . -type f
find . -type f -size 1033c
find . -type f -size 1033c -readable
find . -type f -size 1033c ! -executable
```

## Hints (in increasing order)
1. Search recursively rather than opening files one by one.
2. Translate each stated property into a `find` predicate.
3. Use `-size ...c` when the condition is expressed in bytes.

## Solution explanation
Combine the official criteria as `find` predicates. Confirm the candidate with `stat` and `file` before reading it.

## Why it works
`find` evaluates multiple predicates against each filesystem object; conditions are combined logically.

## Lessons learned
Translate a natural-language requirement into small, testable predicates.

## Official verification
[Bandit Level 5 → Level 6](https://overthewire.org/wargames/bandit/bandit6.html)
