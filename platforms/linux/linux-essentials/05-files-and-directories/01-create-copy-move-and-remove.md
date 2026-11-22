# Create, Copy, Move, and Remove Files


## Learning objectives
- Create files and directories.
- Copy and move files safely.
- Explain the risks of recursive deletion.

## Commands
```bash
mkdir -p ~/linux-lab/{input,backup}
touch ~/linux-lab/input/notes.txt
cp ~/linux-lab/input/notes.txt ~/linux-lab/backup/
mv ~/linux-lab/backup/notes.txt ~/linux-lab/backup/notes-old.txt
rmdir ~/linux-lab/empty-dir
```
- `mkdir -p`: create parent directories as needed; do not fail if the target already exists.
- `touch`: create an empty file if absent or update timestamps if present.
- `cp`: copy; `-r` recursively copies directories; `-i` prompts before overwrite; `-a` preserves attributes as far as possible.
- `mv`: move or rename; `-i` prompts before overwrite.
- `rmdir`: removes empty directories only.
- `rm`: removes files; `-r` recursively removes directory trees; `-f` suppresses prompts/errors for missing files.

### Safe deletion
Before deleting:
1. Print the current directory with `pwd`.
2. Inspect the exact target with `ls -la -- target`.
3. Prefer a narrow path and interactive mode (`rm -i`) while learning.
4. Avoid `rm -rf` with variables, wildcards, or paths you have not verified.
5. Never copy a command containing `sudo rm -rf` from an untrusted source.

Example:
```bash
rm -i ~/linux-lab/input/old.txt
```
Do not test destructive commands on real data.

## Inspecting files
```bash
file ~/linux-lab/input/notes.txt
stat ~/linux-lab/input/notes.txt
cat ~/linux-lab/input/notes.txt
less /var/log/dpkg.log
head -n 5 /etc/passwd
tail -n 20 /var/log/syslog
```
`less` is interactive; press `q` to quit. Some log paths vary by distribution. `tail -f` follows new lines as a log grows.

## Hands-on practice
- Create `~/linux-lab/{input,output}`.
- Create three files, copy one, rename one, and remove one interactively.
- Use `file` and `stat` on each remaining file.
- Expected result: a directory tree you can explain.
- Hint: `find ~/linux-lab -maxdepth 2 -type f -print`.

## Common mistakes
- Using `rmdir` on a non-empty directory.
- Forgetting `cp -r` for a directory.
- Running `rm -rf` from an unexpected working directory.
- Assuming `touch` always creates a new file; it updates an existing file's timestamp.

## Key takeaways
Inspect targets before changing them. `rmdir` is safer for empty directories; recursive `rm` deserves extra caution.

## Further practice
Read `man cp`, `man mv`, and `man rm`.

## References
- [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/)
