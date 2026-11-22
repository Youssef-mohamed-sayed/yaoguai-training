# Scripts, Variables, Arguments, and Input


## Learning objectives
- Create and execute a Bash script.
- Use variables, command substitution, arguments, and `read`.
- Understand common special parameters.

## First script
Create `hello.sh`:
```bash
#!/usr/bin/env bash
set -u

name="${1:-learner}"
printf 'Hello, %s!
' "$name"
```
The shebang selects Bash through `env`. `set -u` treats unset variables as errors. `${1:-learner}` uses the first argument if set and non-empty, otherwise a default. Make it executable with `chmod +x hello.sh`, then run `./hello.sh Yaoguai`. You can also run `bash hello.sh Yaoguai`.

### Variables and quoting
```bash
project='Linux Essentials'
printf '%s
' "$project"
kernel="$(uname -r)"
printf 'Kernel: %s
' "$kernel"
```
No spaces are allowed around `=` in a simple assignment. Quote expansions to prevent word splitting and glob expansion.

### Parameters
| Parameter | Meaning |
|---|---|
| `$0` | Script name |
| `$1`, `$2` | Positional arguments |
| `$@` | All arguments as separate words when quoted as `"$@"` |
| `$#` | Number of positional arguments |
| `$?` | Previous command's exit status |
| `$$` | Current shell process ID |

Use `"$@"` when forwarding arguments. Avoid `$*` for most argument-forwarding tasks because it joins arguments.

### Input and exit codes
```bash
read -r -p 'Enter a hostname: ' host
printf 'You entered: %s
' "$host"
exit 0
```
`read -r` prevents backslash interpretation. Exit status 0 conventionally means success; nonzero means failure. `exit` terminates the script.

## Hands-on practice
- Write a script that accepts a first name and prints a greeting.
- Add a check that exactly one argument was supplied.
- Try an argument containing spaces.
- Hint: use `[[ $# -eq 1 ]]` and quote `"$1"`.

## Common mistakes
- Forgetting the shebang.
- Writing `name = value` with spaces.
- Using unquoted variables in paths.
- Using `echo` for output that requires predictable escape handling; prefer `printf`.

## Key takeaways
Bash scripts are programs. Quote variable expansions, validate input, and return meaningful exit statuses.

## Further practice
Read the Bash manual sections on shell parameters, quoting, and command substitution.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
