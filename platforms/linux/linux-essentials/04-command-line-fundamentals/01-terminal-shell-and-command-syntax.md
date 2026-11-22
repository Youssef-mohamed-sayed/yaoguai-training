# Terminal, Shell, and Command Syntax


## Learning objectives
- Explain how a command is parsed and executed.
- Use built-in help and manual pages.
- Understand quoting, escaping, globbing, and environment variables.

## Core concepts
A command commonly has the form `command [options] [arguments]`. Options change behavior; arguments identify targets or values. Commands may be external programs or shell built-ins.

The shell expands variables, quotes, wildcards, and command substitutions before starting an external program. This is why quoting matters.

### Quoting and special characters
- `'single quotes'` preserve literal characters (no variable expansion).
- `"double quotes"` allow variable and command substitution but prevent word splitting and pathname expansion in the quoted text.
- `\` escapes the next character in many contexts.
- `*` matches any string; `?` matches one character; `[abc]` matches one listed character.
- `~` commonly expands to the home directory.
- `$NAME` expands an environment variable.
- `$(command)` runs a command and substitutes its output.

Examples:
```bash
name='Linux learner'
printf '%s
' "$name"
printf '%s
' '$name'
printf 'Home: %s
' "$HOME"
kernel="$(uname -r)"
printf 'Kernel: %s
' "$kernel"
```

### Help
```bash
man ls
ls --help
help cd
type cd
type ls
which python3
history
clear
```
`history` displays the current shell's command history (Bash commonly keeps a bounded history in memory and may save it to `~/.bash_history`). `clear` clears the visible terminal display; it does not delete command history or files.
`man` opens a manual page; press `q` to quit. `help` documents Bash built-ins. `type` identifies how the current shell resolves a name. `which` searches `PATH` for an executable and may not identify aliases or built-ins reliably.

## Efficiency
- Tab completes commands and paths.
- Up/Down navigate history; `Ctrl-R` searches history in Bash.
- `Ctrl-A` and `Ctrl-E` move to line start/end.
- `Ctrl-U` clears from cursor to line start; `Ctrl-K` clears to line end.
- `Ctrl-C` interrupts the foreground command; `Ctrl-D` sends end-of-input (often exits an interactive shell).
- `history` lists recent commands. Avoid placing secrets in commands because history may retain them.

## Hands-on practice
1. Create a directory whose name contains spaces and list it using correct quoting.
2. Set `project='linux lab'` and print it safely.
3. Use `type` on `cd`, `ls`, and `grep`; compare results.
4. Open `man grep`, search for `-i`, and quit.
5. Hint: quote a complete path containing spaces.

## Common mistakes
- Forgetting quotes around variables that may contain spaces.
- Assuming `which` describes aliases and shell functions.
- Pasting commands without understanding shell metacharacters.
- Typing passwords directly into command arguments.

## Key takeaways
The shell performs expansions before execution. Quoting is essential for predictable and safe commands.

## Further practice
Read `man bash` sections on quoting, expansions, and history.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
