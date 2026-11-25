# grep, sed, awk, and Practical Log Analysis


## Learning objectives
- Search text with grep and beginner regular expressions.
- Transform text with sed.
- Extract and aggregate fields with awk.
- Compose cut, sort, uniq, wc, tr, tee, and xargs into real analysis pipelines.

## grep: find the lines that matter
```bash
grep -n -i 'failed' auth.log        # line numbers, case-insensitive
grep -E 'error|warning' app.log     # extended regex: either word
grep -Rni 'password' ./config       # recursive through a directory
grep -c 'failed' auth.log           # count matching lines
grep -v 'health-check' app.log      # invert: everything EXCEPT matches
```

Key options: `-n` line numbers, `-i` ignore case, `-E` extended regular expressions, `-R` recursive, `-c` count, `-v` invert, `-o` print only the matched part.

A beginner regex survival kit:

- `^failed` matches lines *starting* with "failed"; `failed$` matches lines *ending* with it.
- `.` matches any single character; `.*` matches any run of characters.
- `[0-9]` matches a digit; `[0-9]{3}` matches exactly three.
- `error|warning` (with `-E`) matches either alternative.

> [!CAUTION]
> When grepping for credentials or secrets during an investigation, results can contain real passwords or keys. Do not paste raw matches into shared tickets or chat.

## sed: edit the stream
```bash
sed 's/old/new/g' file.txt          # replace every "old" with "new", print result
sed -n '1,5p' file.txt              # print only lines 1-5
sed '/^#/d' config.txt              # delete comment lines from the output
```

`sed` is a stream editor: by default it **prints** the transformed text and never touches the original file. The substitution command `s/old/new/g` replaces per line (`g` = all occurrences on the line, not just the first). In-place editing (`sed -i`) rewrites the file; behavior differs between GNU and BSD sed, so take a backup first (`sed -i.bak ...` keeps the original as `file.bak`).

## awk: work with columns
```bash
awk '{print $1, $2}' file.txt       # first two whitespace-separated fields
awk -F: '{print $1}' /etc/passwd    # colon-separated: usernames
awk '$3 >= 1000 {print $1, $3}' /etc/passwd   # conditions on fields
```

`awk` reads records (lines) split into fields: `$1` is the first field, `$0` the whole line, `-F:` sets the separator. A condition before the block filters which records the block applies to. This is the tool for "column questions" that `grep` cannot answer.

## The supporting cast
```bash
cut -d: -f1 /etc/passwd                      # simpler field extraction
sort names.txt | uniq                        # unique values...
sort names.txt | uniq -c | sort -nr          # ...or a ranked frequency table
wc -l file.txt                               # count lines
tr '[:upper:]' '[:lower:]' < file.txt        # normalize case
command | tee output.txt                     # print AND save simultaneously
printf '%s\0' f1 f2 | xargs -0 ls -l --      # build arguments safely
```

Two traps to memorize: `uniq` only merges **adjacent** duplicates, so `sort` must come first; and filenames containing spaces break naive `xargs`, so use `find -print0 | xargs -0` for anything real.

## Worked example: analyzing an authentication log
Save this as `sample-auth.log` (addresses are documentation ranges, safe to use):

```text
Nov 21 09:01:02 lab sshd[1201]: Failed password for invalid user guest from 192.0.2.10 port 50122 ssh2
Nov 21 09:02:11 lab sshd[1204]: Accepted publickey for analyst from 192.0.2.25 port 50123 ssh2
Nov 21 09:03:45 lab sshd[1210]: Failed password for root from 192.0.2.10 port 50130 ssh2
Nov 21 09:04:03 lab sshd[1212]: Failed password for analyst from 198.51.100.7 port 50131 ssh2
Nov 21 09:05:20 lab sshd[1218]: Connection closed by authenticating user analyst 192.0.2.25 port 50140 [preauth]
Nov 21 09:06:50 lab sshd[1221]: Failed password for invalid user test from 192.0.2.10 port 50155 ssh2
```

