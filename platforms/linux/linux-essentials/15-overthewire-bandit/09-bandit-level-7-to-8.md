# Bandit Level 7 to Level 8: The Word Next to the Password


## Level objective
In `data.txt` (a huge text file), the password sits on the line containing the word `millionth`. Extract it. Confirm the exact goal on the official level page.

## Concepts practiced
`grep` as a precision instrument on large files, and the habit of never opening giant files whole.

## Background
`data.txt` has on the order of a million lines. `cat` would bury your terminal; even `less` makes you scroll a haystack. But you know something better than the password's location: you know a *word on the same line*. That is a `grep` pattern.

One refinement separates tidy from sloppy: `grep millionth data.txt` prints the whole line, password and marker word together. If you want just the credential, remember `grep` prints matching **lines** by default; the password is simply the last whitespace-separated field, so `awk '{print $NF}'` can trim it. For the game, the full line is fine.

## Relevant commands
```bash
ls -la
wc -l data.txt
grep millionth data.txt
grep millionth data.txt | awk '{print $NF}'
```

## Hints (in increasing order)
1. Do not read the file; search it.
2. The marker word is your pattern.
3. `grep` finds the line; the password is on it.

## Solution explanation
`grep millionth data.txt` prints the single line containing the marker word, which ends with the next password. Log in to the next level with it.

## Why it works
`grep` streams the file line by line and prints only lines matching the pattern, so a million-line file costs one fast pass and one line of output. This is the core loop of all log analysis: know a marker, extract the line, read the value.

## Check yourself
**Q1.** Why is `grep` on a million-line file fast, while opening the same file in an editor is not?

<details>
<summary>Show answer</summary>

`grep` streams: it reads, tests, and discards line by line, never holding the file. Editors load and index the whole document for display and editing.
</details>

**Q2.** What would `grep -c millionth data.txt` tell you, and when is the count more useful than the line?

<details>
<summary>Show answer</summary>

How many lines match. When validating assumptions: if you expected exactly one match, a count of 0 or 3 changes your next move before you read anything.
</details>

## Official verification
[Bandit Level 7 → Level 8](https://overthewire.org/wargames/bandit/bandit8.html)
