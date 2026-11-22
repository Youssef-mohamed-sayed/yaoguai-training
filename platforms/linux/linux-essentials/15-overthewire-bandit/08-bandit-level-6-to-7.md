# Bandit Level 6 to Level 7: Search by Ownership and Size


## Level objective
Locate a file using the owner, group, and size conditions stated by the official game.

## Concepts practiced
UID/GID ownership, `find -user`, `find -group`, and `find -size`.

## Relevant commands
```bash
find / -type f -user bandit7 -group bandit6 -size 33c 2>/dev/null
stat /path/to/candidate
```

## Hints (in increasing order)
1. The target may not be under the current home directory.
2. Combine owner, group, and size tests in one search.
3. Permission-denied messages are expected when searching system-wide as an unprivileged user; suppress them only if you understand the limitation.

## Solution explanation
Search the filesystem for a regular file satisfying all official ownership and size conditions. Verify the candidate's metadata with `stat`, then read it if permitted.

## Why it works
`find` can filter on ownership and size without requiring you to know the file's path in advance.

## Lessons learned
File ownership is metadata, not a filename property. A search with suppressed errors may be incomplete.

## Official verification
[Bandit Level 6 → Level 7](https://overthewire.org/wargames/bandit/bandit7.html)
