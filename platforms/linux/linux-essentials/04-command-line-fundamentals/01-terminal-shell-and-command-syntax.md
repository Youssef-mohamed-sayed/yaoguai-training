# Terminal, Shell, and Command Syntax


## Learning objectives
- Explain what the terminal, the shell, and a command really are, and how a command is parsed and executed.
- Use built-in help, manual pages, and `type` to understand any command you meet.
- Control quoting, escaping, globbing, and environment variables so commands do exactly what you intend.

## Terminal, shell, and command: three different things
People say "the terminal" for everything, but three separate pieces are involved every time you run a command:

- The **terminal** (or terminal emulator) is the window on your screen. It draws text and sends your keystrokes to the shell. GNOME Terminal, Konsole, Windows Terminal, and the Linux virtual consoles are all terminals.
- The **shell** is the program running inside that window. It reads the line you typed, interprets it, starts programs, and prints their output. On most Linux systems the shell is **Bash**; others include Zsh and Dash.
- A **command** is one instruction you give the shell: a program name plus optional modifiers.

You can check which shell you are running:

```bash
echo "$SHELL"
printf '%s\n' "$0"
```

Typical output:

```text
/bin/bash
bash
```

This distinction matters because some behavior belongs to the shell (history, tab completion, wildcards), some to the terminal (copy/paste shortcuts, scrollback), and some to the command itself (its options and output). When something behaves unexpectedly, knowing which layer owns the behavior tells you where to look.

## Anatomy of a command
A command line commonly has the form `command [options] [arguments]`:

```bash
ls -lah /var/log
```

- `ls` is the **command**: the program to run.
- `-lah` is a bundle of three **options** (`-l`, `-a`, `-h`). Options change behavior. Short options start with one dash and can usually be bundled; long options start with two dashes and stand alone (`--all`). Some options take a value of their own, as in `grep -n 3 file` or `cut -d ,`.
- `/var/log` is an **argument**: the target the command acts on. Many commands accept several arguments, or none.

Commands come in two kinds. **External programs** are files on disk, usually in directories like `/bin` and `/usr/bin`. **Shell built-ins** are features of the shell itself: `cd`, `echo`, `pwd`, `history`, and `export` are built-ins in Bash. The difference shows up when you look for help (see below) and when you script.

## What the shell does before your command runs
The most important idea in this lesson: **the shell rewrites your line before the command ever sees it.** This rewriting is called *expansion*, and it happens in a fixed order. The command receives only the final, expanded words.

Watch it happen with `echo`, which simply prints the arguments it receives:

```bash
echo home is $HOME
echo files: *.conf
echo today is $(date +%F)
echo "literal: $HOME *.conf $(date)"
```

Sample output (yours will differ):

```text
home is /home/learner
files: app.conf db.conf
today is 2026-11-25
literal: $HOME *.conf $(date)
```

In order, the first three lines performed **variable expansion** (`$HOME`), **pathname expansion** (`*.conf` became the matching filenames in the current directory), and **command substitution** (`$(date +%F)` ran `date` and inserted its output). The fourth line was quoted, so nothing expanded.

Other expansions you will meet early:

- `~` expands to your home directory; `~alice` expands to user alice's home.
- `{a,b,c}` is **brace expansion**: `mkdir lab_{one,two}` creates `lab_one` and `lab_two`.
- `$((2 + 3))` is arithmetic expansion.

### Quoting and escaping
Quoting controls expansion:

