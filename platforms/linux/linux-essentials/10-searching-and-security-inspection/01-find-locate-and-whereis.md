# Find, locate, whereis, and which


## Learning objectives
- Search the filesystem by name, type, size, owner, permissions, and time.
- Choose correctly between live search (find) and indexed search (locate).
- Handle unusual filenames safely.

## find: the live search
`find` walks the filesystem **right now**, testing every entry against your predicates:

```bash
find ~/linux-lab -type f -name '*.log'
find /var/log -type f -size +10M 2>/dev/null
find /home -type f -user "$USER" -mtime -7 2>/dev/null
find / -xdev -type f -perm -0002 -print 2>/dev/null
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

The predicate kit:

- `-name '*.log'`: filename pattern (quote it, or the shell expands the `*` first).
- `-type f` regular file, `-type d` directory, `-type l` symlink.
- `-size +10M` larger than 10 MiB; `-size -1k` smaller than 1 KiB.
- `-user NAME` owner; `-group NAME` group.
- `-mtime -7` modified within the last seven 24-hour periods; `-mtime +30` older than thirty.
- `-perm -4000` has the SUID bit; `-perm -0002` is world-writable.
- `-xdev` stay on one filesystem (skips `/proc`, mounted disks).
- `2>/dev/null` hides permission-denied noise. Use it knowingly: it also hides directories the search *could not enter*, so the result is "everything I was allowed to see", not "everything".

Predicates combine with AND by default; `-o` is OR, `!` negates: `find . -type f ! -name '*.txt'`.

`find` can also **act**: `-delete` (dangerous, test with `-print` first) and `-exec cmd {} \;` (run a command per match).

## locate, whereis, which: the fast answers
```bash
locate ssh_config     # indexed filename search: instant
whereis ssh           # binary, source, and man page locations
which python3         # what PATH resolves this name to
command -v python3    # the script-safe version of which
```

`locate` searches a **database**, not the disk, which makes it instant and stale: a file created after the last database update is invisible until `updatedb` runs (usually scheduled nightly; may need sudo to run manually). Reach for `locate` when speed matters and yesterday is close enough; reach for `find` when correctness matters.

## Safe filename handling
Filenames may contain spaces, tabs, even newlines, which breaks naive parsing:

```bash
find . -type f -print0 | xargs -0 -r file
```

`-print0` separates results with NUL bytes (the only character a filename can never contain) and `xargs -0` reads them the same way. Any pipeline that consumes `find` output for real work should use this pair.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** In `~/linux-lab`, create files of different sizes and types, then find (a) every file larger than 1 KiB, (b) everything modified in the last day, (c) every directory.

<details>
<summary>Show a worked solution</summary>

```bash
cd ~/linux-lab
printf 'x%.0s' {1..2000} > big.txt
touch small.txt
mkdir -p subdir
find . -type f -size +1k
find . -mtime -1
find . -type d
```

`{1..2000}` is brace expansion producing 2000 arguments, a quick way to make a file with known size.
</details>

**Exercise 2.** Find every world-writable file anywhere in your home directory, suppressing only the errors you understand.

<details>
<summary>Show a worked solution</summary>

```bash
find ~ -type f -perm -0002 -print 2>/dev/null
```

Each result deserves a look: world-writable inside a home directory is rarely intended. Remember the suppression means unreadable directories were silently skipped.
</details>

**Exercise 3.** `locate notes.txt` finds nothing, but you created the file ten minutes ago. Explain, fix it, and prove both search tools can now find it.

<details>
<summary>Show a worked solution</summary>

The `locate` database has not been rebuilt since the file was created. Refresh it (may need sudo and take a minute):

```bash
sudo updatedb
locate notes.txt
find ~ -name notes.txt
```

`find` would have found it all along, because it searches live.
</details>

**Exercise 4.** Print the real type of every file in the current directory, robust against filenames containing spaces.

<details>
<summary>Show a worked solution</summary>

```bash
find . -maxdepth 1 -type f -print0 | xargs -0 -r file
```
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why must you quote `'*.log'` in `find . -name '*.log'`?

<details>
<summary>Show answer</summary>

Unquoted, the shell expands `*` against the *current directory* before `find` runs, so `find` receives literal filenames instead of the pattern. Quoted, the pattern reaches `find` intact and is applied at every level of the tree.
</details>

**Q2.** When is `locate` the wrong tool even though it is faster?

<details>
<summary>Show answer</summary>

When the file may have been created or moved since the last database update, or when you need attribute tests (size, permissions, time) that the index does not store.
</details>

**Q3.** What does `-xdev` protect against during `find /`?

<details>
<summary>Show answer</summary>

Crossing into other mounted filesystems: the virtual ones (`/proc`, `/sys`, `/dev`) full of pseudo-files, and any mounted disks or network shares you did not mean to crawl.
</details>

## Common mistakes
- Expecting `locate` to be current.
- Running `find /` without `-xdev`, a permission plan, or patience.
- Suppressing all errors and assuming the search was complete.
- Parsing `find` output line-by-line when filenames can contain newlines.
- Forgetting to quote patterns.

## Key takeaways
`find` for live, attribute-based, correct search; `locate` for instant, slightly stale name lookup; `-print0 | xargs -0` for anything filenames might break.

## Further practice
Read `man find`, `man locate`, and `man xargs`, then write one `find` command that answers a question you actually had this week ("which files in Downloads are over 100M?").

## References
- [GNU findutils](https://www.gnu.org/software/findutils/)
