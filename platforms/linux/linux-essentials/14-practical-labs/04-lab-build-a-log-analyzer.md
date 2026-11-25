# Lab: Build a Bash Log Analyzer


## Lab objectives
Write, test, and critique a safe Bash script that summarizes a log file. This is the capstone for module 12: argument validation, strict mode, pipelines, and honest exit codes in one artifact.

## Requirements
- Accept exactly one readable log file argument.
- Print the total number of lines.
- Count lines containing `Failed`.
- Extract IP-like tokens from failed lines and rank them.
- Print a clear message when no matching lines exist.
- Return nonzero for invalid input.
- Never modify the source log.

## Starter implementation
```bash
#!/usr/bin/env bash
set -u

if [[ $# -ne 1 || ! -r "$1" || ! -f "$1" ]]; then
    printf 'Usage: %s READABLE_LOG_FILE\n' "$0" >&2
    exit 2
fi

log=$1
printf 'Lines: '
wc -l < "$log"

matches=$(grep -ic 'Failed' "$log" || true)
printf 'Failed lines: %s\n' "$matches"

if (( matches > 0 )); then
    grep -i 'Failed' "$log" |
      grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
      sort | uniq -c | sort -nr
else
    printf 'No failed events found.\n'
fi
```

Line by line: the shebang selects Bash; `set -u` fails on unset variables; the guard checks argument count, readability, *and* regular-file status before anything touches the file; `wc -l < file` prints just the count; `grep -c` counts matches with `|| true` absorbing the no-match status; the arithmetic test branches on whether the count is positive.

The regex extracts IP-*shaped* tokens only; it accepts impossible octets like `999`. For production use, parse structured logs and validate addresses properly.

## Test plan
Build this table and actually run every row:

| # | Input | Expected |
|---|---|---|
| 1 | sample with failed events | counts + ranked tokens, exit 0 |
| 2 | sample with no failed events | "No failed events found.", exit 0 |
| 3 | no argument | usage on stderr, exit 2 |
| 4 | two arguments | usage on stderr, exit 2 |
| 5 | nonexistent file | usage on stderr, exit 2 |
| 6 | path containing spaces | works (quoting test) |
| 7 | a directory as the argument | usage on stderr, exit 2 |

Test data for rows 1 and 2: reuse `sample-auth.log` from lab 02, and make an empty-failures variant with `grep -v Failed sample-auth.log > clean.log`.

## Validation
**Check 1.** Why does the guard test `! -r "$1" || ! -f "$1"` in addition to the argument count?

<details>
<summary>Show answer</summary>

Count alone says nothing about usability: the path could be missing, unreadable, or a directory (which passes a read test on some systems but produces garbage downstream). Row 7 of the test plan exists precisely for the `-f` check.
</details>

**Check 2.** Why `matches=$(grep -ic ... || true)` instead of relying on `set -e`-style behavior?

<details>
<summary>Show answer</summary>

`grep` exits 1 when nothing matches, which is a normal outcome here, not an error. `|| true` converts "zero matches" into a successful command substitution so the script continues and reports `0`; under strict mode without it, the script would die silently at that line.
</details>

**Check 3.** Run row 6. If it fails, what is the most likely defect in a script?

<details>
<summary>Show answer</summary>

An unquoted expansion: `"$log"` written as `$log` splits `my logs/auth.log` into two arguments. The quoting is what the row tests.
</details>

**Check 4.** Name two limitations of this text-scraping approach for real logs.

<details>
<summary>Show answer</summary>

Any two of: message formats vary by event type and version, so field positions drift; the IP regex is not validation; timestamps are not parsed, so no time-window analysis; a crafted log line could inject misleading "evidence". Structured logs (JSON) and a real parser address all four.
</details>

## Extension (optional)
Add an optional second argument `--since "HH:MM"` that only counts events after that time, while keeping every existing test row passing.

## Deliverable
Submit the script, the completed seven-row test table with actual outputs, and a short note on the limitations of text-based parsing.

## Common mistakes
- Testing only the happy path (row 1).
- Letting the script print usage to stdout.
- "Fixing" the no-matches case by removing the message instead of handling grep's status.
