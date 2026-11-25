# Bandit Level 9 to Level 10: Text Hidden in Binary


## Level objective
`data.txt` is mostly binary data. The password is in one of the few human-readable strings, preceded by several `=` characters. Find it. Confirm the exact goal on the official level page.

## Concepts practiced
Extracting readable strings from binary files, and piping extraction into filtering.

## Background
`cat` on this file would spray control characters at your terminal, and `grep` treats binary files awkwardly by default ("Binary file matches" at best). The right tool is `strings`: it scans any file and emits only the runs of printable characters, which is exactly the human-readable subset hiding in the noise.

That output is still long, so filter it with the second clue: the target string is preceded by several `=` signs. `strings data.txt | grep '=='` or `grep '=\{2,\}'` narrows it to a handful of lines. This two-stage shape, extract candidates then filter, is the same pattern as every pipeline in module 08.

## Relevant commands
```bash
file data.txt
strings data.txt | head
strings data.txt | grep '=='
```

## Hints (in increasing order)
1. Do not read the binary; extract its readable parts.
2. `strings` does the extraction.
3. The `=` characters are your filter pattern.

## Solution explanation
`strings data.txt | grep '=='` prints the few printable strings containing runs of `=`; the password is the token after them on the matching line. Use it to log in to the next level.

## Why it works
Binary formats interleave structure and data, but passwords and messages survive as printable runs. `strings` finds those runs; the `=` marker, chosen by the level designer, is a signature that separates the needle from the other printable hay.

## Check yourself
**Q1.** Why is `strings` safer than `cat` on an unknown binary?

<details>
<summary>Show answer</summary>

`strings` outputs only printable character runs, so no terminal control sequences reach your display; `cat` passes raw bytes, including control characters that garble or manipulate the terminal.
</details>

**Q2.** Outside a wargame, name one legitimate use of `strings`.

<details>
<summary>Show answer</summary>

Triage of an unknown binary: extracting embedded messages, paths, version banners, or URLs before deciding how to analyze it further. (Also: recovering readable fragments from a corrupted file.)
</details>

## Official verification
[Bandit Level 9 → Level 10](https://overthewire.org/wargames/bandit/bandit10.html)
