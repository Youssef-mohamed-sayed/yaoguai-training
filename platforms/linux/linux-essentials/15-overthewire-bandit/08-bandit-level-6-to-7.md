# Bandit Level 6 to Level 7: Owned by Someone, Somewhere


## Level objective
Somewhere on the whole system is a file owned by user `bandit7`, group `bandit6`, exactly 33 bytes. Find it and read the password. Confirm the exact goal on the official level page.

## Concepts practiced
System-wide `find` with ownership predicates, and disciplined error suppression.

## Background
Now the search space is the entire filesystem, which raises two practical problems you will meet on real servers too.

First, the search must start at `/`: `find /`. Second, most of the tree is unreadable to you, so the output drowns in "Permission denied" lines. The standard move is `2>/dev/null`, which discards stderr while leaving real results on stdout. Use it knowingly: you are searching *everything you may read*, not literally everything, and in this game that is enough.

The predicates translate directly: owner → `-user bandit7`, group → `-group bandit6`, size → `-size 33c`.

## Relevant commands
```bash
find / -type f -user bandit7 -group bandit6 -size 33c 2>/dev/null
```

## Hints (in increasing order)
1. Start the search at `/`.
2. `-user` and `-group` filter by ownership.
3. Send the permission errors to `/dev/null`.

## Solution explanation
The command prints exactly one path. Read it with `cat` for the next password. If you see many permission errors, confirm the `2>/dev/null` is redirecting descriptor 2, not being passed to `find`.

## Why it works
Ownership and size are inode metadata, so `find` answers from directory records and inodes without opening files. The `2>/dev/null` redirection works because errors are emitted on stderr (descriptor 2), a separate stream from the results, the exact split from module 08 lesson 1.

## Check yourself
**Q1.** What do you silently give up when you add `2>/dev/null` to a system-wide search?

<details>
<summary>Show answer</summary>

Knowledge of what was skipped. Directories you cannot enter never report their contents, so the honest summary is "nothing found *that I can read*". On audits, that caveat belongs in the report.
</details>

**Q2.** Why is this search fast even though it starts at `/`?

<details>
<summary>Show answer</summary>

It tests metadata (owner, group, size) rather than reading file contents, so the cost is directory traversal, not data transfer.
</details>

## Official verification
[Bandit Level 6 → Level 7](https://overthewire.org/wargames/bandit/bandit7.html)
