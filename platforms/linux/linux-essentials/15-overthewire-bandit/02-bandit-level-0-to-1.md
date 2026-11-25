# Bandit Level 0 to Level 1: Read a File


## Level objective
Log in to the game and read the file in the home directory that holds the next account's password. Confirm the exact current goal on the official level page.

## Concepts practiced
SSH login, home directories, `pwd`, `ls`, and reading a text file. This level is intentionally simple: it is the handshake between you and the game.

## Background
Everything in Bandit happens over a remote shell. When your SSH connection succeeds, you land in the home directory of the account you logged in as, and that account's files are the puzzle. The password you find becomes the login for the *next* account, so the game is a chain: each level's solution unlocks the next level's environment.

Two habits start now and never stop being useful. First, orient before acting: `pwd` and `ls -la` answer "where am I and what is here" in one second. Second, treat every credential as a secret: passwords found in the game go into the next login, never into notes, screenshots, or writeups.

## Relevant commands
```bash
pwd
ls -la
file readme
cat readme
```

## Hints (in increasing order)
1. Confirm that you are logged in as the expected account with `whoami`.
2. List the home directory, including hidden entries.
3. Identify the file type before reading it.

## Solution explanation
After connecting with the official instructions, `ls` shows a file named `readme` in the home directory. `file readme` confirms it is plain text, and `cat readme` prints it. The contents are the next account's password; use them only to log in to the next level, for example:

```bash
ssh bandit1@bandit.labs.overthewire.org -p 2220
```

## Why it works
The challenge is the simplest form of the pattern every level follows: something in the environment holds the credential, and a small, correct command reveals it. `cat` sends a file's contents to standard output; there is nothing between you and the answer except knowing the file is there.

## Check yourself
**Q1.** Why run `file` on an unknown file before `cat`?

<details>
<summary>Show answer</summary>

To learn what the content actually is before displaying it. If it were binary, `cat` could garble your terminal; `file` inspects the content safely first.
</details>

**Q2.** Why does the course refuse to store the level passwords even though they are all over the internet?

<details>
<summary>Show answer</summary>

Two reasons: the operators rotate credentials, so stored passwords go stale and mislead; and the point is performing the inspection yourself. A saved password teaches nothing; finding it teaches the method.
</details>

## Official verification
Use the official [Bandit Level 0 → Level 1 page](https://overthewire.org/wargames/bandit/bandit1.html). The official page is authoritative if details change.
