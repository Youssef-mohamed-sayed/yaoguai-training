# Find, locate, whereis, and which


## Learning objectives
- Search by filename, type, size, owner, permissions, and time.
- Compare live filesystem search with an indexed search.
- Handle unusual filenames safely.

## Commands
```bash
find ~/linux-lab -type f -name '*.log'
find /var/log -type f -size +10M 2>/dev/null
find /home -type f -user "$USER" -mtime -7 2>/dev/null
find / -xdev -type f -perm -0002 -print 2>/dev/null
find / -xdev -type f -perm -4000 -print 2>/dev/null
```
`find` traverses the filesystem at execution time. Common predicates:
- `-name` matches a filename pattern.
- `-type f` regular file; `-type d` directory; `-type l` symlink.
- `-size +10M` larger than 10 MiB (GNU find syntax).
- `-user NAME` owner match.
- `-mtime -7` modified within the last seven 24-hour periods.
- `-perm -4000` has SUID bit set.
- `-xdev` avoids crossing filesystem boundaries.
- `2>/dev/null` hides permission-denied diagnostics; use it only when you understand that errors are being suppressed.

Other tools:
```bash
locate ssh_config
whereis ssh
which python3
grep -Rni 'Listen' /etc/ssh
```
`locate` searches a database and can miss recently created files until its database is updated. `updatedb` refreshes that database and may require elevated privileges; it is not installed or scheduled identically everywhere. `whereis` searches standard locations for binaries, source, and manual pages. `which` searches PATH; `command -v` is often better in shell scripts.

## Safe filename handling
```bash
find . -type f -print0 | xargs -0 -r file
```
NUL delimiters safely represent filenames containing spaces, tabs, or newlines.

## Hands-on practice
- Create files of different sizes and extensions in `~/linux-lab`.
- Find files larger than 1 KiB and files modified in the last day.
- Find world-writable files inside your lab directory.
- Hint: use `-size +1k` and `-perm -0002`.

## Common mistakes
- Expecting `locate` to be immediately current.
- Running `find /` without considering permissions and system load.
- Suppressing all errors and assuming the search was complete.
- Parsing `find` output line-by-line when filenames can contain newlines.

## Key takeaways
Use `find` for live, attribute-based searches. Treat indexed results and suppressed errors carefully.

## Further practice
Read `man find`, `man locate`, and `man xargs`.

## References
- [GNU findutils](https://www.gnu.org/software/findutils/)
