# Bandit Level 7 to Level 8: Search Text for a Keyword


## Level objective
Use the official level condition to find a value associated with a specified keyword in a text file.

## Concepts practiced
`grep`, line-oriented text search, and context.

## Relevant commands
```bash
grep -n 'keyword' data.txt
grep -i -n 'keyword' data.txt
```

## Hints (in increasing order)
1. The target is associated with a word in a text file.
2. `grep` prints lines that match a pattern.
3. Add `-n` to retain the line number while investigating.

## Solution explanation
Search for the exact keyword stated on the official page. Read the matching line and use the corresponding value as the next credential.

## Why it works
`grep` tests each input line against a pattern and prints matching lines.

## Lessons learned
Filter large text files before manually reading them.

## Official verification
[Bandit Level 7 → Level 8](https://overthewire.org/wargames/bandit/bandit8.html)
