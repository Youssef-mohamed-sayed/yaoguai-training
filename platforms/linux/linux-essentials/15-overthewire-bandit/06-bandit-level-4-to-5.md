# Bandit Level 4 to Level 5: The Only Human-Readable File


## Level objective
In the `inhere` directory, several files have similar names, but only one contains human-readable text. Find it and read the password. Confirm the exact goal on the official level page.

## Concepts practiced
Content-based file identification with `file`, glob patterns, and resisting the urge to `cat` everything.

## Background
The directory holds ten files named like `-file00` through `-file09`. Nine contain binary noise; one contains the password. Two lessons from earlier levels combine here: the names start with a dash (so use `./` paths or `--`), and extensions are absent, so names tell you nothing about content.

You could `cat` each file and let the binary garbage garble your terminal (run `reset` if that happens), but the intended tool is `file`, which inspects content signatures safely. Run it against all of them at once with a glob, and the odd one out identifies itself.

## Relevant commands
```bash
cd inhere
ls -la
file ./*
cat ./-file07
```

(The answer file number is stable in the long-running game, but verify by running `file` yourself rather than trusting any writeup, including this one.)

## Hints (in increasing order)
1. Ask the filesystem what each file *contains*, not what it is named.
2. `file` accepts many arguments or a glob.
3. Only one entry will say "ASCII text".

## Solution explanation
`file ./*` prints a type for every entry: nine report `data`, one reports `ASCII text`. Read that one with `cat ./-fileXX` (substituting the name `file` revealed) to get the next password.

## Why it works
`file` reads the leading bytes and matches them against a signature database: text encodings, executables, archives, images. It answers "what is this" from content, which is the only honest answer when names are meaningless or misleading.

## Check yourself
**Q1.** Why `file ./*` instead of `file *` in this directory?

<details>
<summary>Show answer</summary>

The filenames start with `-`. The glob `*` expands to names like `-file00`, which `file` would parse as options; `./` makes each one an explicit path.
</details>

**Q2.** What does `file` report as bare `data`, and why is that still useful information?

<details>
<summary>Show answer</summary>

Content matching no known signature, typically binary noise or an unrecognized format. Useful because it tells you *not* to read it as text, and here it eliminates nine of ten candidates.
</details>

## Official verification
[Bandit Level 4 → Level 5](https://overthewire.org/wargames/bandit/bandit5.html)
