# Bandit Level 8 to Level 9: The Line That Appears Once


## Level objective
In `data.txt`, the password is on the only line that occurs exactly once. Find it. Confirm the exact goal on the official level page.

## Concepts practiced
The `sort | uniq` idiom, and *why the sort is mandatory*.

## Background
The file is full of repeated decoy lines; the real line is unique. `uniq -u` prints lines that occur only once, but with a catch that bites everyone once: `uniq` compares **adjacent** lines only. In an unsorted file, the same line appearing at positions 5 and 9000 looks "unique" at each position. Sorting first gathers all copies of every line together, making `uniq`'s counts globally true.

So the classic pipeline is two stages: `sort` to group, `uniq -u` to keep singletons. Expect the sort of a million-line file to take a moment; that is normal.

## Relevant commands
```bash
sort data.txt | uniq -u
```

## Hints (in increasing order)
1. Duplicates must stand next to each other to be counted.
2. `sort` before `uniq`.
3. `-u` keeps lines seen exactly once.

## Solution explanation
`sort data.txt | uniq -u` prints the one unique line, which contains the next password. Log in to the next level with it.

## Why it works
Sorting imposes an order in which identical lines are necessarily adjacent. With duplicates grouped, `uniq -u`'s local adjacency test becomes a correct global answer: any line with no neighbor equal to itself occurs exactly once in the whole file.

## Check yourself
**Q1.** What would `uniq -u data.txt` (unsorted) most likely print, and why is it wrong?

<details>
<summary>Show answer</summary>

Almost every line, because repeated lines are scattered and each isolated occurrence looks unique to `uniq`'s adjacency check. The count would claim hundreds of "unique" lines that are not.
</details>

**Q2.** How would you instead get the *most common* line in a file?

<details>
<summary>Show answer</summary>

`sort file | uniq -c | sort -nr | head -n 1`: count each distinct line, then rank numerically descending and take the top. (Same idiom as the log-analysis module.)
</details>

## Official verification
[Bandit Level 8 → Level 9](https://overthewire.org/wargames/bandit/bandit9.html)
