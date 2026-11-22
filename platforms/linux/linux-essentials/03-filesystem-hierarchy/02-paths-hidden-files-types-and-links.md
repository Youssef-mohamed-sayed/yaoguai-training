# Paths, Hidden Files, File Types, and Links


## Learning objectives
- Recognize hidden files and common file types.
- Explain extensions, inodes, hard links, and symbolic links.
- Inspect file metadata safely.

## Core concepts
A filename beginning with `.` is hidden by convention; it is not encrypted or protected. Examples include `.bashrc` and `.ssh/`. Linux does not require extensions: a file named `report` may contain text, while a `.jpg` file may not actually be an image.

The filesystem stores metadata in an **inode**: ownership, permissions, timestamps, and pointers to file data (implementation details vary). A directory maps names to inode numbers.

A **hard link** is another directory entry referring to the same inode. It generally cannot cross filesystem boundaries and normally cannot be made to directories by ordinary users. A **symbolic link** is a special file containing a path to another object; it can cross filesystems and can become dangling if its target moves.

## Commands
```bash
ls -la
file /etc/passwd
stat /etc/passwd
ln report.txt report-hardlink.txt
ln -s report.txt report-symlink.txt
ls -li report*
```
`ls -i` displays inode numbers. `stat` shows detailed metadata. `file` identifies content using signatures and heuristics rather than trusting the extension.

Create a safe demonstration:
```bash
mkdir -p ~/linux-lab/links
cd ~/linux-lab/links
printf 'sample
' > original.txt
ln original.txt hard.txt
ln -s original.txt symbolic.txt
stat original.txt hard.txt symbolic.txt
```
The original and hard link share an inode; the symlink has its own inode and points to the target.

## Hands-on practice
- Create one hidden file and one extensionless text file.
- Use `ls -la`, `file`, `stat`, and `ls -li` to inspect them.
- Create a hard link and a symbolic link; rename the original and observe which link still resolves.
- Hint: a symlink stores a path, while a hard link names the same inode.

## Common mistakes
- Assuming hidden means secure.
- Assuming extensions determine file type.
- Deleting a symlink's target when intending to remove only the link. `rm linkname` removes the link itself, not the target.

## Key takeaways
Names, extensions, file types, and inodes are different concepts. Hard links share an inode; symbolic links point by path.

## Further practice
Read `man ln`, `man stat`, and `man inode`.

## References
- [GNU Coreutils: ln](https://www.gnu.org/software/coreutils/manual/html_node/ln-invocation.html)
- [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html)
