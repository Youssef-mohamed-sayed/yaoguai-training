# Conditionals, Loops, Functions, and Arrays


## Learning objectives
- Test strings, numbers, and files with `[[ ... ]]`.
- Control flow with `if`, `case`, `for`, `while`, and `until`.
- Define functions with local variables and use beginner-level arrays safely.

## Tests: asking questions
```bash
[[ -f "$path" ]]          # regular file exists
[[ -d "$path" ]]          # directory exists
[[ -r "$path" ]]          # readable by this process
[[ -x "$path" ]]          # executable (or searchable directory)
[[ -e "$path" ]]          # exists at all
[[ "$name" == "admin" ]]  # string equality
[[ "$name" == ad* ]]      # pattern match
[[ -n "$value" ]]         # non-empty string
[[ -z "$value" ]]         # empty string
[[ "$count" -ge 3 ]]      # numeric: -eq -ne -lt -le -gt -ge
```

Use Bash's `[[ ... ]]`, not the older `[ ... ]`: inside `[[ ]]` word splitting and glob expansion are disabled, so quoted-empty variables and spaces behave. (The classic `[ $x = y ]` fails outright when `$x` is empty; `[[ $x == y ]]` does not.) Note the two families: `==` compares strings, `-eq` compares numbers; mixing them compares the wrong things.

## Conditionals and case
```bash
if [[ -f "$1" ]]; then
    printf 'File exists\n'
elif [[ -d "$1" ]]; then
    printf 'Directory exists\n'
else
    printf 'Path not found\n' >&2
    exit 1
fi
```

`case` is the cleaner tool when one value drives many branches, and every service-style script uses this shape:

```bash
case "${1:-}" in
    start)  printf 'Starting\n' ;;
    stop)   printf 'Stopping\n' ;;
    status) printf 'Checking\n' ;;
    *)      printf 'Usage: %s {start|stop|status}\n' "$0" >&2; exit 2 ;;
esac
```

`"${1:-}"` supplies an empty default so an absent argument lands in the usage branch instead of erroring under `set -u`; `*` is the catch-all.

## Loops
```bash
for item in alpha beta gamma; do
    printf '%s\n' "$item"
done

for file in *.log; do
    printf 'Found: %s\n' "$file"
done

while IFS= read -r line; do
    printf 'Line: %s\n' "$line"
done < input.txt

until [[ -e ready.flag ]]; do
    sleep 1
done
```

- `for` iterates a fixed list or a glob. Globbing (`*.log`) is the safe way to loop over files.
- `while IFS= read -r line` is **the** correct file-reading idiom: `IFS=` preserves leading/trailing whitespace, `-r` preserves backslashes. Never use `for x in $(cat file)`: it splits on every whitespace character and expands globs, mangling real data.
- `while` repeats while its condition succeeds; `until` repeats until it does. Any wait loop needs a `sleep` or it burns a CPU core busy-spinning.

## Functions and arrays
```bash
greet() {
    local name="${1:-learner}"
    printf 'Hello, %s\n' "$name"
}
greet "Linux student"

tools=(grep awk sed)
printf '%s\n' "${tools[@]}"     # each element, safely
printf 'count: %d\n' "${#tools[@]}"
```

Functions take positional parameters just like scripts (`$1`, `$2`), and `local` keeps their variables from leaking into the rest of the script. Without `local`, a function that assigns `name=...` silently overwrites a global of the same name, one of the sneakiest Bash bugs.

Arrays hold lists without packing them into strings. `"${array[@]}"` (quoted, with `@`) expands to each element as its own word; every other form mangles elements containing spaces.

## Arithmetic
```bash
count=$((count + 1))
if (( count > 10 )); then printf 'many\n'; fi
```

`$(( ... ))` evaluates arithmetic and yields the value; `(( ... ))` evaluates a condition. Strings never belong inside either.

## Practice exercises
Try every task before opening its solution.

