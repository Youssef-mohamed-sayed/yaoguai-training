# Navigation and Shell Efficiency


## Learning objectives
- Navigate the filesystem confidently with `pwd`, `cd`, and `ls`.
- Choose between absolute and relative paths, and predict what each resolves to.
- Read a long `ls` listing field by field.
- Move fast with history, completion, and directory shortcuts.

## Where am I: the working directory
Every process, including your shell, has a **current working directory**. Relative paths are resolved against it, which is why the same command can do different things in different places. Your first habit: confirm your location before and after moving.

```bash
pwd
```

Output:

```text
/home/learner
```

## Absolute and relative paths
An **absolute path** starts at the filesystem root `/` and works from anywhere: `/etc/ssh/sshd_config` means the same thing no matter where you stand.

A **relative path** starts from your current directory. If `pwd` is `/home/learner`, then `docs/notes.txt` means `/home/learner/docs/notes.txt`. Three building blocks make relative paths expressive:

- `.` is the current directory. `./script.sh` runs a script in the current directory (deliberately *not* searched by `PATH`).
- `..` is the parent directory. From `/home/learner/docs`, `..` is `/home/learner`, and `../Pictures` is `/home/learner/Pictures`.
- `~` is your home directory, expanded by the shell before the command runs.

Compare:

```bash
cd /tmp        # absolute: /tmp, from anywhere
cd tmp         # relative: the "tmp" inside your current directory, if it exists
cd ..          # up one level
cd ../..       # up two levels
cd ~           # home
cd -           # back to the previous directory (toggle)
cd             # bare cd also goes home
```

`cd -` is worth learning early: it jumps back to wherever you were before the last `cd`, and prints that path. Two `cd -` in a row toggle you between two directories, which is ideal for comparing or copying between them.

> [!WARNING]
> `cd /tmp` and `cd tmp` are not the same command. Mixing up absolute and relative paths is how files get created in the wrong place, and how `rm -r` hits the wrong tree.

## Listing directories: ls in depth
`ls` shows what a path contains. The options you will use daily:

```bash
ls            # names only
ls -l         # long format: permissions, owner, size, time
ls -a         # include hidden entries (names starting with a dot)
ls -A         # hidden entries except "." and ".."
ls -h         # with -l, human-readable sizes (K, M, G)
ls -t         # sort by modification time, newest first
ls -r         # reverse the sort order
ls -lah /var/log   # the classic bundle
```

A long listing line rewards careful reading:

```text
drwxr-xr-x 3 root root 4096 Nov 25 03:58 ssh
```

Field by field: `d` says this is a directory (`-` for a regular file, `l` for a symlink); `rwxr-xr-x` is the permission set you will study in module 06; `3` is the link count; then owner, group, size in bytes, last modification time, and the name.

Two views of the bigger picture:

```bash
tree -L 2 ~/linux-lab
find /etc -maxdepth 1 -type d
```

`tree` draws a hierarchy (`-L` limits depth) but may need installation. `find` is always available; you will learn it properly in module 10.

Hidden files matter more than beginners expect. Configuration for your whole environment lives in dotfiles like `~/.bashrc` and `~/.ssh/`. Plain `ls` hides them; `ls -a` is how you see the real contents of a home directory.

## Shell efficiency: doing less typing
Everything from lesson 01 applies here; these habits pay off specifically while navigating:

- **Tab completion** is your spell-checker for paths. Type `cd /etc/ss` + Tab and the shell completes `ssh/`. Press Tab twice to list candidates when the prefix is ambiguous. If nothing completes, the path probably does not exist.
- **History search**: `Ctrl-R`, then type part of an old command, Enter to run it or the arrow keys to edit it first. Far safer than retyping a long path.
- **Line editing**: `Ctrl-A` / `Ctrl-E` to the line start/end, `Ctrl-U` to delete backwards, `Ctrl-K` to delete forwards. Fixing a typo at the start of a long command takes one keystroke, not twenty.
- **Reuse arguments**: `!$` expands to the last argument of the previous command. `mkdir project && cd !$` creates a directory and enters it.

```bash
mkdir -p ~/linux-lab/notes && cd !$
pwd
history | tail -n 5
```

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Starting anywhere, go to `/etc` with an absolute path, then to its parent with a relative path, then home, then back to where you just were, in four commands total.

