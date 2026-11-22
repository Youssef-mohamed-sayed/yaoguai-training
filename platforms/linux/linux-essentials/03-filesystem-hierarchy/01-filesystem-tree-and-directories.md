# The Filesystem Tree and Important Directories


## Learning objectives
- Navigate the Linux directory tree from `/`.
- Explain the purpose of major system directories.
- Distinguish absolute and relative paths.

## Introduction
Linux presents filesystems through one directory tree. The top of that tree is `/`, called the root directory. Separate disks and partitions are mounted at directories within this tree.

## Important directories

| Path | Purpose |
|---|---|
| `/` | Root of the directory tree |
| `/home` | Regular users' home directories |
| `/root` | Root account's home directory |
| `/etc` | Host-specific system configuration |
| `/var` | Variable data such as logs, queues, caches |
| `/tmp` | Temporary files; cleanup policy varies |
| `/usr` | Most user-space programs, libraries, and shared data |
| `/bin`, `/sbin` | Essential commands; often symlinks into `/usr` on merged-usr systems |
| `/opt` | Optional/add-on application software |
| `/dev` | Device interfaces |
| `/proc` | Virtual process and kernel information |
| `/sys` | Kernel device and subsystem information |
| `/boot` | Bootloader and kernel-related files |
| `/mnt` | Conventional temporary mount point |
| `/media` | Common mount location for removable media |

`/proc` and `/sys` are virtual filesystems; their entries represent kernel-maintained information rather than ordinary stored files. Do not edit them casually.

### Paths
- Absolute path starts at `/`, e.g. `/etc/ssh/sshd_config`.
- Relative path starts from the current working directory, e.g. `notes/todo.txt`.
- `.` means current directory; `..` means parent directory; `~` expands to the current user's home directory in common shells.

### Configuration and logs
Common locations include `/etc/` for configuration, `/var/log/` for many logs, and service-specific directories under `/var/lib/`. Exact files depend on distribution and service. Use `journalctl` for systemd journal logs where applicable.

## Commands
```bash
pwd
ls /
ls -la /etc
ls -ld /var/log
cd /var/log
pwd
```
`ls -a` includes hidden entries; `-l` uses a detailed listing; `-d` lists the directory itself rather than its contents.

## Hands-on practice: filesystem exploration
- Objective: document the purpose of ten top-level directories.
- Initial conditions: a Linux shell with read access to `/`.
- Run `ls -la /`, `ls -ld /etc /var /home /proc /sys`, and `find /etc -maxdepth 1 -type f | head`.
- Expected result: a short table of directory names and their purposes, plus examples of configuration files.
- Hint: use `man hier` if installed; the FHS reference is also useful.

## Common mistakes
- Confusing `/` with `/root`.
- Assuming every machine has the same contents under `/home`.
- Trying to treat `/proc` like persistent disk storage.

## Key takeaways
The filesystem is one tree. Learn the purpose of common directories before changing system files.

## Further practice
Inspect `/etc/os-release`, `/etc/hostname`, and `/var/log` without modifying them.

## References
- [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [hier(7)](https://man7.org/linux/man-pages/man7/hier.7.html)
