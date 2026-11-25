# Paths, Hidden Files, File Types, and Links


## Learning objectives
- Recognize hidden files and common file types, and explain what extensions do and do not mean.
- Explain inodes, hard links, and symbolic links well enough to predict their behavior.
- Inspect file metadata safely with `ls`, `file`, and `stat`.

## Core concepts

### Hidden files
A filename beginning with `.` is hidden **by convention**: `ls` and graphical file managers simply do not show it unless asked (`ls -a`). Hidden does not mean encrypted, protected, or secure. Anyone with read permission can see a hidden file with `ls -a`. Your home directory is full of them because they hold configuration: `.bashrc`, `.profile`, `.ssh/`, `.gitconfig`.

> [!WARNING]
> Never treat a dotfile as a secret store. `.ssh/` contains private keys, but they are protected by *permissions* (module 06), not by the dot in the name.

### Extensions and real file types
Linux does not require extensions, and the kernel does not care about them. A file named `report` may be plain text, and a file named `photo.jpg` may be a script. Extensions are hints for humans and for some applications, nothing more. To learn what a file actually contains, ask the filesystem to inspect its content:

```bash
file /etc/passwd
file photo.jpg
```

Sample output:

```text
/etc/passwd: ASCII text
photo.jpg:   JPEG image data, JFIF standard 1.01
```

`file` reads the first bytes and matches them against a database of signatures ("magic numbers"), so it reports the real type regardless of the name.

### Inodes
The filesystem stores a file's metadata in an **inode**: ownership, permissions, timestamps, size, and pointers to the actual data blocks. The inode does *not* store the filename. A directory is a table mapping **names to inode numbers**, which is why one file's data can have several names, and why a name can point at nothing.

See the inode numbers directly:

```bash
ls -li report.txt
stat report.txt
```

`ls -i` adds the inode column; `stat` prints the full metadata record: size, permissions, owner, inode number, link count, and the three timestamps (access, modify, change).

### Hard links and symbolic links
A **hard link** is a second directory entry that names the *same inode*. The two names are equal citizens: neither is "the original". The data survives until the last name is removed. Hard links generally cannot cross filesystem boundaries, and ordinary users cannot make them to directories.

A **symbolic link** (symlink) is a small special file that *contains a path* to another object. It can cross filesystems and point to directories, but it is only a pointer: if the target moves or is deleted, the symlink dangles and breaks.

Create a safe demonstration and watch the difference:

```bash
mkdir -p ~/linux-lab/links && cd ~/linux-lab/links
printf 'sample\n' > original.txt
ln original.txt hard.txt
ln -s original.txt symbolic.txt
ls -li
```

Sample output (inode numbers will differ):

```text
1049090 -rw-rw-r-- 2 learner learner 7 Nov 25 04:15 hard.txt
1049090 -rw-rw-r-- 2 learner learner 7 Nov 25 04:15 original.txt
1049091 lrwxrwxrwx 1 learner learner 12 Nov 25 04:15 symbolic.txt -> original.txt
```

`hard.txt` and `original.txt` share inode `1049090`, and the link count is `2`. The symlink has its own inode and a type letter `l`, with its target shown after `->`. Now rename the original:

```bash
mv original.txt renamed.txt
cat hard.txt        # works: same inode
cat symbolic.txt    # fails: points at the old path
```

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Create one hidden file and one extensionless text file in `~/linux-lab/links`, then use `ls -la`, `file`, and `stat` to inspect both.

<details>
<summary>Show a worked solution</summary>

```bash
cd ~/linux-lab/links
printf 'secret-ish\n' > .notes
printf 'plain text\n' > report
ls -la
file .notes report
stat report
```

`ls -la` reveals `.notes`; plain `ls` does not. `file` reports both as ASCII text despite the missing extension.
</details>

**Exercise 2.** Create a hard link and a symlink to the same file, then delete the original name. Which link still shows the content, and what does `ls -l` tell you about the other?

<details>
<summary>Show a worked solution</summary>

```bash
cd ~/linux-lab/links
printf 'data\n' > base.txt
ln base.txt base-hard.txt
ln -s base.txt base-sym.txt
rm base.txt
cat base-hard.txt   # still works
cat base-sym.txt    # No such file or directory
ls -l base-sym.txt
```

The hard link keeps the inode (and its data) alive. The symlink now dangles; many `ls` configurations highlight broken symlinks in a warning color.
</details>

**Exercise 3.** A download is named `setup.bin` but you suspect it is actually a shell script. Identify it without executing it, then read the first lines safely.

<details>
<summary>Show a worked solution</summary>

```bash
file setup.bin
head -n 5 setup.bin
```

`file` will say something like `Bourne-Again shell script, ASCII text executable` if it is a script. `head` shows the shebang line (`#!/bin/bash`) without running anything. Never execute an unidentified file to "see what it does".
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Is a file named `.secret` protected from other users? Why or why not?

<details>
<summary>Show answer</summary>

No. The leading dot only hides it from default listings. Anyone with read permission on the file (and search permission on its directory) can read it with `ls -a` and `cat`. Protection comes from permissions, not names.
</details>

**Q2.** You rename `original.txt` to `renamed.txt`. What happens to a hard link and to a symlink that both pointed at `original.txt`?

<details>
<summary>Show answer</summary>

The hard link still works: it names the inode, which never changed. The symlink breaks: it stores the old path, which no longer exists.
</details>

**Q3.** What does the link count in `ls -l` (the number after the permissions) mean for a regular file?

<details>
<summary>Show answer</summary>

The number of directory entries (names) pointing to that inode. A plain file starts at 1; each hard link adds one. The data is freed only when the count reaches 0 and no process holds the file open.
</details>

## Common mistakes
- Assuming hidden means secure.
- Assuming the extension determines the type; check with `file` instead.
- Confusing link removal semantics: `rm linkname` removes the link itself, not its target, but careless use of tab completion or wildcards around symlinks to directories can still bite.
- Believing a symlink protects data when the target is deleted; the symlink survives, the data does not.

## Key takeaways
Names, extensions, file types, and inodes are four different concepts. A hard link is another name for the same inode; a symlink is a path in a file. `file` and `stat` tell you the truth about both.

## Further practice
Read `man ln`, `man stat`, and `man inode`, then hunt for real symlinks on your system: `ls -l /bin /usr/bin | head` on a merged-usr system shows `/bin` itself as a symlink.

## References
- [GNU Coreutils: ln](https://www.gnu.org/software/coreutils/manual/html_node/ln-invocation.html)
- [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7)](https://man7.org/linux/man-pages/man7/symlink.7.html)