<details>
<summary>Show a worked solution</summary>

```bash
cd /etc
cd ..
cd
cd -
```

`cd /etc` is absolute; `cd ..` moves to `/`; bare `cd` goes home; `cd -` returns to `/`.
</details>

**Exercise 2.** Create the path `~/linux-lab/deep/nested/dir` with a single command, enter it, then return to `~/linux-lab` without typing the words `linux-lab` again.

<details>
<summary>Show a worked solution</summary>

```bash
mkdir -p ~/linux-lab/deep/nested/dir
cd ~/linux-lab/deep/nested/dir
cd ../../..
pwd
```

Output:

```text
/home/learner/linux-lab
```

Each `..` climbs one level: `nested`, `deep`, `linux-lab`.
</details>

**Exercise 3.** List all entries in your home directory including hidden ones, in long format with human-readable sizes, sorted so the most recently changed appear last.

<details>
<summary>Show a worked solution</summary>

```bash
ls -lahrt ~
```

`-t` sorts newest first; `-r` reverses it so the newest end up at the bottom, nearest your prompt.
</details>

**Exercise 4.** In the `ls -l` line below, what is the owner's name, is this a file or a directory, and what is its size?

```text
-rw-r----- 1 learner labteam 1280 Nov 24 22:41 notes.txt
```

<details>
<summary>Show answer</summary>

Owner `learner` (group `labteam`), a regular file (leading `-`), 1280 bytes.
</details>

**Exercise 5.** Using history and editing keys only: re-run the last `ls` command you typed, but change its target to `/var/log` before running it.

<details>
<summary>Show a worked solution</summary>

Press `Ctrl-R`, type `ls`, press the Right arrow (or `Ctrl-E`) to load the line for editing instead of running it, edit the path to `/var/log` using `Ctrl-A` / arrows and `Ctrl-K` / `Ctrl-U` to trim, then press Enter.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You are in `/home/learner/docs` and run `cd Pictures`. The shell reports "No such file or directory", yet `~/Pictures` exists. What went wrong?

<details>
<summary>Show answer</summary>

`cd Pictures` is relative: it looks for `/home/learner/docs/Pictures`, which does not exist. Use `cd ~/Pictures` (absolute via home) or `cd ../Pictures`.
</details>

**Q2.** What is the difference between `ls -a` and `ls -A`, and why does the difference matter when scripting?

<details>
<summary>Show answer</summary>

`ls -a` includes `.` and `..` themselves; `ls -A` shows hidden files but excludes them. In a loop like `for f in *` or when parsing `ls -a`, the `.` and `..` entries can make a script act on the current and parent directories unexpectedly.
</details>

**Q3.** After `mkdir reports && cd reports`, which single shortcut takes you back out without typing a path?

<details>
<summary>Show answer</summary>

`cd -` (it returns to the previous working directory). `cd ..` also works here, but `cd -` works no matter where you came from.
</details>

**Q4.** Why does `./backup.sh` work when `backup.sh` alone gives "command not found", even while you are standing in the script's directory?

<details>
<summary>Show answer</summary>

For safety, the current directory is not in `PATH`, so the shell never searches it. `./backup.sh` is an explicit relative path to the file, bypassing the `PATH` search.
</details>

## Common mistakes
- Confusing `cd /tmp` with `cd tmp`; check `pwd` when in doubt.
- Forgetting that relative paths depend on the current directory, especially inside scripts.
- Assuming `ls` shows hidden files; it does not.
- Retyping long commands instead of using `Ctrl-R`, Tab, and `!$`.
- Running `./something` from an untrusted directory just because it exists; executing local files is an explicit action for a reason.

## Key takeaways
`pwd` tells you the truth about where you are; absolute paths are unambiguous and relative paths are short. Read `ls -l` field by field, and let Tab, history search, and `cd -` carry the typing for you.

## Further practice
Spend one session moving only between `/`, `/etc`, `/var/log`, `/tmp`, and your home directory without a graphical file manager, using each shortcut from this lesson at least once. Then explore `man 7 glob` for the full pattern language you met in lesson 01.

## References
- [Bash builtins: cd](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- [ls(1)](https://man7.org/linux/man-pages/man1/ls.1.html)
- [find(1)](https://man7.org/linux/man-pages/man1/find.1.html)
