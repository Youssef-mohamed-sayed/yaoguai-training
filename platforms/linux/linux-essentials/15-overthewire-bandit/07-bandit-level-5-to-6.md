# Bandit Level 5 to Level 6: Find by Attributes


## Level objective
Somewhere under `inhere` (with many subdirectories) is a file that is human-readable, exactly 1033 bytes, and not executable. Find it and read the password. Confirm the exact goal on the official level page.

## Concepts practiced
Multi-predicate `find`: searching by attributes when the name and location are unknown.

## Background
Brute force dies here: dozens of nested directories make manual browsing silly. This is precisely what `find` predicates are for (module 10 lesson 1). Translate each clue into a predicate and let the filesystem answer:

- human-readable → check with `file` after the search, or filter by name patterns first;
- 1033 bytes → `-size 1033c` (the `c` means bytes; without it, `find` counts in 512-byte blocks);
- not executable → `! -executable`.

`find` ANDs predicates by default, so stacking them narrows the search to exactly the file you want.

## Relevant commands
```bash
cd inhere
find . -type f -size 1033c ! -executable
find . -type f -size 1033c ! -executable -exec file {} \;
```

## Hints (in increasing order)
1. Translate each property into a `find` test.
2. Size in bytes uses the `c` suffix.
3. Chain `file` onto the result to confirm readability.

## Solution explanation
The first command returns one path (deep in a subdirectory). The second confirms it is ASCII text. `cat` that path for the next password.

## Why it works
`find` evaluates every entry under the starting directory against all predicates and prints only full matches. Size and executability are recorded in each file's metadata (module 03's inode), so the search is a metadata query, not a content scan: instant even over thousands of files.

## Check yourself
**Q1.** Why is `-size 1033` without the `c` wrong?

<details>
<summary>Show answer</summary>

Bare numbers are measured in 512-byte blocks, so `1033` means files of 1033 blocks, about half a megabyte. The `c` suffix selects bytes.
</details>

**Q2.** What does `! -executable` negate, and what is `find`'s default combination rule?

<details>
<summary>Show answer</summary>

It negates the executability test (files you cannot execute). Predicates listed together are ANDed by default; `-o` is OR.
</details>

## Official verification
[Bandit Level 5 → Level 6](https://overthewire.org/wargames/bandit/bandit6.html)
