# Navigation and Shell Efficiency


## Learning objectives
- Navigate with `pwd`, `cd`, and `ls`.
- Use relative and absolute paths.
- Use history, completion, and directory shortcuts efficiently.

## Commands
```bash
pwd
ls
ls -lah
cd /etc
cd ..
cd ~
cd -
```
- `pwd`: print current directory.
- `ls -l`: long listing; `-a`: include hidden entries; `-h`: human-readable sizes; `-A`: include hidden entries except `.` and `..`.
- `cd`: change directory; `cd -` returns to the previous directory; `cd ~` goes home.

`tree` displays a directory hierarchy but may need installation:
```bash
tree -L 2 ~/linux-lab
```
`-L` limits depth. If unavailable, use `find`.

## Hands-on practice
- Starting in your home directory, navigate to `/etc` using an absolute path.
- Move to its parent using `cd ..`.
- Return home with `cd`.
- Use `cd -` twice and explain what changed.
- List hidden entries in your home directory.
- Hint: `pwd` confirms your location after every navigation step.

## Common mistakes
- Confusing `cd /tmp` with `cd tmp`.
- Forgetting that relative paths depend on the current directory.
- Assuming `ls` lists hidden files by default.

## Key takeaways
Use `pwd` to verify context, and prefer explicit paths when a command could affect important files.

## Further practice
Practice moving between `/`, `/etc`, `/var/log`, and your home directory without using a graphical file manager.

## References
- [Bash builtins: cd](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- [ls(1)](https://man7.org/linux/man-pages/man1/ls.1.html)
