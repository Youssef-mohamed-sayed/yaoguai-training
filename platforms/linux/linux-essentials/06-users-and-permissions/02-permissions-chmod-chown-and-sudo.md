# Permissions, chmod, chown, and sudo


## Learning objectives
- Interpret read, write, and execute permissions on files *and* directories, which mean different things.
- Use symbolic and octal modes fluently, in both directions.
- Change ownership and use sudo responsibly.

## The permission model
Every file and directory carries three permission sets, for three classes of identity:

- **user/owner (`u`):** the account that owns the file.
- **group (`g`):** accounts in the file's group.
- **other (`o`):** everyone else.

Each set has three bits, but their meaning depends on whether the object is a file or a directory:

| Bit | On a file | On a directory |
|---|---|---|
| `r` (4) | read the contents | list the names inside |
| `w` (2) | modify the contents | create, delete, rename entries (with `x`) |
| `x` (1) | run it as a program | traverse: enter it and reach its entries |

Read a real listing:

```text
-rwxr-xr-- 1 learner analysts 4096 Nov 25 04:20 deploy.sh
```

The leading `-` says regular file. Then three triples: owner `rwx` (read, write, execute), group `r-x` (read and execute, no write), other `r--` (read only). Owner is `learner`, group is `analysts`.

> [!IMPORTANT]
> Directory `x` is the most misunderstood bit in Linux. It means *traversal*: without it you cannot open files inside the directory even if you can list their names with `r`, and even if the files themselves are readable. When "the file is readable but access is denied", check the execute bit on every directory in the path.

### Octal modes
Each triple adds up: read 4, write 2, execute 1.

| Mode | Owner | Group | Other | Typical use |
|---|---|---|---|---|
| 755 | rwx | r-x | r-x | Programs and public directories |
| 644 | rw- | r-- | r-- | Ordinary readable files |
| 700 | rwx | --- | --- | Private directories (`~/.ssh`) |
| 600 | rw- | --- | --- | Private files (keys, secrets) |
| 640 | rw- | r-- | --- | Files a team may read but not change |

To go the other direction (symbols to octal), read each triple as a three-bit number: `r-x` = 4+0+1 = 5.

## Commands
```bash
chmod 640 report.txt        # octal: set exactly rw- r-- ---
chmod u+x script.sh         # symbolic: add execute for the owner
chmod go-rwx private.txt    # remove everything from group and other
chmod -R u+rwX ~/shared/    # recursive; capital X sets x only on directories and already-executable files
sudo chown alice:analysts report.txt
sudo chgrp analysts report.txt
```

`chmod` changes mode bits; symbolic form adjusts relative to the current mode (`+`, `-`, `=`), octal form replaces it entirely. `chown` changes owner and optionally group; `chgrp` changes only the group. Ownership changes almost always require root.

### sudo: borrowed privilege
`sudo command` runs one command with elevated privilege, as authorized by the sudoers policy (module 06 lesson 1), and logs the attempt. `sudo -iu username` starts a login shell as another user where policy permits; `su - username` does the same using *that account's* password.

Two disciplines:

- Run **one** privileged command, not a privileged session, whenever one command will do.
- `sudo` writes as root. Careless use (`sudo` on editors, package installs into home, redirected output with `>`) leaves **root-owned files inside a user's home directory**, which later breaks that user's own programs.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Create a file and a directory in `~/linux-lab`, set the file to `600` and the directory to `700`, and verify with `ls -ld` and `stat`.

<details>
<summary>Show a worked solution</summary>

```bash
mkdir -p ~/linux-lab/private
touch ~/linux-lab/private/secret.txt
chmod 600 ~/linux-lab/private/secret.txt
chmod 700 ~/linux-lab/private
ls -ld ~/linux-lab/private ~/linux-lab/private/secret.txt
```

Output:

```text
drwx------ 2 learner learner 4096 Nov 25 04:22 /home/learner/linux-lab/private
-rw------- 1 learner learner    0 Nov 25 04:22 /home/learner/linux-lab/private/secret.txt
```
</details>

**Exercise 2.** Write the octal mode for each requirement, then apply one of them: (a) owner read+write, group read, other nothing; (b) everyone reads and executes, only owner writes; (c) owner everything, nobody else anything.

<details>
<summary>Show a worked solution</summary>

(a) `640`, (b) `755`, (c) `700`. Apply (a):

```bash
touch ~/linux-lab/report.txt
chmod 640 ~/linux-lab/report.txt
ls -l ~/linux-lab/report.txt
```

Output: `-rw-r-----`.
</details>

**Exercise 3.** In a disposable VM, create a test user, give them a file, and make the file readable by a group they share, without making it world-readable.

<details>
<summary>Show a worked solution</summary>

```bash
sudo useradd -m -s /bin/bash labuser
sudo usermod -aG "$USER" labuser   # labuser joins your group, for the lab only
touch ~/linux-lab/team.txt
chmod 640 ~/linux-lab/team.txt     # group-readable, not world-readable
ls -l ~/linux-lab/team.txt
id labuser
```

The `640` mode plus shared group membership is the standard pattern for team-readable files. Remove the test account when done (`sudo userdel -r labuser`).
</details>

**Exercise 4.** A script at `~/linux-lab/run.sh` will not execute: you get "Permission denied" even though you own it. Diagnose and fix it.

<details>
<summary>Show a worked solution</summary>

```bash
ls -l ~/linux-lab/run.sh
```

The file almost certainly lacks the execute bit (`-rw-rw-r--`). Ownership alone does not make a file executable:

```bash
chmod u+x ~/linux-lab/run.sh
~/linux-lab/run.sh
```
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** A directory has mode `666` (everyone reads and writes). Can anyone `cd` into it or open its files?

<details>
<summary>Show answer</summary>

No. Without the execute/traverse bit on the directory, nobody can enter it or reach its contents, whatever the read and write bits say. This is why directories are normally `755`, `750`, or `700`.
</details>

**Q2.** Why is `chmod 777` almost never the right fix for an access error?

<details>
<summary>Show answer</summary>

It grants every account on the system full read, write, and execute access, replacing a solvable permission question (who *should* reach this?) with "everyone can do anything". The right fix names the correct owner, group, and minimal mode.
</details>

**Q3.** Convert `-rwxr-x---` to octal, and `654` to symbols.

<details>
<summary>Show answer</summary>

`rwx`=7, `r-x`=5, `---`=0, so `750`. And `654` is `rw-`, `r-x`, `r--`, written `-rw-r-xr--`.
</details>

## Common mistakes
- Thinking execute on a directory means "run it"; it means traversal.
- Reaching for `777` to silence an access error.
- Forgetting directory execute permission when troubleshooting file access.
- Using `sudo` for everything and littering home directories with root-owned files.
- Changing ownership recursively with `chown -R` before checking what the tree contains.

## Key takeaways
Permissions are an access-control boundary with three classes and three bits whose meaning flips between files and directories. Apply the narrowest mode that supports the task, and let sudo elevate one command at a time.

## Further practice
Read `man chmod`, `man chown`, and `man sudo`, then audit your own home directory: `ls -la ~` and explain every mode you see.

## References
- [chmod(1)](https://man7.org/linux/man-pages/man1/chmod.1.html)
- [GNU Coreutils: chown](https://www.gnu.org/software/coreutils/manual/html_node/chown-invocation.html)
- [sudo(8)](https://man7.org/linux/man-pages/man8/sudo.8.html)
