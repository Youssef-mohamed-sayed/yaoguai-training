# Safe Scripting, Debugging, and Error Handling


## Learning objectives
- Use `set -euo pipefail` with an understanding of its limits.
- Validate inputs and quote paths safely.
- Debug scripts and handle errors explicitly.

## Strict-mode options
```bash
set -euo pipefail
```
- `-e`: exit on many unhandled command failures.
- `-u`: treat unset variables as errors.
- `-o pipefail`: a pipeline returns failure if a command in it fails.

These options are useful but **not a complete error-handling system**. `-e` has exceptions in conditionals, `&&`/`||` lists, pipelines, and functions. Explicitly check commands whose failure matters. Initialize optional variables and handle expected nonzero statuses.

## Input validation
```bash
if [[ $# -ne 1 ]]; then
    printf 'Usage: %s DIRECTORY
' "$0" >&2
    exit 2
fi

target=$1
if [[ ! -d "$target" ]]; then
    printf 'Error: not a directory: %s
' "$target" >&2
    exit 1
fi
```
Treat input as data, not shell syntax. Never build a command string and pass it to `eval`. Use arrays for command arguments and quote expansions.

## Debugging
```bash
bash -n script.sh       # syntax check
bash -x script.sh       # trace commands
```
`set -x` can reveal secrets expanded into commands; do not enable it around passwords, tokens, or sensitive data. Add meaningful messages to stderr and use appropriate exit codes.

## Six complete practical scripts

### 1. System information collector
```bash
#!/usr/bin/env bash
set -u
printf 'Host: %s
' "$(hostname)"
printf 'Kernel: %s
' "$(uname -r)"
printf 'Uptime: '
uptime -p 2>/dev/null || uptime
printf '
Memory:
'
free -h 2>/dev/null || printf 'free is unavailable
'
printf '
Root filesystem:
'
df -h /
```
Line by line: select Bash; enable unset-variable checks; print hostname and kernel; prefer human-readable uptime with fallback; show memory if available; show root filesystem capacity. `free` and `uptime -p` availability may vary.

### 2. File existence checker
```bash
#!/usr/bin/env bash
set -u
if [[ $# -ne 1 ]]; then
    printf 'Usage: %s PATH
' "$0" >&2
    exit 2
fi
path=$1
if [[ -f "$path" ]]; then
    printf 'Regular file: %s
' "$path"
elif [[ -d "$path" ]]; then
    printf 'Directory: %s
' "$path"
elif [[ -e "$path" ]]; then
    printf 'Exists, but is not a regular file or directory: %s
' "$path"
else
    printf 'Not found: %s
' "$path"
    exit 1
fi
```
The script requires exactly one argument, assigns it safely, tests regular file and directory before the broader existence test, and returns failure when absent.

### 3. Simple backup script
```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
    printf 'Usage: %s SOURCE_DIR BACKUP_PARENT
' "$0" >&2
    exit 2
fi
source_dir=$1
backup_parent=$2
[[ -d "$source_dir" ]] || { printf 'Source directory missing
' >&2; exit 1; }
mkdir -p -- "$backup_parent"
stamp=$(date +%Y%m%d-%H%M%S)
archive="$backup_parent/backup-$stamp.tar.gz"
tar -czf "$archive" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
printf 'Created: %s
' "$archive"
```
The script validates argument count and source directory, creates the destination parent, builds a timestamped archive, and uses `tar -C` so the archive contains the source directory rather than an absolute path. Use only directories you are authorized to back up. Test restore procedures; an archive that has never been restored is not a proven backup.

### 4. Log analyzer
```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 || ! -r "$1" ]]; then
    printf 'Usage: %s READABLE_LOG_FILE
' "$0" >&2
    exit 2
fi
log=$1
printf 'Failed events: '
grep -ci 'failed' "$log" || true
printf 'Top IP-like tokens in matching lines:
'
grep -i 'failed' "$log" |
    grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
    sort | uniq -c | sort -nr | head -n 10
```
The script validates readability, counts matching lines, extracts IP-like strings from failed lines, and ranks them. The regex is illustrative, not complete IPv4 validation. `|| true` handles grep's status 1 when there are no matches; it should not hide unrelated failures in more complex pipelines.

### 5. User input validator
```bash
#!/usr/bin/env bash
set -u
read -r -p 'Enter a short project label (letters, digits, dash): ' label
if [[ "$label" =~ ^[a-zA-Z0-9-]{1,32}$ ]]; then
    printf 'Accepted label: %s
' "$label"
else
    printf 'Invalid label
' >&2
    exit 1
fi
```
`read -r` reads literal input. The Bash regular-expression operator `=~` checks a 1–32 character allowlist. The accepted value is printed, not executed.

### 6. Basic system monitoring
```bash
#!/usr/bin/env bash
set -u
interval=${1:-5}
if [[ ! "$interval" =~ ^[1-9][0-9]{0,2}$ ]]; then
    printf 'Interval must be an integer from 1 to 999 seconds
' >&2
    exit 2
fi
while true; do
    printf '
=== %s ===
' "$(date)"
    uptime
    free -h
    df -h /
    sleep "$interval"
done
```
The interval is validated as a positive integer with at most three digits before it is passed to `sleep`. The loop prints a timestamp and basic resource information. Stop it with `Ctrl-C`. It is a simple polling tool, not a production monitoring system.

## Hands-on practice
- Save each script in its own file and run `bash -n` before execution.
- Test normal input, missing arguments, paths with spaces, and nonexistent paths.
- Run the backup script against a disposable directory and list the archive with `tar -tzf`.
- Hint: use a temporary directory under your home folder.

## Common mistakes
- Assuming strict mode catches every possible error.
- Using `eval` with user-controlled input.
- Forgetting to quote paths.
- Exposing secrets through `bash -x`.
- Running scripts with `sudo` before testing as a regular user.

## Key takeaways
Safe scripts validate inputs, quote variables, check important failures, and avoid interpreting untrusted data as commands.

## Further practice
Extend the log analyzer to accept a time window or output path, while preserving safe argument handling.

## References
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/) (static analysis for shell scripts)
