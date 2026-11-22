# Conditionals, Loops, Functions, and Arrays


## Learning objectives
- Use `if`, `elif`, `else`, `case`, `for`, `while`, and `until`.
- Test strings, numbers, and files.
- Define functions and beginner-level arrays.

## Tests
```bash
[[ -f "$path" ]]   # regular file exists
[[ -d "$path" ]]   # directory exists
[[ -r "$path" ]]   # readable by current process
[[ -x "$path" ]]   # executable or directory searchable
[[ "$name" == "admin" ]]
[[ "$count" -ge 3 ]]
```
Bash `[[ ... ]]` is a Bash keyword and safer/more expressive than the historical `[ ... ]` in several cases. `test` and `[ ... ]` are widely available but have stricter quoting and parsing rules. For POSIX shell portability, use POSIX-compatible tests.

## Conditionals and case
```bash
if [[ -f "$1" ]]; then
    printf 'File exists
'
elif [[ -d "$1" ]]; then
    printf 'Directory exists
'
else
    printf 'Path not found
'
fi

case "${1:-}" in
    start) printf 'Starting
' ;;
    stop)  printf 'Stopping
' ;;
    *)     printf 'Usage: %s {start|stop}
' "$0"; exit 2 ;;
esac
```

## Loops
```bash
for item in alpha beta gamma; do
    printf '%s
' "$item"
done

while IFS= read -r line; do
    printf 'Line: %s
' "$line"
done < input.txt

until [[ -e ready.flag ]]; do
    sleep 1
done
```
`while` repeats while its condition succeeds; `until` repeats until its condition succeeds. Avoid busy-wait loops without a delay.

## Functions and arrays
```bash
greet() {
    local name="${1:-learner}"
    printf 'Hello, %s
' "$name"
}
greet "Linux student"

tools=(grep awk sed)
printf '%s
' "${tools[@]}"
```
`local` limits a variable to the function. `"${array[@]}"` preserves each array element as a separate word.

## Arithmetic and strings
```bash
count=$((count + 1))
if [[ -n "$value" ]]; then printf 'non-empty
'; fi
if [[ "$value" == *linux* ]]; then printf 'contains linux
'; fi
```
Arithmetic expansion uses `$(( ... ))`. `-n` tests non-empty strings; `-z` tests empty strings.

## Hands-on practice
- Write a script that accepts a directory and lists regular files.
- Add a `case` statement for `--help`.
- Store three filenames in an array and loop over them.
- Hint: validate that the directory exists before calling `find`.

## Common mistakes
- Using `[` without spaces around its arguments.
- Forgetting `local` and accidentally changing global variables.
- Iterating over unquoted `$@` or command output with spaces.
- Using `for x in $(cat file)` to read lines; it breaks on whitespace and glob characters.

## Key takeaways
Use `[[ ]]` in Bash, quote expansions, and read files line-by-line with `IFS= read -r`.

## Further practice
Read `man bash` sections on conditional constructs, loops, functions, and arrays.

## References
- [Bash conditional constructs](https://www.gnu.org/software/bash/manual/html_node/Conditional-Constructs.html)
