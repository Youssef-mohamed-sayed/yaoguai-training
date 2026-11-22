# Yaoguai Linux Essentials

A practical, beginner-first Linux course for learners preparing for Linux administration, CTFs, and cybersecurity work.

## Audience
Learners with basic computer literacy who want to become comfortable in a Linux terminal. No previous Linux experience is required.

## Prerequisites
- A computer capable of running a supported Linux distribution, a virtual machine, or WSL 2.
- Internet access for package installation and the OverTheWire section.
- Curiosity and willingness to practice commands rather than only read about them.

## Learning outcomes
By the end, you should be able to:
- Explain the Linux kernel, GNU/Linux, distributions, shells, and common environments.
- Navigate the filesystem and safely manage files, directories, links, and metadata.
- Read and change ownership and permissions, and use administrative privileges responsibly.
- Inspect processes, services, logs, and system resources.
- Build useful text-processing pipelines for administration and security analysis.
- Install and inspect software using the package manager appropriate to a distribution.
- Search for files and audit permissions without turning inspection into exploitation.
- Connect to remote hosts using SSH keys and transfer files securely.
- Write readable Bash scripts with input validation and basic error handling.
- Apply the skills in practical labs and OverTheWire: Bandit.

## Course map

| # | Module | Focus |
|---|---|---|
| 01 | [Introduction to Linux](01-introduction-to-linux/README.md) | Kernel, GNU/Linux, architecture, open source |
| 02 | [Distributions and Environments](02-distributions-and-environments/README.md) | Distros, desktop/CLI, shells, VMs, WSL |
| 03 | [Filesystem Hierarchy](03-filesystem-hierarchy/README.md) | FHS, paths, file types, links, inodes |
| 04 | [Command-Line Fundamentals](04-command-line-fundamentals/README.md) | Terminal, shell, navigation, efficiency |
| 05 | [Files and Directories](05-files-and-directories/README.md) | Create, copy, move, inspect, delete |
| 06 | [Users and Permissions](06-users-and-permissions/README.md) | Accounts, groups, modes, sudo, special bits |
| 07 | [Processes and Services](07-processes-and-services/README.md) | Processes, signals, systemd, logs |
| 08 | [Text Processing and Pipelines](08-text-processing-and-pipelines/README.md) | Streams, redirection, grep, sed, awk |
| 09 | [Package Management](09-package-management/README.md) | apt/dpkg, dnf/rpm, pacman |
| 10 | [Searching and Security Inspection](10-searching-and-security-inspection/README.md) | find, locate, permissions, audit basics |
| 11 | [SSH and Remote Access](11-ssh-and-remote-access/README.md) | SSH, keys, SCP, SFTP, host verification |
| 12 | [Bash Scripting](12-bash-scripting/README.md) | Variables, control flow, functions, safe scripts |
| 13 | [Linux Security and Privilege Basics](13-linux-security-basics/README.md) | Least privilege, SUID/SGID/sticky, defensive review |
| 14 | [Practical Labs](14-practical-labs/README.md) | Integrated administration and security exercises |
| 15 | [OverTheWire: Bandit](15-overthewire-bandit/README.md) | Progressive command-line wargame practice |

## Recommended learning order
Follow modules 01–15 in order. Complete each lesson's practice before moving on. Modules 06–13 build on filesystem and command-line fundamentals. The practical labs consolidate the skills before Bandit.

## Practice environments and tools
Recommended:
- Ubuntu LTS in a virtual machine, a spare machine, or WSL 2.
- A non-administrator user for everyday work.
- `man`, `info`, and `--help` for local documentation.
- `tree`, `htop`, `curl`, and `openssh-client` where not already installed.
- A snapshot before experimenting with system-level changes in a VM.

Commands and package names vary by distribution. Prefer the documentation for the distribution you are actually using. WSL is useful for command-line learning but does not behave exactly like a full Linux machine for every service, kernel, device, or boot task.

## How to use the course
1. Read the lesson and type each command yourself.
2. Predict output before running examples.
3. Complete exercises in a disposable practice directory.
4. Do not run destructive commands against important files or an unfamiliar system.
5. Record commands, observations, errors, and explanations in your own notes.
6. For security exercises, use only systems you own or have explicit permission to test.

## Using OverTheWire Bandit
Start with the [Bandit introduction](15-overthewire-bandit/01-bandit-introduction.md). The official game is authoritative for current level instructions and credentials. Credentials are intentionally not stored in this repository. The first connection details are published by OverTheWire; subsequent passwords are earned in the game and may change. Try independently before opening the hint and solution sections in each lesson.

## Course completion checklist
- [ ] Complete all module lessons and exercises.
- [ ] Complete the filesystem exploration and permissions labs.
- [ ] Build and test the six Bash scripts.
- [ ] Complete the remote SSH lab using key authentication.
- [ ] Analyze the supplied sample authentication log.
- [ ] Attempt Bandit levels using the official game pages.
- [ ] Review [COURSE-CHECKLIST.md](COURSE-CHECKLIST.md).

## References and documentation
- [Linux man-pages](https://man7.org/linux/man-pages/)
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [Ubuntu documentation](https://help.ubuntu.com/)
- [Debian documentation](https://www.debian.org/doc/)
- [Red Hat documentation](https://docs.redhat.com/)
- [Arch Wiki](https://wiki.archlinux.org/)
- [OverTheWire Bandit](https://overthewire.org/wargames/bandit/)
