# Safe Scripting, Debugging, and Error Handling


## Learning objectives
- Use `set -euo pipefail` with an honest understanding of its limits.
- Validate inputs and quote paths so hostile input stays data.
- Debug scripts methodically and handle errors explicitly.

## Strict mode, and what it does not do
```bash
set -euo pipefail
```

- `-e`: exit when a command fails.
- `-u`: treat unset variables as errors.
- `-o pipefail`: a pipeline fails if any stage fails, not just the last.

These catch whole categories of bugs, but they are **not a complete error-handling system**, and `-e` in particular has a famous list of exceptions: commands inside `if` conditions, `&&`/`||` lists, and pipeline stages are allowed to fail without exiting (that is how conditions work at all). The professional posture: enable strict mode, *and* still check explicitly the commands whose failure matters:

```bash
if ! cp "$source" "$dest"; then
    printf 'copy failed: %s -> %s\n' "$source" "$dest" >&2
    exit 1
fi
```

## Input validation: treat input as data
```bash
if [[ $# -ne 1 ]]; then
    printf 'Usage: %s DIRECTORY\n' "$0" >&2
    exit 2
fi

target=$1
if [[ ! -d "$target" ]]; then
    printf 'Error: not a directory: %s\n' "$target" >&2
    exit 1
fi
```

Rules that keep scripts safe:

- Validate count, then shape, then existence, in that order.
- Usage errors exit `2`; operational failures exit `1`; success exits `0`. Consistent codes let callers react correctly.
- Messages about errors go to stderr (`>&2`), never stdout.
- **Never** build a command string from input and run it through `eval`, and never pass input to `sh -c`. Use arrays for argument lists and quote every expansion.

## Debugging without leaking
```bash
bash -n script.sh     # syntax check only; runs nothing
bash -x script.sh     # trace: prints each command as expanded
```

`bash -n` before every first run. `bash -x` when behavior surprises you: the trace shows exactly what each line became after expansion, which is usually where the surprise lives.

> [!WARNING]
> `bash -x` prints *expanded* commands, including any password or token a variable held. Never trace scripts that handle secrets, and never paste traces into tickets without reading them first.

## Six complete practical scripts
Study each, then do the exercises.

### 1. System information collector
```bash
#!/usr/bin/env bash
set -u
printf 'Host: %s\n' "$(hostname)"
printf 'Kernel: %s\n' "$(uname -r)"
printf 'Uptime: '
uptime -p 2>/dev/null || uptime
printf '\nMemory:\n'
free -h 2>/dev/null || printf 'free is unavailable\n'
printf '\nRoot filesystem:\n'
df -h /
```

Pattern: prefer the friendly command, fall back gracefully (`||`) when it is missing, and never assume an optional tool exists.

### 2. File existence checker
```bash
#!/usr/bin/env bash
set -u
if [[ $# -ne 1 ]]; then
    printf 'Usage: %s PATH\n' "$0" >&2
    exit 2
fi
path=$1
if [[ -f "$path" ]]; then
    printf 'Regular file: %s\n' "$path"
elif [[ -d "$path" ]]; then
    printf 'Directory: %s\n' "$path"
elif [[ -e "$path" ]]; then
    printf 'Exists, but is not a regular file or directory: %s\n' "$path"
else
    printf 'Not found: %s\n' "$path"
    exit 1
fi
```

Pattern: argument count first, then classify from most specific (`-f`) to most general (`-e`), with distinct exit codes for usage versus not-found.

### 3. Simple backup script
```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
    printf 'Usage: %s SOURCE_DIR BACKUP_PARENT\n' "$0" >&2
    exit 2
fi
source_dir=$1
backup_parent=$2
[[ -d "$source_dir" ]] || { printf 'Source directory missing\n' >&2; exit 1; }
mkdir -p -- "$backup_parent"
stamp=$(date +%Y%m%d-%H%M%S)
archive="$backup_parent/backup-$stamp.tar.gz"
tar -czf "$archive" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
printf 'Created: %s\n' "$archive"
```

Pattern: timestamped outputs so reruns never clobber; `tar -C` with `dirname`/`basename` so the archive stores *relative* paths that restore anywhere. An archive you have never restored is not a proven backup; test restores.

### 4. Log analyzer
```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 || ! -r "$1" ]]; then
    printf 'Usage: %s READABLE_LOG_FILE\n' "$0" >&2
    exit 2
fi
log=$1
printf 'Failed events: '
grep -ci 'failed' "$log" || true
printf 'Top IP-like tokens in matching lines:\n'
grep -i 'failed' "$log" |
    grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
    sort | uniq -c | sort -nr | head -n 10
```

