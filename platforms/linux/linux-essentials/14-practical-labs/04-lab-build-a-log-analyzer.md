# Lab: Build a Bash Log Analyzer


## Lab objectives
Create a safe Bash script that summarizes a log file.

## Requirements
- Accept exactly one readable log file argument.
- Print the total number of lines.
- Count lines containing `Failed`.
- Extract IP-like tokens from failed lines and rank them.
- Print a clear message when no matching lines exist.
- Return nonzero for invalid input.
- Do not modify the source log.

## Starter implementation
```bash
#!/usr/bin/env bash
set -u

if [[ $# -ne 1 || ! -r "$1" || ! -f "$1" ]]; then
    printf 'Usage: %s READABLE_LOG_FILE
' "$0" >&2
    exit 2
fi

log=$1
printf 'Lines: '
wc -l < "$log"

matches=$(grep -ic 'Failed' "$log" || true)
printf 'Failed lines: %s
' "$matches"

if (( matches > 0 )); then
    grep -i 'Failed' "$log" |
      grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
      sort | uniq -c | sort -nr
else
    printf 'No failed events found.
'
fi
```
Line-by-line: Bash is selected; unset-variable checking is enabled; argument count, readability, and regular-file status are checked; `wc` counts lines; `grep -c` counts matching lines; `|| true` handles the no-match status; arithmetic tests whether the count is positive; the pipeline extracts, sorts, and counts tokens.

The regex extracts IP-like tokens only; it is not a complete IP validator. For production use, consider structured logs and a parser that validates addresses.

## Test cases
- Valid sample with failed events.
- Valid sample with no failed events.
- Missing argument.
- Two arguments.
- Nonexistent file.
- File path containing spaces.

## Deliverable
Submit the script, test table, and a note describing the limitations of text-based parsing.
