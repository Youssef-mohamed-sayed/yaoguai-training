# Create, Copy, Move, and Remove Files


## Learning objectives
- Create, copy, move, and remove files and directories deliberately.
- Choose the right options for each operation and predict the result before pressing Enter.
- Explain the risks of recursive deletion and apply a safe-deletion routine every time.

## Commands

```bash
mkdir -p ~/linux-lab/{input,backup}
touch ~/linux-lab/input/notes.txt
cp ~/linux-lab/input/notes.txt ~/linux-lab/backup/
mv ~/linux-lab/backup/notes.txt ~/linux-lab/backup/notes-old.txt
rmdir ~/linux-lab/empty-dir
```

What each command really does:

- `mkdir -p`: creates parent directories as needed and does not fail if the target already exists. Without `-p`, `mkdir a/b/c` fails if `a/b` does not exist. The `{input,backup}` brace expansion creates both directories in one command.
- `touch`: creates an empty file if it is absent, or **updates the timestamps** of an existing file without changing its content. It is not a "make file" command so much as a "make or freshen" command.
- `cp`: copies. Useful options: `-r` copies directories recursively (required, or `cp` refuses directories), `-i` prompts before overwriting, `-a` archives, preserving permissions, timestamps, and links as far as possible. `cp file dir/` places a copy inside `dir`; `cp file newname` copies to a new name in place.
- `mv`: moves or renames. Same filesystem or not, the *name* changes; across filesystems the data is actually copied and the original removed. `-i` prompts before overwriting.
- `rmdir`: removes **empty** directories only. Its refusal to remove anything non-empty makes it the safe choice.
- `rm`: removes files. `-r` descends into directory trees; `-f` suppresses prompts and missing-file errors. `rm` does not move anything to a trash can: deletion is immediate and effectively permanent.

### Safe deletion routine
Before any deletion that matters:

1. Print the current directory with `pwd`.
2. Inspect the exact target with `ls -la -- target`.
3. Prefer a narrow, fully spelled-out path and interactive mode (`rm -i`) while learning.
4. Avoid `rm -rf` combined with variables, wildcards, or paths you have not just verified.
5. Never paste a command containing `sudo rm -rf` from an untrusted source.

Example:

```bash
rm -i ~/linux-lab/input/old.txt
```

Output:

```text
rm: remove regular empty file '/home/learner/linux-lab/input/old.txt'? y
```

> [!CAUTION]
> The classic disaster is a variable or space in the wrong place: `rm -rf $dir/*` with an empty `dir` becomes `rm -rf /*`. Quote variables, verify paths, and test destructive commands on lab data only.

## Inspecting what you created
```bash
file ~/linux-lab/input/notes.txt
stat ~/linux-lab/input/notes.txt
find ~/linux-lab -maxdepth 2 -type f -print
```

`file` identifies content, `stat` shows full metadata, and that `find` one-liner lists every file under your lab to two levels deep. Run it after each exercise to confirm the tree looks the way you think it does.

## Practice exercises
Do these in your own terminal, inside `~/linux-lab` only. Try every task before opening its solution.

**Exercise 1.** Create `~/linux-lab/input` and `~/linux-lab/output` with a single command, then create three empty files in `input` named `a.txt`, `b.txt`, and `c.txt` with one command each (or one clever command).

<details>
<summary>Show a worked solution</summary>

```bash
mkdir -p ~/linux-lab/{input,output}
touch ~/linux-lab/input/{a,b,c}.txt
ls ~/linux-lab/input
```

Output:

```text
a.txt  b.txt  c.txt
```

Brace expansion turns one `touch` into three paths.
</details>

**Exercise 2.** Copy `a.txt` into `output`, then rename the copy to `a-archived.txt`, then move it back into `input`. Verify each step with `ls`.

<details>
<summary>Show a worked solution</summary>

```bash
cp ~/linux-lab/input/a.txt ~/linux-lab/output/
mv ~/linux-lab/output/a.txt ~/linux-lab/output/a-archived.txt
mv ~/linux-lab/output/a-archived.txt ~/linux-lab/input/
ls ~/linux-lab/input ~/linux-lab/output
```

`input` ends with four files and `output` ends empty.
</details>

**Exercise 3.** Remove `c.txt` interactively, then try to `rmdir` `input` and explain the error. Finally remove `output` safely.

<details>
<summary>Show a worked solution</summary>

```bash
rm -i ~/linux-lab/input/c.txt
rmdir ~/linux-lab/input
```

Output:

```text
rm: remove regular empty file '/home/learner/linux-lab/input/c.txt'? y
rmdir: failed to remove '/home/learner/linux-lab/input': Directory not empty
```

`rmdir` refuses because files remain; that refusal is the safety feature. `rmdir ~/linux-lab/output` succeeds because it is empty.
</details>

**Exercise 4.** Without running it, say exactly what this command does, and name one reason it is dangerous in a script:

```bash
rm -rf $workdir/tmp
```

<details>
<summary>Show a worked solution</summary>

It recursively and forcefully deletes the `tmp` subdirectory of whatever `$workdir` expands to. If `$workdir` is empty or unset, the path becomes `/tmp`, deleting the system temp directory; if it contains spaces and is unquoted, the command may delete several unintended paths. Quote it (`"$workdir/tmp"`), verify the variable, and consider `rm -ri` during testing.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You run `touch existing.txt` on a file full of important data. Did you just erase it?

<details>
<summary>Show answer</summary>

No. `touch` only updates the file's timestamps; the content is untouched. It creates a file only when the file does not already exist.
</details>

**Q2.** Why does `cp mydir /tmp/` fail when `mydir` is a directory, and what is the fix?

<details>
<summary>Show answer</summary>

`cp` refuses directories without `-r` ("omitting directory"). Use `cp -r mydir /tmp/`, or `cp -a` to also preserve attributes.
</details>

**Q3.** Is `rm -i` a real safety mechanism or just a comfort feature?

<details>
<summary>Show answer</summary>

A real one for interactive mistakes: it forces a per-file confirmation, which catches wrong paths, wrong directories, and over-broad wildcards before damage. It does nothing for you inside scripts, where the routine (verify `pwd`, narrow paths, quote variables) is the protection.
</details>

## Common mistakes
- Using `rmdir` on a non-empty directory and being surprised by the refusal.
- Forgetting `cp -r` for a directory.
- Running recursive `rm` from an unexpected working directory; `pwd` first.
- Assuming `touch` always creates a new file.
- Believing deleted files go somewhere recoverable; `rm` is final.

## Key takeaways
Inspect targets before changing them, quote variables, and treat recursive `rm` with the respect you would give a loaded tool. `rmdir` for empty directories, `rm -i` while learning, and `ls` after every operation.

## Further practice
Read `man cp`, `man mv`, and `man rm`. Pay attention to `-n` (no clobber) as the opposite of `-f`, and decide which default behavior you want in your own aliases later.

## References
- [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/)
