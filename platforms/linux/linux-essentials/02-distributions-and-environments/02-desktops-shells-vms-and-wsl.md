# Desktop Environments, Shells, VMs, and WSL


## Learning objectives
- Distinguish a terminal emulator, a shell, and a desktop environment.
- Compare Bash with common alternative shells, and know when the differences bite.
- Select a safe Linux practice environment for each kind of work.

## Core concepts
Three things people casually call "the terminal":

- A **desktop environment** provides the graphical layer: panels, windows, settings, and applications. GNOME, KDE Plasma, and Xfce are the common ones. Two machines running the same distribution can look completely different because they run different desktop environments.
- A **terminal emulator** is one application inside that desktop: it draws a text session in a window and passes your keystrokes along. GNOME Terminal, Konsole, and Alacritty are emulators.
- A **shell** is the program inside the session that interprets your commands. This is where Bash lives.

The desktop environment is interchangeable decoration. The shell is where your skills transfer (or fail to).

### Bash and the other shells
Bash (Bourne Again Shell) is the default interactive shell on most Linux distributions. Others you will meet:

- `sh`: the POSIX standard name. On Debian/Ubuntu it is `dash`, a small, fast, strictly limited shell.
- `zsh`: highly customizable, the default on macOS for years.
- `fish`: friendly interactive defaults, but deliberately non-POSIX syntax.

Syntax differs between them. Bash arrays, `[[ ... ]]`, and `==` inside tests are **not** POSIX `sh` features. This has a practical consequence: a script that works when you paste it into your Bash prompt can fail when run as `sh script.sh`, because `sh` may be a different, stricter program. Scripts must declare their interpreter with a shebang (`#!/usr/bin/env bash`, covered in module 12) so the right shell runs them.

### VMs and WSL
A **virtual machine (VM)** runs a guest operating system on virtualized hardware. Its killer feature for learning is **snapshots**: save the machine's state, experiment fearlessly, and roll back in seconds. A VM gives you a full, conventional Linux system: real boot process, systemd, networking you control, and isolation from your main machine.

**WSL 2** runs a real Linux kernel in a lightweight VM integrated with Windows. It is excellent for command-line development and most of this course, but it differs from a conventional installation: service management, devices, networking, and boot behavior are not the same, and some labs (systemd services, firewalling, low-level networking) behave differently or not at all.

## Commands
```bash
printf 'Shell: %s\n' "$SHELL"
ps -p "$$" -o pid=,comm=
echo "$0"
bash --version | head -n 1
```

Sample output:

```text
Shell: /bin/bash
    PID COMMAND
   2410 bash
bash
GNU bash, version 5.2.21(1)-release ...
```

`$SHELL` describes your account's configured **login** shell; it may not be the shell currently interpreting a nested script. `ps -p "$$"` inspects the process that is actually running (`$$` is the current shell's process ID). When the answers disagree, believe `ps`.

## Choosing an environment
- Use a **VM** for full-system administration, snapshots, systemd services, and network labs. This is the environment this course assumes for anything risky.
- Use **WSL** for convenient command-line development and most utilities and scripting practice.
- Use a **dedicated lab VM** for security tools and experiments, on a host-only or NAT network.
- Do not expose vulnerable lab services to untrusted networks, and never point security tools at systems you do not own or lack written permission to test.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Identify the shell you are actually running right now, then start a Bash subshell, confirm you are inside it, and leave it.

<details>
<summary>Show a worked solution</summary>

```bash
ps -p "$$" -o pid=,comm=
bash
ps -p "$$" -o pid=,comm=
exit
```

The process ID changes inside the subshell, proving it is a new process; `exit` returns you to the parent shell.
</details>

**Exercise 2.** Demonstrate the `sh` versus Bash difference: run this one-liner under both and compare.

```bash
bash -c 'x=3; [[ $x == 3 ]] && echo bash-says-yes'
sh -c 'x=3; [[ $x == 3 ]] && echo sh-says-yes'
```

<details>
<summary>Show a worked solution</summary>

The first prints `bash-says-yes`. The second prints an error like `sh: 1: [[: not found`, because `[[` is a Bash keyword that POSIX `sh` (here `dash`) does not have. This is why scripts declare `#!/usr/bin/env bash` when they use Bash features.
</details>

**Exercise 3.** Decide and justify: you need to (a) practice creating users and systemd services, (b) write and test a small script during your Windows workday, (c) experiment with a deliberately vulnerable web app. Which environment for each?

<details>
<summary>Show a worked solution</summary>

(a) A VM: services and systemd behave conventionally there, and snapshots forgive mistakes. (b) WSL: fast to open, integrated with your Windows files and editor. (c) A dedicated, isolated lab VM on a host-only network: vulnerable services must never be reachable from untrusted networks.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** "I changed my terminal and now my aliases are gone." Which layer did they actually change, and where do aliases really live?

<details>
<summary>Show answer</summary>

They changed the terminal emulator, which only displays the session. Aliases belong to the shell's configuration (for Bash, files like `~/.bashrc`). If the new emulator starts the same shell with the same startup files, the aliases survive; if it starts a different shell, they do not.
</details>

**Q2.** A script starts with `#!/bin/sh` and uses arrays. What happens on Ubuntu, and why?

<details>
<summary>Show answer</summary>

It fails: on Ubuntu `/bin/sh` is `dash`, which has no arrays. The shebang selects the interpreter, so the script runs under `dash` even if the author's interactive shell is Bash. The fix is `#!/usr/bin/env bash`.
</details>

**Q3.** Why is a snapshot-enabled VM the recommended environment for the administration labs in this course?

<details>
<summary>Show answer</summary>

Administration labs create users, change permissions, and restart services; mistakes are part of learning. A snapshot restores a known-good state in seconds, and the VM's isolation keeps experiments away from your real system and network.
</details>

## Common mistakes
- Treating the terminal and the shell as synonyms.
- Assuming every Bash script runs unchanged under `sh`.
- Assuming WSL behaves identically to a physical Linux host for services, boot, and networking.
- Practicing destructive or security labs on your main machine instead of a snapshot-enabled VM.

## Key takeaways
The terminal is an interface, the shell is the interpreter, and the desktop is decoration. Choose your practice environment per task: WSL for convenience, a VM for realism and snapshots, an isolated lab VM for anything vulnerable or offensive.

## Further practice
Read the first sections of `man bash`, then skim the official Microsoft WSL documentation's comparison of WSL 1 and WSL 2 to understand exactly what your setup virtualizes.

## References
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
- [Microsoft WSL documentation](https://learn.microsoft.com/windows/wsl/)
- [GNOME](https://www.gnome.org/)
- [KDE Plasma](https://kde.org/plasma-desktop/)
