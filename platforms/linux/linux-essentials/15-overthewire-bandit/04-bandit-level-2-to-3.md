# Bandit Level 2 to Level 3: Spaces in a Filename


## Level objective
Read the file in the home directory whose name contains spaces. Confirm the exact goal on the official level page.

## Concepts practiced
Word splitting, quoting, and escape characters, the core of module 04 lesson 1 applied to a real annoyance.

## Background
The file is named `spaces in this filename`. Type it bare and the shell performs **word splitting**: the one name becomes four arguments, and `cat` tries to open four files named `spaces`, `in`, `this`, and `filename`, failing on the first with "No such file or directory".

The shell gives you three equivalent ways to keep the name one argument:

- **Single quotes:** `'spaces in this filename'` — everything literal.
- **Double quotes:** `"spaces in this filename"` — literal except `$`, backticks, and `\`.
- **Escaping each space:** `spaces\ in\ this\ filename` — the backslash escapes the character after it.

In practice, nobody types the escapes: type `cat sp` and press **Tab**, and the shell completes the name with the escaping done for you. Completion is the everyday answer; quoting is the scripting answer.

## Relevant commands
```bash
ls -la
cat "spaces in this filename"
cat spaces\ in\ this\ filename
```

## Hints (in increasing order)
1. The spaces are splitting the name into separate arguments.
2. Quoting or escaping keeps the name whole.
3. Tab completion writes the escapes for you.

## Solution explanation
`ls -la` shows the spaced filename. Read it with any of the quoted or escaped forms above to get the next password, then log in to the next level.

## Why it works
Word splitting happens after the shell reads your line and before the command runs, at every unquoted space. Quoting and escaping both mark the spaces as *data*, so the command receives exactly one argument: the real filename.

## Check yourself
**Q1.** In a script, a variable holds a filename that might contain spaces. Which form is safe: `cat $file`, `cat "$file"`, or `cat '$file'`?

<details>
<summary>Show answer</summary>

`cat "$file"`. Unquoted splits the value on spaces; single quotes would print the literal text `$file` instead of the variable's value.
</details>

**Q2.** Why did `cat spaces in this filename` report the error on `spaces` rather than on the whole name?

<details>
<summary>Show answer</summary>

Because after word splitting, `cat` received four arguments and tried them in order; the first nonexistent "file" was `spaces`.
</details>

## Official verification
[Bandit Level 2 → Level 3](https://overthewire.org/wargames/bandit/bandit3.html)
