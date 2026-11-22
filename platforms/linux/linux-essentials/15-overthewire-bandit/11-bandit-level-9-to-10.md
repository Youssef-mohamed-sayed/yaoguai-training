# Bandit Level 9 to Level 10: Extract Readable Strings


## Level objective
Find the human-readable string described by the official challenge in a file containing non-text data.

## Concepts practiced
`strings`, `grep`, binary inspection, and filtering.

## Relevant commands
```bash
file data.txt
strings data.txt
strings data.txt | grep 'pattern'
```

## Hints (in increasing order)
1. The file is not ordinary plain text.
2. `strings` prints sequences of printable characters from binary data.
3. Filter those sequences using the condition in the official level description.

## Solution explanation
Use `strings` to extract readable sequences, then `grep` to narrow the output to the pattern described by the official game. Do not publish the resulting credential.

## Why it works
Binary formats can contain embedded text. `strings` extracts printable runs, which can then be searched.

## Lessons learned
Binary files can contain useful textual metadata, but `strings` is not a full parser.

## Official verification
[Bandit Level 9 → Level 10](https://overthewire.org/wargames/bandit/bandit10.html)
