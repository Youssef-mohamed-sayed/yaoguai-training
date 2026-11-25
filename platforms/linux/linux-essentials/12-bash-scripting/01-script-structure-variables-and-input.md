# Scripts, Variables, Arguments, and Input


## Learning objectives
- Create and execute a Bash script with a proper shebang.
- Use variables, command substitution, arguments, and `read` correctly.
- Know the special parameters and quote everything that needs quoting.

## Your first script
Create `hello.sh`:

```bash
#!/usr/bin/env bash
set -u

name="${1:-learner}"
printf 'Hello, %s!\n' "$name"
```

Three lines of ceremony, each earning its place:

- `#!/usr/bin/env bash` is the **shebang**: it tells the kernel which interpreter runs this file. `env` finds `bash` through `PATH`, which is more portable than a hardcoded path.
- `set -u` makes referencing an unset variable an error instead of a silent empty string. Typos fail loudly instead of corrupting paths.
- `${1:-learner}` is a default: the first argument if set and non-empty, otherwise `learner`.

Run it two ways:

```bash
chmod +x hello.sh
./hello.sh Yaoguai
bash hello.sh
```

Output:

```text
Hello, Yaoguai!
Hello, learner!
```

`chmod +x` plus the shebang makes it a real program; `bash hello.sh` skips both by handing the file to Bash directly.

## Variables and quoting
```bash
project='Linux Essentials'
printf '%s\n' "$project"
kernel="$(uname -r)"
printf 'Kernel: %s\n' "$kernel"
```

Rules that break scripts when ignored:

- **No spaces around `=`.** `name = value` is not an assignment; Bash parses it as running a command called `name` with arguments.
- **Quote expansions**: `"$project"`. Unquoted, the value is word-split and glob-expanded (module 04 lesson 1), so a variable holding `my dir` silently becomes two arguments.
- `$(command)` captures a command's stdout into the variable.

## Special parameters
| Parameter | Meaning |
|---|---|
| `$0` | Script name as invoked |
| `$1`, `$2`, ... | Positional arguments |
| `$#` | How many arguments were given |
| `"$@"` | All arguments, each preserved as its own word |
| `$?` | Exit status of the last command |
| `$$` | The script's own process ID |

Forward arguments to another program with `"$@"`, never `$*` (which mushes them into one string) and never unquoted `$@` (which splits them on spaces). `"$@"` is the only form that treats `deploy.sh "my server" prod` as two arguments, which it is.

## Input and exit codes
```bash
read -r -p 'Enter a hostname: ' host
printf 'You entered: %s\n' "$host"
exit 0
```

- `read -r` stops backslashes being mangled; make `-r` a reflex.
- Exit status is your script's report to whoever ran it: `0` means success, anything else means failure. `exit 3` tells a calling script (or a human checking `$?`) not just *that* you failed but *how*.

## Practice exercises
Try every task before opening its solution.

**Exercise 1.** Write `greet.sh`: takes exactly one argument (a name), prints `Hello, NAME!`, and exits with status 2 and a usage message if the argument count is wrong.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

if [[ $# -ne 1 ]]; then
    printf 'usage: %s NAME\n' "$0" >&2
    exit 2
fi
printf 'Hello, %s!\n' "$1"
```

Test all three paths:

```bash
chmod +x greet.sh
./greet.sh Ada          # Hello, Ada!
./greet.sh              # usage: ./greet.sh NAME ; echo $? -> 2
./greet.sh Ada Lovelace # usage message too: two arguments is also wrong
```

Usage messages go to stderr (`>&2`) so they never pollute piped output.
</details>

**Exercise 2.** Extend the script so `greet.sh "Ada Lovelace"` prints one correct greeting, and explain which characters in your script made that work.

<details>
<summary>Show a worked solution</summary>

Two layers of quoting cooperate: the caller's `"Ada Lovelace"` makes it one argument, and the script's `"$1"` keeps it one word after expansion. Remove either and the name splits.
</details>

**Exercise 3.** Write `sysnote.sh` that stores today's date and the kernel release in variables using command substitution, then prints a one-line summary.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

today="$(date +%F)"
kernel="$(uname -r)"
printf '%s: kernel %s is running\n' "$today" "$kernel"
```

Output:

```text
2026-11-25: kernel 6.8.0-45-generic is running
```
</details>

**Exercise 4.** Write `confirm.sh` that asks "Proceed? [y/N]", prints "continuing" only on `y` or `Y`, and exits 1 otherwise.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

read -r -p 'Proceed? [y/N] ' answer
if [[ "$answer" == [yY] ]]; then
    printf 'continuing\n'
else
    printf 'aborted\n' >&2
    exit 1
fi
```

(The `[[ ]]` test is the subject of the next lesson; the pattern `[yY]` matches either letter.)
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why does `name = Ada` fail, and what does Bash think you meant?

<details>
<summary>Show answer</summary>

With spaces it is not an assignment: Bash parses `name` as a command with arguments `=` and `Ada`, and reports "name: command not found". Assignments are exactly `name=value`.
</details>

**Q2.** What does `set -u` catch that Bash would otherwise ignore?

<details>
<summary>Show answer</summary>

References to unset variables, which otherwise expand to empty strings. `rm -r "$dir/"` with a typo'd `$dri` is the classic disaster `set -u` turns into a clean error.
</details>

**Q3.** Why is `"$@"` the only safe way to forward all arguments?

<details>
<summary>Show answer</summary>

Quoted, it expands to each argument as a separate word, spaces inside arguments intact. Unquoted `$@` splits on spaces; `"$*"` glues everything into one word. Both corrupt multi-word arguments.
</details>

## Common mistakes
- Forgetting the shebang, then watching `sh` run Bash syntax and fail strangely.
- Spaces around `=`.
- Unquoted variables in paths.
- Using `echo` for output where escapes and leading dashes matter; `printf` is predictable.
- Exiting without a status, leaving callers unable to tell success from failure.

## Key takeaways
Scripts are programs: declare the interpreter, fail loudly on unset variables, quote expansions, validate input, and return honest exit codes.

## Further practice
Read the Bash manual sections on parameters, quoting, and command substitution, then rewrite one thing you did three times this week as a script with an argument.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
