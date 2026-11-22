# Bandit Level 2 to Level 3: Spaces in Filenames


## Level objective
Read the file identified by the official level page when its name contains spaces.

## Concepts practiced
Quoting, escaping, and filename completion.

## Relevant commands
```bash
ls -lb
cat 'spaces in this filename'
cat spaces\ in\ this\ filename
```

## Hints (in increasing order)
1. The shell normally splits unquoted words at spaces.
2. Put the complete filename in single quotes.
3. Alternatively, escape each space with a backslash.

## Solution explanation
Quote the full filename as one shell argument. Single quotes preserve the spaces literally.

## Why it works
The shell performs word splitting before launching `cat`. Quoting prevents the filename from becoming several separate arguments.

## Lessons learned
Quote paths by default, especially when they come from users or external data.

## Official verification
[Bandit Level 2 → Level 3](https://overthewire.org/wargames/bandit/bandit3.html)
