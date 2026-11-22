# Fedora/RHEL: dnf and rpm; Arch: pacman


## Learning objectives
- Identify the package manager for RPM and Arch systems.
- Install, update, remove, search, and inspect packages.
- Avoid mixing package ecosystems.

## Fedora and Red Hat family
```bash
sudo dnf check-update
sudo dnf search htop
sudo dnf info htop
sudo dnf install htop
sudo dnf upgrade
sudo dnf remove htop
rpm -q htop
rpm -ql bash
rpm -qf /usr/bin/bash
```
`dnf` resolves repositories and dependencies. `rpm` queries and manages the RPM package database and local RPM files. `dnf check-update` returning a nonzero status can indicate updates are available; read the output rather than treating every nonzero status as a failure.

## Arch Linux
```bash
sudo pacman -Syu
pacman -Ss htop
sudo pacman -S htop
pacman -Qi htop
pacman -Ql htop
sudo pacman -R htop
```
`-Syu` synchronizes package databases and performs a full system upgrade. Arch generally expects full upgrades; partial upgrades are unsupported and can break dependency consistency. `-Ss` searches repositories; `-Qi` inspects an installed package; `-Ql` lists package files.

## Package verification and trust
Use official repositories and verify package signatures using the distribution's configured trust chain. Do not bypass signature checks to force an installation. Confirm a package's origin and maintainer when auditing a system.

## Hands-on practice
- Identify your distribution with `/etc/os-release`.
- Use only the package manager for that distribution to search for `htop`.
- Inspect an installed package and identify one file it owns.
- Do not run commands from all three package families on one system.

## Common mistakes
- Running `apt` on Fedora or `pacman` on Ubuntu.
- Performing an Arch partial upgrade.
- Disabling signature checks to silence an error.
- Removing a package without checking dependent software.

## Key takeaways
Package commands are distribution-specific. Identify the OS first and use its supported repository workflow.

## Further practice
Read the official package-management guide for your distribution.

## References
- [DNF documentation](https://dnf.readthedocs.io/)
- [RPM documentation](https://rpm.org/documentation.html)
- [Arch Wiki: pacman](https://wiki.archlinux.org/title/Pacman)
