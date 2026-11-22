# Desktop Environments, Shells, VMs, and WSL


## Learning objectives
- Distinguish a terminal emulator, shell, and desktop environment.
- Compare Bash with common alternative shells.
- Select a safe Linux practice environment.

## Core concepts
A **desktop environment** provides graphical panels, windows, settings, and applications. GNOME, KDE Plasma, and Xfce are examples. A **terminal emulator** displays a text session in a graphical window. A **shell** interprets commands inside that session.

Bash (Bourne Again Shell) is common on Linux. Other shells include `sh`, `zsh`, `fish`, and `dash`. Shell syntax differs: Bash arrays and `[[ ... ]]` are not POSIX `sh` features. Scripts should declare the interpreter they require.

A **virtual machine (VM)** runs a guest operating system using virtualized hardware. It is useful for snapshots and isolated labs. **WSL 2** runs a Linux environment integrated with Windows and uses a real Linux kernel in a lightweight VM architecture, but service management, devices, networking, and boot behavior can differ from a conventional Linux installation.

## Commands
```bash
printf 'Shell: %s
' "$SHELL"
ps -p "$$" -o pid=,comm=
echo "$0"
```
`$SHELL` usually describes the account's configured login shell; it may not identify the shell currently interpreting a nested script. `ps` inspects the current shell process.

```bash
bash --version
```

## Choosing an environment
- Use a VM for full-system administration, snapshots, systemd, and network labs.
- Use WSL for convenient command-line development and many Linux utilities.
- Use a dedicated lab VM for security tools and experiments.
- Do not expose vulnerable lab services to untrusted networks.

## Hands-on practice
- Run the commands above and identify your current shell.
- If available, open a Bash subshell using `bash`, then run `exit`.
- Compare `pwd` and `uname -a` between WSL and a Linux VM if you have both.

## Common mistakes
- Treating the terminal and shell as synonyms.
- Assuming every Bash script runs unchanged under `sh`.
- Assuming WSL has the same service and boot behavior as a physical Linux host.

## Key takeaways
The terminal is an interface; the shell interprets commands. VM and WSL environments are useful but have different system boundaries.

## Further practice
Read `man bash` and the official Microsoft WSL documentation.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
- [Microsoft WSL documentation](https://learn.microsoft.com/windows/wsl/)
- [GNOME](https://www.gnome.org/)
- [KDE Plasma](https://kde.org/plasma-desktop/)
