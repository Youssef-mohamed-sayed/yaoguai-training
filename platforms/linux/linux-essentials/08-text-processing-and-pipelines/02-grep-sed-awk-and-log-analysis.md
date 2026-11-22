# grep, sed, awk, and Practical Log Analysis


## Learning objectives
- Search text with grep and beginner regular expressions.
- Transform text with sed.
- Extract and aggregate fields with awk.
- Combine cut, sort, uniq, wc, tr, tee, and xargs.

## Core tools
```bash
grep -n -i 'failed' auth.log
grep -E 'error|warning' application.log
grep -Rni 'password' ./config
```
`grep` searches lines. `-n` prints line numbers, `-i` ignores case, `-E` enables extended regular expressions, and `-R` recursively searches directories. Avoid dumping secret files into shared logs or tickets.

```bash
sed 's/old/new/g' file.txt
sed -n '1,5p' file.txt
```
`sed` is a stream editor. The first command replaces each `old` with `new` on each line in output; it does not modify the file in place. `-n` suppresses default printing, and `p` prints selected lines. In-place editing (`-i`) is platform-sensitive; make a backup first.

```bash
awk '{print $1, $2}' file.txt
awk -F: '{print $1}' /etc/passwd
awk '$3 > 1000 {print $1, $3}' /etc/passwd
```
`awk` processes records (usually lines) and fields. `-F:` sets the field separator. `$1` is the first field; `$0` is the full record.

Other useful commands:
```bash
cut -d: -f1 /etc/passwd
sort names.txt
sort names.txt | uniq
sort names.txt | uniq -c | sort -nr
wc -l file.txt
tr '[:upper:]' '[:lower:]' < file.txt
command | tee output.txt
printf '%s
' file1 file2 | xargs -r ls -l --
```
`uniq` detects adjacent duplicate lines, so sort first for global counts. `xargs` builds command arguments from input; use `-0` with `find -print0` for filenames containing whitespace or unusual characters.

## Progressive examples
1. Case-insensitive failure lines:
   `grep -ni 'failed' auth.log`
2. Count failure lines:
   `grep -ci 'failed' auth.log`
3. Count source IP-like tokens in a controlled sample:
   `grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' auth.log | sort | uniq -c | sort -nr`
4. Extract colon-delimited usernames:
   `cut -d: -f1 /etc/passwd`

The IP regular expression above is illustrative token extraction, **not complete IPv4 validation**. It can match invalid octets such as 999 and does not validate context.

## Sample log
Save as `sample-auth.log`:
```text
Nov 21 09:01:02 lab sshd[1201]: Failed password for invalid user guest from 192.0.2.10 port 50122 ssh2
Nov 21 09:02:11 lab sshd[1204]: Accepted publickey for analyst from 192.0.2.25 port 50123 ssh2
Nov 21 09:03:45 lab sshd[1210]: Failed password for root from 192.0.2.10 port 50130 ssh2
Nov 21 09:04:03 lab sshd[1212]: Failed password for analyst from 198.51.100.7 port 50131 ssh2
Nov 21 09:05:20 lab sshd[1218]: Connection closed by authenticating user analyst 192.0.2.25 port 50140 [preauth]
Nov 21 09:06:50 lab sshd[1221]: Failed password for invalid user test from 192.0.2.10 port 50155 ssh2
```
The addresses are from documentation ranges and are safe examples.

## Hands-on practice: analyze the sample
- Count failed-password lines.
- Extract and rank IP-like tokens from failed lines.
- Print only usernames from `/etc/passwd`.
- Save matching lines to a report using `tee`.
- Hint: filter first, then extract, then count with `sort | uniq -c`.

## Common mistakes
- Forgetting `uniq` only combines adjacent duplicates.
- Using an overly broad regular expression and calling it validation.
- Editing the original log while investigating.
- Splitting filenames with spaces using unsafe `xargs` input.

## Key takeaways
Text-processing commands are composable. Filter, extract, normalize, and count in separate pipeline stages.

## Further practice
Use `awk` to count log events by field and compare the result with `grep -c`.

## References
- [GNU grep manual](https://www.gnu.org/software/grep/manual/)
- [GNU sed manual](https://www.gnu.org/software/sed/manual/)
- [GNU awk manual](https://www.gnu.org/software/gawk/manual/)
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