- `'single quotes'` preserve everything literally. Nothing expands, ever.
- `"double quotes"` allow `$variable`, `$(command)`, and backslash escapes, but prevent word splitting and pathname expansion.
- A backslash `\` escapes the single character that follows it.

Word splitting is the reason quoting is not optional. After expansion, the shell splits the line into separate words at unquoted spaces. Compare:

```bash
mkdir "my lab"
mkdir my lab
```

The first creates one directory named `my lab`. The second creates two directories, `my` and `lab`, because the unquoted space split the argument in two. The same rule applies to variables:

```bash
name='linux lab'
printf '%s\n' "$name"   # one argument: linux lab
printf '%s\n' $name     # two arguments: linux and lab
```

> [!WARNING]
> Unquoted variables are one of the most common causes of destructive scripts. `rm -r $dir/*` with an empty or space-filled `dir` can delete things you never intended. Quote every variable unless you specifically want splitting.

### Globbing patterns
When a word contains an unquoted wildcard, the shell replaces it with matching filenames:

- `*` matches any string, including empty: `ls *.log`.
- `?` matches exactly one character: `ls data?.csv`.
- `[abc]` matches one listed character; `[0-9]` matches a range: `ls report[0-9].txt`.
- `[!abc]` matches one character *not* listed.

If nothing matches, Bash passes the pattern through literally, which confuses many commands. And if the pattern would match something dangerous, think before combining it with `rm`.

### Environment variables
Variables live in your shell session. Some are marked for **export**, which means child processes inherit a copy; those are environment variables. Key ones:

- `HOME`: your home directory.
- `PATH`: the colon-separated list of directories the shell searches for commands.
- `USER`, `SHELL`, `PWD`, `LANG`.

```bash
printf '%s\n' "$PATH"
project='linux lab'        # shell variable, current shell only
export project             # now child processes see it too
env | grep '^project='
```

Assignments without `export` disappear when the shell exits and are invisible to programs you start. Permanent variables are set in startup files such as `~/.bashrc`.

## Getting help inside the terminal
You rarely need the web to learn a command. Linux ships its documentation with the system:

```bash
man ls            # full manual page; press q to quit, / to search
ls --help         # short option summary from the command itself
help cd           # documentation for a Bash built-in
type cd           # how the shell resolves this name
type ls
which python3     # which file PATH resolves to this name
apropos copy      # search man page summaries for a keyword
```

- `man` pages are organized into numbered sections. Section 1 is user commands, section 5 is file formats, section 8 is administration commands. Occasionally you need the section number: `man 5 passwd` documents the `/etc/passwd` file format, while `man 1 passwd` documents the password-changing command.
- `help` only covers built-ins. `man bash` covers the shell itself, including every expansion rule in this lesson.
- `type` is the reliable way to ask "what will actually run?": it reports built-ins, aliases, functions, and external paths. `which` only searches `PATH` and can mislead you about aliases and built-ins.
- `history` lists recent commands from the current shell. Bash keeps a bounded in-memory history and commonly saves it to `~/.bash_history` on exit.

> [!IMPORTANT]
> Never type passwords or tokens directly into a command line. They land in your shell history and are visible in process listings while the command runs.

## Efficiency essentials
The shell rewards a handful of keystrokes:

- **Tab** completes commands, paths, and filenames. Press it twice to list possibilities.
- **Up / Down** walk through history; **Ctrl-R** searches it interactively.
- **Ctrl-A** / **Ctrl-E** jump to the start / end of the line.
- **Ctrl-U** deletes from the cursor to the start; **Ctrl-K** deletes to the end.
- **Ctrl-C** interrupts the foreground command; **Ctrl-D** sends end-of-input (an empty line at a shell prompt usually logs you out).
- **Ctrl-L** clears the screen, like the `clear` command. Neither touches history or files.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Create a directory named exactly `course notes` (with the space) in your home directory, then list it with `ls -ld`.

<details>
<summary>Show a worked solution</summary>

```bash
mkdir "$HOME/course notes"
ls -ld "$HOME/course notes"
```

Output:

```text
drwxrwxr-x 2 learner learner 4096 Nov 25 04:10 /home/learner/course notes
```

The quotes keep the space inside one argument. Without them you would create two directories.
</details>

**Exercise 2.** Set a variable `project='linux lab'` and print it on its own line. Then print the literal text `$project` (the dollar sign included).

<details>
<summary>Show a worked solution</summary>

```bash
project='linux lab'
printf '%s\n' "$project"
printf '%s\n' '$project'
```

Output:

```text
linux lab
$project
```

Double quotes expand the variable; single quotes preserve it literally.
</details>

**Exercise 3.** Run `type` on `cd`, `ls`, `grep`, and `history`. Which are built-ins and which are external programs? For each external one, where does the file live?

<details>
<summary>Show a worked solution</summary>

```bash
type cd ls grep history
```

Typical output:

```text
cd is a shell builtin
ls is aliased to `ls --color=auto'
grep is /usr/bin/grep
history is a shell builtin
```

`cd` and `history` are built-ins. `ls` is often an alias wrapping `/usr/bin/ls`; `grep` is a plain external program.
</details>

**Exercise 4.** Open `man grep`, find the documentation for the `-i` option using `/` search, then quit. What does `-i` do?

<details>
<summary>Show a worked solution</summary>

Run `man grep`, type `/-i` and press Enter, press `n` to jump between matches, and `q` to quit. `-i` makes matching case-insensitive (`--ignore-case`).
</details>

**Exercise 5.** Using only globbing (no `find`), list every file in `/etc` whose name ends in `.conf`, then every file in `/var/log` whose name contains a digit.

<details>
<summary>Show a worked solution</summary>

```bash
ls /etc/*.conf
ls /var/log/*[0-9]*
```

The second pattern uses a bracket range, which matches any single digit anywhere in the name.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You run `echo $UNSAVED` and get an empty line, but you typed `UNSAVED=hello` a minute ago in the same shell. What is the most likely explanation?

<details>
<summary>Show answer</summary>

The variable was never assigned in *this* shell, or the shell was restarted. Assignments do not survive a closed terminal. (If it were assigned but not exported, `echo` would still print it, because `echo` runs in the current shell.)
</details>

**Q2.** `rm report final.txt` deleted a file called `report` but not your file `report final.txt`. Why, and how do you remove the right file?

<details>
<summary>Show answer</summary>

The unquoted space split the name into two arguments. Remove it with quoting: `rm "report final.txt"` or `rm report\ final.txt`.
</details>

**Q3.** Which single command tells you whether `python3` is a built-in, an alias, or an external program, and where it lives?

<details>
<summary>Show answer</summary>

`type python3` (`type -a python3` shows every match in resolution order).
</details>

## Common mistakes
- Forgetting quotes around variables or filenames that contain spaces.
- Assuming `which` describes aliases and shell functions; use `type` instead.
- Pasting commands from the web without understanding the metacharacters in them.
- Typing passwords directly into command arguments, where history and process lists keep them.
- Expecting `unset`-style changes or plain assignments to reach other programs without `export`.

## Key takeaways
The shell expands variables, globs, and substitutions **before** running anything, and the command only sees the expanded result. Quoting is how you stay in control of that rewriting, and `type` plus `man` are how you stay in control of unfamiliar commands.

## Further practice
Read the `man bash` sections on quoting, expansions, and history. Then spend one day doing every file task you would normally do in a file manager from the shell instead.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
- [man-pages project](https://man7.org/linux/man-pages/)
