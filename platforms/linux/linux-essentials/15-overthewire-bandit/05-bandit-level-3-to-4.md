# Bandit Level 3 to Level 4: Hidden Files


## Level objective
Locate the target file in the directory specified by the official level page.

## Concepts practiced
Hidden filenames, `ls -a`, and directory traversal.

## Relevant commands
```bash
ls
ls -la
find . -maxdepth 2 -type f -print
```

## Hints (in increasing order)
1. Unix-like systems conventionally hide names that begin with a dot.
2. Plain `ls` omits many hidden entries.
3. Use `ls -a` or `find` to include them.

## Solution explanation
Enter the directory described by the official page, list all entries including hidden ones, and read the identified file. Do not assume hidden means protected.

## Why it works
The leading dot is a display convention used by common tools, not an access-control mechanism.

## Lessons learned
Use `ls -la` when inspecting an unfamiliar directory.

## Official verification
[Bandit Level 3 → Level 4](https://overthewire.org/wargames/bandit/bandit4.html)
