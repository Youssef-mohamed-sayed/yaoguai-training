# Bandit Level 4 to Level 5: Identify Human-Readable Data


## Level objective
Identify the relevant file among a group of files by examining file types.

## Concepts practiced
`file`, text versus binary data, and safe inspection.

## Relevant commands
```bash
ls -la
file ./*
```

## Hints (in increasing order)
1. Filenames may not describe their content.
2. Ask the operating system's file-identification utility.
3. Inspect candidates identified as text, then use the official level condition to select the right one.

## Solution explanation
Run `file` on the candidate files and inspect the one matching the official requirement. Read only the relevant candidate.

## Why it works
`file` examines content signatures and heuristics instead of trusting filename extensions.

## Lessons learned
Identify unknown files before displaying or processing them.

## Official verification
[Bandit Level 4 → Level 5](https://overthewire.org/wargames/bandit/bandit5.html)
