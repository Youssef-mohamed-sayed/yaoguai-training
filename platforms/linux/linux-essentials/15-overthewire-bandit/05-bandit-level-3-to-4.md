# Bandit Level 3 to Level 4: The Hidden File


## Level objective
Find and read the hidden file inside the `inhere` directory. Confirm the exact goal on the official level page.

## Concepts practiced
Hidden files (dotfiles), `ls -a`, and remembering that default listings are incomplete by design.

## Background
Enter `inhere` and run `ls`: the directory looks empty. It is not. Any name starting with `.` is hidden from default listings, purely by convention (module 03 lesson 2). The directory contains a file named `.hidden`, and only `ls -a` (or `ls -la` for the long form) shows it.

This is a small puzzle with a large lesson: **every default view is a filtered view.** Attackers hide files with leading dots; administrators hide their own configuration the same way (`.bashrc`, `.ssh`, `.gitignore`). "The directory is empty" should always trigger "empty according to which listing?"

## Relevant commands
```bash
cd inhere
ls
ls -la
cat .hidden
```

## Hints (in increasing order)
1. Default `ls` does not show everything.
2. Filenames beginning with a dot are hidden.
3. `-a` reveals them.

## Solution explanation
`ls -la inhere` (or `cd inhere` then `ls -la`) reveals `.hidden`. `cat inhere/.hidden` prints the next password. Use it to log in to the next level.

## Why it works
`ls` filters out names starting with `.` unless asked with `-a`. The file was always there and fully readable; only the listing was incomplete.

## Check yourself
**Q1.** Does hiding a file with a leading dot protect it from other users?

<details>
<summary>Show answer</summary>

No. It only filters default listings. Anyone with read permission sees it with `ls -a` and can read it normally. Protection is permissions, not naming.
</details>

**Q2.** Name two legitimate, everyday uses of dotfiles in a home directory.

<details>
<summary>Show answer</summary>

Configuration like `~/.bashrc` and credential material like `~/.ssh/` (protected by permissions). The convention keeps default listings clean, not secure.
</details>

## Official verification
[Bandit Level 3 → Level 4](https://overthewire.org/wargames/bandit/bandit4.html)
