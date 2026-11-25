# What Is Linux?


## Learning objectives
- Define Linux and distinguish the kernel from a complete operating system.
- Explain the roles of user space, the kernel, and system utilities.
- Describe GNU/Linux and the open-source model, including what open source does and does not guarantee.

## Introduction
Linux is a family of operating systems built around the Linux kernel. It runs most of the world's servers, the majority of cloud infrastructure, every Android phone (through its kernel lineage), network equipment, embedded devices, developer workstations, and nearly every serious security tool. If you plan to work in system administration, DevOps, or cybersecurity, Linux is not one option among many; it is the default environment you will operate in.

Its command line is especially worth learning because it makes system behavior **inspectable** (you can ask the system exactly what it is doing) and **automatable** (anything you can type, you can script and repeat a thousand times).

## Core concepts

### Kernel and operating system
The **kernel** is the privileged core of the system. It manages CPU scheduling, memory, devices and their drivers, filesystems, networking, and the system calls through which programs request services. When people say "Linux" precisely, they often mean this kernel alone.

Applications normally run in **user space**, a protected mode where they cannot touch hardware or each other's memory directly. When a program wants to read a file, open a network connection, or start another program, it asks the kernel through a **system call**, and the kernel decides whether to allow it.

A usable operating system needs much more than a kernel: a C library, command-line utilities, an init and service manager, a package manager, libraries, applications, and often a graphical environment. A **distribution** integrates all of these around the kernel and maintains them as a coherent whole. Ubuntu, Debian, Fedora, and Arch are distributions; "Linux" underneath each of them is the same kernel project.

### GNU/Linux
GNU is a long-running free-software project that provides many foundational user-space tools, including the Bash shell and the core utilities (`ls`, `cp`, `grep`, and friends). Many general-purpose systems combine the Linux kernel with GNU tools, so **GNU/Linux** is a technically descriptive name for those systems. Not every Linux-based system uses GNU components: Android and Alpine Linux, for example, do not.

### High-level architecture
From the metal up:

1. **Hardware** provides CPU, memory, storage, and network devices.
2. The **kernel** manages those resources and exposes system calls.
3. **System services** (daemons) provide background functionality like logging, networking, and scheduling.
4. **Libraries and command-line tools** offer reusable interfaces for programs and people.
5. **User applications** provide interactive or automated workflows.

Keep this stack in mind. When something breaks, your first diagnostic question is always "which layer owns this behavior?"

### Open source
Open-source software publishes its source code under licenses that grant defined rights to use, inspect, modify, and redistribute it. Practically, this means you can read exactly what your system does, fix it, and share the fix.

Open source does **not** mean that every program is secure, free of charge, or free of bugs. Security still depends on design, maintenance, configuration, and timely updates. A famous component can have a famous vulnerability; the open-source advantage is that the problem can be found, disclosed, and patched in public, and that you can verify the fix yourself.

## Commands and practical examples
Two commands identify almost any Linux system:

```bash
uname -a       # kernel name, release, machine architecture, and more
uname -r       # kernel release only
cat /etc/os-release
```

Sample output (yours will differ):

```text
$ uname -r
6.8.0-45-generic

$ cat /etc/os-release
NAME="Ubuntu"
VERSION="24.04 LTS (Noble Numbat)"
ID=ubuntu
VERSION_ID="24.04"
```

Notice the two different answers: `uname` describes the **kernel**, while `/etc/os-release` describes the **distribution**. A system running kernel 6.8 can be Ubuntu, Debian, Fedora, or a container image; the kernel release alone does not tell you. Treat all version numbers in this course as representative examples, not values your system must match.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Identify your environment: print your kernel release, your machine architecture, and your distribution's name and version, using the commands from this lesson.

<details>
<summary>Show a worked solution</summary>

```bash
uname -r
uname -m
grep -E '^(NAME|VERSION)=' /etc/os-release
```

Typical output:

```text
6.8.0-45-generic
x86_64
NAME="Ubuntu"
VERSION="24.04 LTS (Noble Numbat)"
```

`uname -m` prints the machine architecture (`x86_64`, `aarch64`, ...). Filtering `/etc/os-release` with `grep` keeps the output to the two fields you need; you will learn `grep` properly in module 08.
</details>

**Exercise 2.** Open the manual page for `uname` and find the option that prints *only* the operating system name. Run it.

<details>
<summary>Show a worked solution</summary>

Run `man uname`, search for "operating system" with `/`, and you will find `-o, --operating-system`:

```bash
uname -o
```

Output:

```text
GNU/Linux
```

Even `uname` acknowledges the GNU user space.
</details>

**Exercise 3.** In one or two sentences each, say which layer of the architecture stack owns this behavior: (a) a program cannot open another user's file, (b) your Wi-Fi card is not detected, (c) `ls` prints a directory listing.

<details>
<summary>Show a worked solution</summary>

(a) The kernel enforces file permissions when the program's system call requests the open. (b) The kernel, specifically a missing or broken device driver or firmware. (c) A user-space utility (`ls` from GNU coreutils) making system calls the kernel answers.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** A friend says "I installed Linux 24.04." What is imprecise about that sentence?

<details>
<summary>Show answer</summary>

24.04 is a *distribution* release (Ubuntu 24.04), not a Linux kernel version. The kernel on that system has its own version, shown by `uname -r`.
</details>

**Q2.** Why can a normal program not read directly from the disk hardware, and what does it do instead?

<details>
<summary>Show answer</summary>

Programs run in user space without direct hardware access. They request the operation through a system call, and the kernel performs it (or refuses it) on their behalf.
</details>

**Q3.** Does "open source" mean "secure"? Explain in one sentence.

<details>
<summary>Show answer</summary>

No. Open source means the code can be inspected and modified under its license; security still depends on design, maintenance, configuration, and updates.
</details>

## Common mistakes
- Calling every distribution simply "the Linux kernel." A distribution is the kernel plus an entire user space and support model.
- Assuming open source guarantees security. Review maintenance activity and configuration instead.
- Confusing the kernel version (`uname -r`) with the distribution release (`/etc/os-release`).
- Believing Linux is only for servers: it is also phones, routers, cars, and the machine you may be reading this on.

## Key takeaways
- Linux is the kernel; a distribution packages it with user-space software.
- The kernel manages hardware resources and provides system calls; everything else asks it for services.
- Open source enables inspection and collaboration, not automatic correctness.

## Further practice
Read `man uname`, inspect `/etc/os-release` on every Linux system you can reach (a VM, WSL, a cloud free tier), and notice how the answers differ. Then continue to the architecture lesson.

## References
- [Linux kernel documentation](https://docs.kernel.org/)
- [GNU Project](https://www.gnu.org/)
- [Linux man-pages: uname(1)](https://man7.org/linux/man-pages/man1/uname.1.html)
