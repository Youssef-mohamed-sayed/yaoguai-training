# Reading and Inspecting Files


## Learning objectives
- Choose the right tool to read a file based on its size and your purpose.
- Inspect the beginning or end of large files, and follow growing logs live.
- Explain why unknown and binary files should never be dumped blindly to the terminal.

## The right reader for the job

```bash
cat file.txt
less file.txt
head -n 10 file.txt
tail -n 20 file.txt
tail -f application.log
file unknown.bin
stat unknown.bin
```

- `cat` writes whole files to standard output. Perfect for short files and for feeding other commands; painful for anything longer than a screen, because the beginning scrolls away before you can read it.
- `less` is the pager: open, scroll, and search without loading everything at once. Essential keys: `/pattern` to search forward, `n` / `N` for next / previous match, `g` / `G` for top / bottom, `q` to quit.
- `head` and `tail` show the first or last lines; `-n` sets how many. Most real questions about a file are answered by one of its ends.
- `tail -f` follows a file as it grows, printing new lines as they arrive. This is how you watch a log while reproducing a problem. `Ctrl-C` stops following.

Sample session:

```text
$ tail -n 3 /var/log/dpkg.log
2026-11-25 03:58:12 status installed bash:amd64 5.2.21-2ubuntu4
2026-11-25 03:58:13 trigproc libc-bin:amd64 2.39-0ubuntu8
2026-11-25 03:58:13 status installed libc-bin:amd64 2.39-0ubuntu8
```

(Log paths vary by distribution; on systemd systems much of this lives in the journal instead, see module 07.)

## Identify before you display
Use `file` before assuming something is text:

```bash
file unknown.bin
```

Output:

```text
unknown.bin: ELF 64-bit LSB pie executable, x86-64, ...
```

Printing arbitrary binary data with `cat` floods your terminal with control characters: the display can garble, beep, or become unreadable until you run `reset`. Worse, a maliciously crafted file can exploit that trust. The habit: unknown file, `file` first; if it is binary, inspect it with purpose-built tools (`stat`, `strings` for readable fragments) rather than dumping it.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Read `/etc/os-release` three ways: with `cat`, with `less`, and with `head` limited to its first three lines.

<details>
<summary>Show a worked solution</summary>

```bash
cat /etc/os-release
less /etc/os-release     # press q to quit
head -n 3 /etc/os-release
```

Output of the last:

```text
NAME="Ubuntu"
VERSION="24.04 LTS (Noble Numbat)"
ID=ubuntu
```
</details>

**Exercise 2.** Create a growing log and watch it live: make `~/linux-lab/watch.log` with one line, start `tail -f` on it, then from a second terminal append two more lines and describe what the first terminal does.

<details>
<summary>Show a worked solution</summary>

Terminal 1:

```bash
printf 'line one\n' > ~/linux-lab/watch.log
tail -f ~/linux-lab/watch.log
```

Terminal 2:

```bash
printf 'line two\n' >> ~/linux-lab/watch.log
printf 'line three\n' >> ~/linux-lab/watch.log
```

Terminal 1 prints each new line the moment it is appended. `>>` appends; a single `>` would overwrite. Stop following with `Ctrl-C`.
</details>

**Exercise 3.** You downloaded a 2 GB file named `backup` with no extension. Identify its type and read just enough to confirm what it begins with, without loading it into memory or flooding the terminal.

<details>
<summary>Show a worked solution</summary>

```bash
file backup
stat backup
head -c 200 backup | less
```

`file` reports the real type (an archive, a database, an image). `head -c 200` reads only 200 bytes, piped into `less` so even those cannot flood the display. Never `cat` a file this size.
</details>

**Exercise 4.** A teammate says "the log shows an error somewhere near the end." Show them one command that answers it, and one that would let them watch the error happen again.

<details>
<summary>Show a worked solution</summary>

```bash
tail -n 50 application.log     # see the recent end
tail -f application.log        # watch new lines live while they reproduce the issue
```

Add a search in a pager (`less application.log`, then `/error`) when "somewhere" is bigger than the tail.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why is `cat huge.log` worse than `less huge.log`, beyond convenience?

<details>
<summary>Show answer</summary>

`cat` streams the whole file through the terminal, which must render megabytes of output while you wait, and the part you wanted scrolls away. `less` reads on demand, starts instantly, and lets you search.
</details>

**Q2.** What is the safe first command on any file you do not recognize, and what does it actually inspect?

<details>
<summary>Show answer</summary>

`file name`. It reads the file's leading bytes and matches them against known signatures, reporting the real content type regardless of the name or extension.
</details>

**Q3.** `tail -f` shows nothing new, but you can see the application's log growing in another window. Name a likely reason.

<details>
<summary>Show answer</summary>

You are following the wrong file: the application may write a rotated or date-stamped name (`app.log.1`, `app-2026-11-25.log`) while you watch an old one. `ls -lt` in the log directory shows which file is actually being written.
</details>

## Common mistakes
- Using `cat` on huge files and waiting while the terminal drowns.
- Treating binary output as meaningful text (or letting it garble the terminal; `reset` fixes the display).
- Forgetting `tail -f` is still running in a background tab.
- Overwriting a file with `>` when `>>` (append) was intended.

## Key takeaways
Match the reader to the file: `cat` for short, `less` for long, `head`/`tail` for ends, `tail -f` for live logs. Identify unknown files with `file` before displaying anything.

## Further practice
Open a real log in `less`, search for `error` and `fail`, and jump between matches with `n` and `N`. Then follow a log with `tail -f` while you trigger one event in the matching application.

## References
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
- [less manual](https://greenwoodsoftware.com/less/)