Pattern: validate readability up front; `|| true` swallows grep's status 1 ("no matches") which is an outcome, not an error. The IP regex is extraction, not validation.

### 5. User input validator
```bash
#!/usr/bin/env bash
set -u
read -r -p 'Enter a short project label (letters, digits, dash): ' label
if [[ "$label" =~ ^[a-zA-Z0-9-]{1,32}$ ]]; then
    printf 'Accepted label: %s\n' "$label"
else
    printf 'Invalid label\n' >&2
    exit 1
fi
```

Pattern: allowlist validation with `=~` (Bash regex). Define what is *permitted* (1-32 letters, digits, dashes) instead of trying to enumerate what is dangerous.

### 6. Basic system monitoring
```bash
#!/usr/bin/env bash
set -u
interval=${1:-5}
if [[ ! "$interval" =~ ^[1-9][0-9]{0,2}$ ]]; then
    printf 'Interval must be an integer from 1 to 999 seconds\n' >&2
    exit 2
fi
while true; do
    printf '\n=== %s ===\n' "$(date)"
    uptime
    free -h
    df -h /
    sleep "$interval"
done
```

Pattern: every value reaching a command (`sleep` here) is validated first. Stop with `Ctrl-C`. A polling loop is a learning tool, not a monitoring system.

## Practice exercises
Try every task before opening its solution.

**Exercise 1.** Save script 3 (backup) as `backup.sh`, run `bash -n` on it, then back up a disposable directory and prove the archive contains relative paths.

<details>
<summary>Show a worked solution</summary>

```bash
bash -n backup.sh && echo "syntax ok"
mkdir -p ~/linux-lab/source-data && touch ~/linux-lab/source-data/{a,b}.txt
./backup.sh ~/linux-lab/source-data ~/linux-lab/backups
tar -tzf ~/linux-lab/backups/backup-*.tar.gz
```

The listing shows `source-data/` and `source-data/a.txt`, relative, not `/home/...` absolute paths.
</details>

**Exercise 2.** Break the backup script deliberately: run it with one argument, with a nonexistent source, and with a source path containing spaces. Describe which guard caught each case.

<details>
<summary>Show a worked solution</summary>

One argument: the `$# -ne 2` usage guard, exit 2. Nonexistent source: the `[[ -d ]]` guard, exit 1. Path with spaces: works correctly *because* every expansion is quoted; try removing the quotes and watch it fail, then restore them.
</details>

**Exercise 3.** Extend the log analyzer (script 4) to also print how many lines the log has in total, without breaking the no-matches case.

<details>
<summary>Show a worked solution</summary>

```bash
printf 'Total lines: '
wc -l < "$log"
```

`wc -l < file` prints just the number (no filename), and it never fails the way `grep -c` does on zero matches, so no `|| true` is needed.
</details>

**Exercise 4.** Add a `--help` option to the monitoring script (script 6) that prints usage and exits 0.

<details>
<summary>Show a worked solution</summary>

Insert after the shebang block:

```bash
if [[ "${1:-}" == "--help" ]]; then
    printf 'Usage: %s [INTERVAL_SECONDS]\n' "$0"
    exit 0
fi
```

Note the exit status: asking for help is success, so `0`, not `2`.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Under `set -e`, why does `if grep -q x file; then ...` not exit the script when the grep finds nothing?

<details>
<summary>Show answer</summary>

Commands in a condition context are exempt from `-e`; their status feeds the `if` instead. This exemption is exactly why `-e` alone is not error handling.
</details>

**Q2.** Why is `eval "rm -r $user_input"` catastrophic even when you "trust" the user?

<details>
<summary>Show answer</summary>

`eval` re-parses the string as shell code, so a value like `x; rm -rf ~` runs the second command too. Mistakes and attacks look identical to `eval`. Keep input in quoted variables; never re-parse it.
</details>

**Q3.** What is the difference between exit codes 1 and 2 in this lesson's scripts, and why does the distinction matter?

<details>
<summary>Show answer</summary>

2 means "you called me wrong" (usage); 1 means "you called me right but the work failed". A wrapper script can then retry operational failures while reporting usage bugs to the developer instead of retrying them forever.
</details>

## Common mistakes
- Assuming strict mode catches everything.
- `eval` or `sh -c` on user-controlled input.
- Unquoted paths.
- Tracing with `bash -x` around secrets.
- Running new scripts with `sudo` before testing them as a regular user.
- Backups never tested with a restore.

## Key takeaways
Validate count, shape, then existence; quote everything; keep input as data; check important failures explicitly even under strict mode. `bash -n` always, `bash -x` carefully.

## Further practice
Run [ShellCheck](https://www.shellcheck.net/) on every script in this lesson and on one of your own; it is the single fastest way to level up shell code.

## References
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/)
