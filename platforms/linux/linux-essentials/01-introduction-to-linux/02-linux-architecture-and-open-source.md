# Linux Architecture and Open Source


## Learning objectives
- Recognize the kernel, user space, libraries, services, and applications as separate layers.
- Understand privileged and unprivileged execution at a high level.
- Relate open-source development practices to real security maintenance.

## Introduction
Understanding the layers of a Linux system turns troubleshooting from guessing into reasoning. If a network interface is missing, the cause may be a kernel driver, missing firmware, a stopped network service, a configuration file, or the application itself, and each possibility belongs to a different layer with different tools. This lesson gives you the map; later modules give you the tools for each layer.

## Core concepts
- **Hardware:** physical or virtual CPU, memory, storage, and peripherals.
- **Kernel space:** privileged code with direct resource-management responsibilities. A bug here can crash the whole machine.
- **User space:** ordinary programs, including your shell and system services. A bug here crashes one process; the kernel cleans up.
- **System call:** a controlled entry point through which a process requests a kernel operation: open a file, map memory, send a packet, create a process.
- **Daemon/service:** a background program that provides a function such as logging (`rsyslog`, `systemd-journald`), name resolution, or remote access (`sshd`).
- **Library:** reusable code linked into programs. The C library (`glibc` on most systems) sits under nearly everything, wrapping raw system calls in functions programs actually use.

A process normally has its own virtual address space. The kernel enforces boundaries between processes and controls access to resources, so one user's program cannot read another's memory or files without permission. The **root** account is the exception: it bypasses most of these checks, which is exactly why daily work should happen in a normal account. Root privileges grant broad administrative authority but do not make any operation safe; one mistaken command as root can destroy the whole system, while the same command as a normal user can only destroy what that user owns.

### Open source as a maintenance model
Open-source projects commonly publish their source, issue trackers, release notes, and security advisories. A responsible administrator tracks supported releases and applies updates through the distribution's trusted repositories, which are signed and verified by the package manager (module 09). The practical loop looks like this:

1. A vulnerability is reported and assigned an identifier (a CVE).
2. The project fixes it and the distribution backports the fix to its supported releases.
3. Your package manager offers the patched version as an ordinary update.
4. You apply it, and your system is protected without changing how you work.

This is why "is this project actively maintained?" is a security question, not just a preference.

## Commands and practical examples
These commands inspect different layers. Some may be absent in minimal environments; install them with your distribution's package manager.

```bash
uname -r        # kernel release
lscpu           # CPU architecture and topology
free -h         # memory, human-readable
lsblk           # block devices (disks and partitions)
```

Sample output:

```text
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.7Gi       1.2Gi       5.4Gi        45Mi       1.1Gi       6.3Gi
Swap:          2.0Gi          0B       2.0Gi
```

```bash
systemctl --version
```

This reports the systemd version when systemd is installed as the init system and service manager. It is common (Ubuntu, Debian, Fedora, RHEL, Arch) but not universal: WSL sessions and some container or minimal environments use different arrangements, and you will see `systemctl` fail there even though the system is perfectly healthy. In module 07 you will use `systemctl` to manage services.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Run `lscpu`, `free -h`, and `lsblk`. For each one, write down whether it describes hardware, the kernel, or user-space software.

<details>
<summary>Show a worked solution</summary>

`lscpu` and `lsblk` describe **hardware** (CPU and disks) as the kernel sees them. `free -h` reports **kernel** memory accounting. All three commands are themselves **user-space** programs reading kernel interfaces, mostly virtual files under `/proc` and `/sys`.
</details>

**Exercise 2.** Peek at the kernel's own view of your machine: print the contents of `/proc/version` and the first five lines of `/proc/cpuinfo`.

<details>
<summary>Show a worked solution</summary>

```bash
cat /proc/version
head -n 5 /proc/cpuinfo
```

Typical output:

```text
Linux version 6.8.0-45-generic (buildd@...) ...
processor	: 0
vendor_id	: GenuineIntel
...
```

`/proc` is a virtual filesystem the kernel maintains: the "files" do not exist on disk; the kernel generates their contents on read. It is one of the cleanest demonstrations of the kernel/user-space boundary.
</details>

**Exercise 3.** Check whether your system uses systemd, and if it does, list how many services are currently running.

<details>
<summary>Show a worked solution</summary>

```bash
systemctl --version
systemctl list-units --type=service --state=running | head
```

If the first command prints a version, systemd is present; the second lists running services with a count at the bottom. If `systemctl` is missing or errors (common in WSL and containers), your environment uses a different init arrangement and module 07 will note the differences.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Your browser crashes. Why does the whole system usually survive?

<details>
<summary>Show answer</summary>

The browser runs as an unprivileged user-space process. The kernel isolates it, so when it dies the kernel reclaims its memory and keeps everything else running.
</details>

**Q2.** Why is doing daily work as root dangerous even if you "know what you are doing"?

<details>
<summary>Show answer</summary>

Root bypasses the permission checks that limit mistakes. One wrong command (a typo in an `rm` path, a redirected write over a system file) can damage the entire system; as a normal user the same typo can only touch files you own.
</details>

**Q3.** Your distribution offers an update described as a security fix for a library. Nothing on your desktop looks broken. Should you apply it, and why?

<details>
<summary>Show answer</summary>

Yes. Security fixes patch vulnerabilities that are not visible in normal use. Applying signed repository updates promptly is the core maintenance habit of a secure system.
</details>

## Common mistakes
- Assuming all Linux systems use systemd.
- Assuming a command exists on every minimal installation; check and install instead.
- Treating root as a normal account for daily browsing and development.
- Ignoring updates because "everything works", which is precisely when known vulnerabilities stay open.

## Key takeaways
Linux is layered: hardware, kernel, services, libraries, applications. Troubleshooting is easier, and safer, when you first identify which layer owns the behavior. Root is a tool for administration, not a lifestyle.

## Further practice
Continue to distributions and environments, then revisit this lesson when you study services (module 07) and permissions (module 06); the layers will keep reappearing.

## References
- [Linux kernel documentation](https://docs.kernel.org/)
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
- [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
