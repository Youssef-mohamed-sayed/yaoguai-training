# Linux Architecture and Open Source


## Learning objectives
- Recognize kernel, user-space, libraries, services, and applications.
- Understand privileged and unprivileged execution at a high level.
- Relate open-source development to security maintenance.

## Introduction
Understanding the layers of a Linux system helps troubleshoot problems. If a network interface is missing, for example, the cause may be a kernel driver, firmware, network service, configuration file, or application—not necessarily the terminal command you typed.

## Core concepts
- **Hardware:** physical or virtual CPU, memory, storage, and peripherals.
- **Kernel space:** privileged code with direct resource-management responsibilities.
- **User space:** ordinary programs, including shells and services.
- **System call:** a controlled entry point through which a process requests a kernel operation.
- **Daemon/service:** a background program that provides a function such as logging or networking.
- **Library:** reusable code used by programs.

A process normally has its own virtual address space. The kernel enforces boundaries between processes and controls access to resources. Root privileges grant broad administrative authority but do not make every operation safe.

Open-source projects commonly publish source, issue trackers, release notes, and security advisories. A responsible administrator tracks supported releases and applies updates through trusted repositories.

## Commands and practical examples
```bash
uname -r
lscpu
free -h
lsblk
```
These commands inspect the kernel release, CPU, memory, and block devices. Some may be absent in minimal environments; install their package using your distribution's package manager.

```bash
systemctl --version
```
This reports the systemd version when systemd is installed. WSL containers and non-systemd distributions may use a different init/service arrangement.

## Hands-on practice
- Run `lscpu`, `free -h`, and `lsblk` where available.
- Identify which output describes hardware and which describes kernel or service software.
- In a VM, compare output before and after changing its allocated RAM (shut the VM down before changing hardware settings).

## Common mistakes
- Assuming all Linux systems use systemd.
- Assuming a command exists on every minimal installation.
- Treating root as a normal account for daily browsing and development.

## Key takeaways
Linux is layered. Troubleshooting is easier when you identify which layer owns the behavior.

## Further practice
Continue to distributions and environments, then revisit this lesson when studying services and devices.

## References
- [Linux kernel documentation](https://docs.kernel.org/)
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
