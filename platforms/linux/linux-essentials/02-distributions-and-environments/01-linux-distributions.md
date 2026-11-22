# Linux Distributions


## Learning objectives
- Explain what a distribution provides.
- Compare Ubuntu, Debian, Kali, Fedora, Arch, and other families.
- Choose an appropriate environment for a learning or operational task.

## Introduction
A Linux distribution combines a kernel, user-space tools, package repositories, installer, defaults, and support model. Different distributions optimize for stability, rapid updates, enterprise support, simplicity, or specialist workflows.

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

### How to choose
- For a first Linux system, Ubuntu LTS or Linux Mint is approachable.
- For stable servers, Debian or an enterprise distribution may be appropriate.
- Kali is a specialist toolkit, not a shortcut to learning Linux. Use it in a lab and understand the underlying tools.
- Arch offers control and documentation but expects more hands-on maintenance.
- Fedora favors relatively recent software and technologies.

A distribution's suitability depends on support lifecycle, hardware, organizational policy, and workload—not popularity alone.

## Commands
```bash
cat /etc/os-release
cat /etc/debian_version 2>/dev/null
```
The first is the portable starting point on many distributions. The second is Debian-family-specific and may not exist elsewhere.

## Hands-on practice
1. Identify your current distribution and version.
2. Find its official documentation and support lifecycle.
3. Explain why Kali and Ubuntu are not interchangeable defaults for every server.

## Common mistakes
- Installing Kali as a daily system without understanding its defaults and threat model.
- Mixing package repositories from different distributions.
- Assuming instructions for `apt` apply to `dnf` or `pacman`.

## Key takeaways
Choose a distribution based on support and purpose. Learn the package manager and release model that belong to it.

## Further practice
Compare the official installation and support documentation for Ubuntu, Debian, Fedora, and Arch.

## References
- [Ubuntu](https://ubuntu.com/)
- [Debian](https://www.debian.org/)
- [Kali Linux documentation](https://www.kali.org/docs/)
- [Fedora documentation](https://docs.fedoraproject.org/)
- [Arch Wiki](https://wiki.archlinux.org/)
