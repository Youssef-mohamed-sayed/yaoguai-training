# Linux Distributions


## Learning objectives
- Explain what a distribution provides beyond the kernel.
- Compare Ubuntu, Debian, Kali, Fedora, Arch, and other families.
- Choose an appropriate environment for a learning or operational task, and defend the choice.

## Introduction
A Linux distribution combines the kernel, user-space tools, package repositories, an installer, default configuration, documentation, and a support model. Different distributions optimize for different things: stability, rapid updates, enterprise support, simplicity, or specialist workflows. There is no "best" distribution, only good and bad matches between a distribution's model and your purpose.

Choosing well matters more than beginners expect, because your distribution decides your package manager, your default configurations, how quickly you receive updates, and how long the system is supported.

## What a distribution actually decides for you
- **Package format and manager:** `.deb` with APT (Debian family) versus `.rpm` with DNF (Fedora/RHEL family) versus pacman (Arch). Commands and package names differ between families.
- **Release model:** fixed releases with years of support (Debian, Ubuntu LTS) versus rolling releases that update continuously (Arch).
- **Defaults:** which desktop, init system, firewall, and security policies ship enabled.
- **Support lifecycle:** how long security updates are provided before you must upgrade.

## Distribution families

| Distribution | Family/model | Typical use |
|---|---|---|
| Debian | Independent, `.deb`, APT | Stable servers and general-purpose systems |
| Ubuntu | Debian-based, APT | Desktops, cloud, servers, learning |
| Kali Linux | Debian-based, APT | Authorized penetration testing and security labs |
| Fedora | RPM, DNF | Modern workstation and developer platform |
| RHEL | RPM, DNF | Enterprise environments and vendor support |
| Arch Linux | Rolling release, pacman | Customizable systems and learning internals |
| Linux Mint | Ubuntu/Debian-based | Beginner-friendly desktop |
| openSUSE | RPM, zypper | Workstations and enterprise-oriented systems |

Family relationships matter: Ubuntu is built from Debian, Mint from Ubuntu, so an `apt` command usually works across all three. It will do nothing useful on Fedora or Arch.

### How to choose
- For a **first Linux system**, Ubuntu LTS or Linux Mint is approachable, well documented, and widely answered about online.
- For **stable servers**, Debian or an enterprise distribution (RHEL or a rebuild like Rocky/Alma) prioritizes predictability over newness.
- For **security labs**, Kali packages hundreds of testing tools. It is a specialist toolkit, not a shortcut to learning Linux, and not a sensible daily desktop; use it in a lab VM and understand the underlying tools.
- For **learning internals**, Arch offers total control and the best wiki in Linux, but expects hands-on maintenance.
- For a **modern developer workstation**, Fedora ships relatively recent software with a predictable cadence.

A distribution's suitability depends on its support lifecycle, your hardware, organizational policy, and workload, not on popularity or aesthetics.

## Commands
```bash
cat /etc/os-release
cat /etc/debian_version 2>/dev/null
```

Sample output:

```text
$ cat /etc/os-release
NAME="Ubuntu"
VERSION="24.04 LTS (Noble Numbat)"
ID=ubuntu
ID_LIKE=debian
```

The first command is the portable starting point on almost every distribution; note `ID_LIKE=debian`, which records the family relationship. The second is Debian-family-specific and will not exist on Fedora or Arch. The `2>/dev/null` silences the error when the file is absent; module 08 explains redirection properly.

## Practice exercises
Do these in your own terminal (and browser for the research tasks). Try every task before opening its solution.

**Exercise 1.** Identify your current distribution, its version, and its family from `/etc/os-release` alone.

<details>
<summary>Show a worked solution</summary>

```bash
cat /etc/os-release
```

Read `NAME` and `VERSION` for the distribution, and `ID` / `ID_LIKE` for the family. `ID=fedora` with no `ID_LIKE` means Fedora itself; `ID=ubuntu` with `ID_LIKE=debian` means the Debian family.
</details>

**Exercise 2.** Find your distribution's official support lifecycle page and write down the date your current release stops receiving security updates. (Search for "<distribution> release cycle" or "EOL".)

<details>
<summary>Show a worked solution</summary>

For Ubuntu, the lifecycle is published on ubuntu.com/about/release-cycle: LTS releases receive five years of standard security maintenance. For Debian, see debian.org/releases. The habit that matters: before deploying anything, confirm the release is still inside its support window.
</details>

**Exercise 3.** In two or three sentences, explain to a junior colleague why Kali and Ubuntu are not interchangeable defaults for every server.

<details>
<summary>Show a worked solution</summary>

Kali is a Debian-based toolkit for authorized security testing: it ships hundreds of attack tools, defaults tuned for labs, and a threat model that assumes a temporary, controlled environment. Ubuntu is a general-purpose system with long support, server tooling, and conservative defaults. Running Kali as a server exposes unnecessary tools and weak defaults; running Ubuntu as a testing platform means assembling the toolkit yourself.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You find a tutorial that says `sudo dnf install nginx`. You are on Ubuntu. What do you do?

<details>
<summary>Show answer</summary>

Translate it to your family: `sudo apt install nginx`. `dnf` is the Fedora/RHEL package manager; Ubuntu uses APT. Package names are usually similar but not guaranteed identical.
</details>

**Q2.** What two facts about a distribution matter most when choosing one for a production server?

<details>
<summary>Show answer</summary>

The support lifecycle (how long security updates continue) and the release model (fixed, predictable releases versus rolling change). Package manager familiarity and organizational policy come next.
</details>

**Q3.** Why can an Ubuntu answer on a forum often help a Debian user, but not an Arch user?

<details>
<summary>Show answer</summary>

Ubuntu is built from Debian: same package format (`.deb`), same manager (APT), similar layout. Arch uses pacman, different package names, and a rolling model, so Debian-family instructions do not transfer.
</details>

## Common mistakes
- Installing Kali as a daily system without understanding its defaults and threat model.
- Mixing package repositories from different distributions or releases; this breaks systems in ways that are painful to undo.
- Assuming instructions written for `apt` apply to `dnf` or `pacman`.
- Choosing by logo and desktop screenshots instead of lifecycle and purpose.

## Key takeaways
Choose a distribution based on support and purpose, then learn the package manager and release model that belong to it. Families share tools; families do not share them across boundaries.

## Further practice
Compare the official installation and support documentation for Ubuntu, Debian, Fedora, and Arch. Note what each project emphasizes on its front page; that is the project telling you what it optimizes for.

## References
- [Ubuntu](https://ubuntu.com/)
- [Debian](https://www.debian.org/)
- [Kali Linux documentation](https://www.kali.org/docs/)
- [Fedora documentation](https://docs.fedoraproject.org/)
- [Arch Wiki](https://wiki.archlinux.org/)