**Exercise 1.** Write `filetype.sh PATH` that prints "regular file", "directory", "other", or "missing" for one argument, with a usage error when no argument is given.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage: %s PATH\n' "$0" >&2
    exit 2
fi
path=$1
if [[ -f "$path" ]]; then
    printf 'regular file\n'
elif [[ -d "$path" ]]; then
    printf 'directory\n'
elif [[ -e "$path" ]]; then
    printf 'other\n'
else
    printf 'missing\n' >&2
    exit 1
fi
```

Test it against a file, a directory, `/dev/null` (other), and a made-up path.
</details>

**Exercise 2.** Write `lines.sh FILE` that prints each line of a file numbered, correctly handling spaces and empty lines.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

[[ -r "${1:-}" ]] || { printf 'Usage: %s READABLE_FILE\n' "$0" >&2; exit 2; }
n=0
while IFS= read -r line; do
    n=$((n + 1))
    printf '%4d: %s\n' "$n" "$line"
done < "$1"
```
</details>

**Exercise 3.** Write `renamer.sh` that renames every `.jpeg` file in the current directory to `.jpg`, printing each rename, and reports when none matched.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

shopt -s nullglob
found=0
for file in *.jpeg; do
    found=1
    mv -- "$file" "${file%.jpeg}.jpg"
    printf 'renamed %s -> %s\n' "$file" "${file%.jpeg}.jpg"
done
(( found )) || printf 'no .jpeg files here\n'
```

`nullglob` makes the glob expand to nothing (instead of the literal text `*.jpeg`) when there are no matches; `${file%.jpeg}` strips the suffix.
</details>

**Exercise 4.** Write a `case`-driven `notes.sh` supporting `add TEXT` (appends to `~/notes.txt`) and `list` (prints it), with a usage branch for anything else.

<details>
<summary>Show a worked solution</summary>

```bash
#!/usr/bin/env bash
set -u

file=~/notes.txt
case "${1:-}" in
    add)
        shift
        [[ $# -ge 1 ]] || { printf 'add needs text\n' >&2; exit 2; }
        printf '%s\n' "$*" >> "$file"
        ;;
    list)
        [[ -f "$file" ]] && cat -- "$file" || printf 'no notes yet\n'
        ;;
    *)
        printf 'Usage: %s {add TEXT|list}\n' "$0" >&2
        exit 2
        ;;
esac
```
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why does `for f in $(ls)` break, and what replaces it?

<details>
<summary>Show answer</summary>

`$(ls)` output is split on every whitespace character and glob-expanded, so `my file.txt` becomes two broken words. Loop the glob directly: `for f in *` (optionally with `nullglob`).
</details>

**Q2.** What is the difference between `[[ $a == 3 ]]` and `[[ $a -eq 3 ]]` when `$a` is `03`?

<details>
<summary>Show answer</summary>

`==` compares strings: `03` does not equal `3`. `-eq` compares numbers: 3 equals 3. Choose by what the data is, not what it looks like.
</details>

**Q3.** A function sets `count=5` and afterwards the script's own `count` changed. Why, and the one-word fix?

<details>
<summary>Show answer</summary>

Bash variables are global by default, so the function overwrote the script's variable. Fix: declare it `local count` inside the function.
</details>

## Common mistakes
- Using `[` without spaces, or with unquoted possibly-empty variables.
- Forgetting `local` in functions.
- Iterating `$(cat file)` instead of `while read`.
- Wait loops without `sleep`.
- Building lists in space-separated strings where an array belongs.

## Key takeaways
`[[ ]]` for tests, globs for file loops, `while IFS= read -r` for lines, `local` in functions, and `"${array[@]}"` for lists. Quote everything, test with hostile input (spaces, empties, missing files).

## Further practice
Read `man bash` on conditional constructs and arrays, then refactor one of your earlier scripts into small functions.

## References
- [Bash conditional constructs](https://www.gnu.org/software/bash/manual/html_node/Conditional-Constructs.html)
- [Bash arrays](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)