Build the analysis in stages, checking each before adding the next:

```bash
grep 'Failed password' sample-auth.log | wc -l
```

```text
4
```

```bash
grep 'Failed password' sample-auth.log | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | sort | uniq -c | sort -nr
```

```text
      3 192.0.2.10
      1 198.51.100.7
```

Read the second pipeline left to right: keep failure lines, extract IP-shaped tokens, sort so duplicates touch, count them, rank descending. The pattern matches IP-*shaped* text, not valid IPv4 (it would accept `999.999.999.999`); it is extraction, not validation.

## Practice exercises
Try every task before opening its solution.

**Exercise 1.** Using `sample-auth.log`: count the failed-password lines, then list just the usernames those attempts targeted.

<details>
<summary>Show a worked solution</summary>

```bash
grep -c 'Failed password' sample-auth.log
grep 'Failed password' sample-auth.log | sed 's/.*for //; s/ from.*//'
```

Output:

```text
4
invalid user guest
root
analyst
invalid user test
```

The `sed` command deletes everything up to "for " and everything from " from" onward, leaving the account name.
</details>

**Exercise 2.** List every username on your system with UID 1000 or higher, using `awk` on `/etc/passwd`.

<details>
<summary>Show a worked solution</summary>

```bash
awk -F: '$3 >= 1000 && $3 < 60000 {print $1, $3}' /etc/passwd
```

The upper bound excludes the `nobody` account (UID 65534).
</details>

**Exercise 3.** Produce a frequency table of the *services* mentioned in `sample-auth.log` (the word inside `[...]`), ranked by count.

<details>
<summary>Show a worked solution</summary>

```bash
grep -Eo '[a-z]+\[[0-9]+\]' sample-auth.log | cut -d'[' -f1 | sort | uniq -c | sort -nr
```

Output:

```text
      6 sshd
```

Extract the `name[pid]` token, cut the pid off, sort, count, rank.
</details>

**Exercise 4.** Save all failed-password lines to `failures.txt` while still seeing them on screen.

<details>
<summary>Show a worked solution</summary>

```bash
grep 'Failed password' sample-auth.log | tee failures.txt
```

`tee` writes to the file and to stdout at once, so the pipeline stays observable.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why does `uniq -c` almost always follow `sort`?

<details>
<summary>Show answer</summary>

`uniq` merges only adjacent duplicate lines. Without sorting first, identical lines scattered through the input are counted separately.
</details>

**Q2.** Does `sed 's/root/admin/' /etc/passwd` change the file?

<details>
<summary>Show answer</summary>

No. Without `-i`, sed prints the transformed stream to stdout and the file is untouched. (And do not run that with `-i` for real: editing account databases by hand is how systems break.)
</details>

**Q3.** In `awk -F: '{print $1}'`, what do `-F:` and `$1` mean?

<details>
<summary>Show answer</summary>

`-F:` splits each line on colons, and `$1` is the first resulting field, the username in `/etc/passwd`.
</details>

## Common mistakes
- Forgetting `uniq` needs sorted input.
- Calling a loose regex "validation".
- Editing the original log mid-investigation; work on a copy.
- Letting `xargs` split on whitespace when filenames may contain spaces.
- Reaching for a Python script when a four-stage pipeline answers the question in one line.

## Key takeaways
Filter (grep), transform (sed), extract (awk/cut), then count and rank (sort, uniq -c). Build pipelines one stage at a time and check each stage's output before adding the next.

## Further practice
Repeat the worked example with `awk` alone (hint: `awk '/Failed/' file | ...` versus a single `awk` program), then run the same analysis against a real log in `/var/log` on your VM.

## References
- [GNU grep manual](https://www.gnu.org/software/grep/manual/)
- [GNU sed manual](https://www.gnu.org/software/sed/manual/)
- [GNU awk manual](https://www.gnu.org/software/gawk/manual/)
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
