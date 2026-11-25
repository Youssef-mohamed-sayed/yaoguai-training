# Bandit Level 1 to Level 2: A Filename Beginning with a Dash


## Level objective
Read the file in the home directory whose name is a single dash: `-`. Confirm the exact goal on the official level page.

## Concepts practiced
Option parsing, relative paths, the `--` end-of-options marker, and explicit pathnames.

## Background
Try the obvious first and watch it fail: `cat -` does not read a file named `-`. Nearly every Unix command-line program treats an argument starting with `-` as an **option**, and a bare `-` by convention often means standard input. So `cat -` waits for you to type, which looks exactly like the command "hanging". (If that happens to you, `Ctrl-C` out.)

Two standard escapes exist, and both are worth knowing because this exact problem recurs with files like `-rf`, `--help`, and worse:

- **Make it a path.** A name containing `/` is never parsed as an option: `./-` is unambiguously the file `-` in the current directory.
- **End the options.** GNU utilities accept `--` to mean "everything after this is an operand, not an option": `cat -- -`.

## Relevant commands
```bash
ls -la
cat ./-
cat -- -
```

## Hints (in increasing order)
1. The filename is being mistaken for a command option.
2. Prefix the name with a path component.
3. Many GNU utilities accept `--` to end option processing.

## Solution explanation
`ls -la` shows the file `-` in the home directory. `cat ./-` reads it as an explicit relative path and prints the next password. On GNU systems, `cat -- -` works too. Use the credential only to log in to the next level.

## Why it works
Option parsers split arguments into options and operands before the program sees them. Both fixes work at that parsing layer: a path with a slash cannot look like an option, and `--` tells the parser to stop looking. Neither changes the file or the command; both change how your argument is *interpreted*.

## Check yourself
**Q1.** A file is named `-rf`. Why is `rm -rf` a terrifying typo, and how do you delete that file safely?

<details>
<summary>Show answer</summary>

Unqualified, the name parses as the recursive-force options. Delete it with an explicit path: `rm -- -rf` or `rm ./-rf` (and read it twice first, as always with `rm`).
</details>

**Q2.** Are `./-` and `--` interchangeable everywhere?

<details>
<summary>Show answer</summary>

Nearly, but not universally: `--` is a GNU convention that some minimal or non-GNU tools do not honor, while the `./name` path form works with anything that accepts a path. When in doubt, use the path form.
</details>

## Official verification
[Bandit Level 1 → Level 2](https://overthewire.org/wargames/bandit/bandit2.html)
