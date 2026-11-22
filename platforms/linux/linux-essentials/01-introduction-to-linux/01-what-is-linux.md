# What Is Linux?


## Learning objectives
- Define Linux and distinguish the kernel from a complete operating system.
- Explain the roles of user space, the kernel, and system utilities.
- Describe GNU/Linux and the open-source model.

## Introduction
Linux is a family of operating systems built around the Linux kernel. It powers servers, cloud infrastructure, phones (through Android's kernel lineage), embedded devices, developer workstations, and security tools. Its command line is especially useful because it makes system behavior inspectable and automatable.

## Core concepts

### Kernel and operating system
The **kernel** is the privileged core that manages CPU scheduling, memory, devices, filesystems, networking, and system calls. Applications normally run in **user space** and request kernel services through system calls.

A usable Linux system also needs user-space components: a C library, command-line utilities, service manager, package manager, libraries, applications, and often a graphical environment. A **distribution** integrates and maintains these components.

### GNU/Linux
GNU is a long-running free-software project that provides many foundational user-space tools, including shells and core utilities. Many general-purpose systems combine the Linux kernel with GNU tools, so **GNU/Linux** is a technically descriptive name. Not every Linux-based system uses the same GNU components.

### High-level architecture
1. Hardware provides CPU, memory, storage, and network devices.
2. The kernel manages resources and exposes system calls.
3. System services provide background functionality.
4. Libraries and command-line tools offer reusable interfaces.
5. User applications provide interactive or automated workflows.

### Open source
Open-source software makes source code available under licenses that grant defined rights to use, inspect, modify, and redistribute it. Open source does not mean that every program is secure, free of charge, or free of bugs. Security still depends on design, maintenance, configuration, and timely updates.

## Commands and practical examples
```bash
uname -a       # kernel and machine information
uname -r       # kernel release
cat /etc/os-release
```
`uname` reports kernel and hardware-related information. `/etc/os-release` is a common, distribution-provided identification file. Its exact values differ by system.

```text
NAME="Ubuntu"
VERSION="24.04 LTS ..."
ID=ubuntu
```
Treat this as representative output, not a required version.

## Hands-on practice
1. **Objective:** Identify your Linux environment.
   - Initial conditions: Open a Linux terminal or WSL shell.
   - Run `uname -a` and `cat /etc/os-release`.
   - Expected result: You can state the kernel release and distribution name.
   - Hint: The kernel name and distribution name are different fields.
2. Explain in your own words why the kernel alone is not the complete desktop operating system.

## Common mistakes
- Calling every Linux distribution simply “the Linux kernel.” A distribution includes much more.
- Assuming open source guarantees security. Review maintenance activity and configuration.
- Confusing the kernel version with the distribution release.

## Key takeaways
- Linux is the kernel; a distribution packages it with user-space software.
- The kernel manages hardware resources and provides system interfaces.
- Open source enables inspection and collaboration, not automatic correctness.

## Further practice
Read `man uname`, inspect `/etc/os-release`, and continue to the distribution comparison lesson.

## References
- [Linux kernel documentation](https://docs.kernel.org/)
- [GNU Project](https://www.gnu.org/)
- [Linux man-pages: uname(1)](https://man7.org/linux/man-pages/man1/uname.1.html)
