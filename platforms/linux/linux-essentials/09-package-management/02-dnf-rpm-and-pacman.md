# Fedora/RHEL: dnf and rpm; Arch: pacman


## Learning objectives
- Identify the right package manager for RPM-family and Arch systems.
- Install, update, remove, search, and inspect packages on each.
- Avoid the classic cross-family and partial-upgrade mistakes.

## Fedora and the Red Hat family
```bash
sudo dnf check-update     # list available updates (exit 100 means: yes, updates exist)
sudo dnf search htop
sudo dnf info htop
sudo dnf install htop
sudo dnf upgrade          # the full system upgrade
sudo dnf remove htop
rpm -q htop               # installed version
rpm -ql bash              # files the package owns
rpm -qf /usr/bin/bash     # package owning this file
```

The split mirrors Debian's: **dnf** is the high-level manager (repositories, dependencies, upgrades), **rpm** is the low-level database and `.rpm` file tool. Two dnf habits differ from APT habits:

- There is no separate "update the indexes" command; dnf refreshes metadata automatically as needed.
- `dnf check-update` uses its exit status to communicate: `0` means no updates, `100` means updates are available. A nonzero status here is information, not an error.

RHEL, CentOS Stream, Rocky, and AlmaLinux all share this toolchain, which is why it is the enterprise standard you will meet at work.

## Arch Linux
```bash
sudo pacman -Syu          # sync databases AND upgrade everything
pacman -Ss htop           # search repositories
sudo pacman -S htop       # install
pacman -Qi htop           # info on an installed package
pacman -Ql htop           # files the package owns
pacman -Qo /usr/bin/htop  # package owning this file
sudo pacman -R htop       # remove
```

pacman's flags are dense but consistent: capital letters select the operation (`-S` sync/install, `-R` remove, `-Q` query the local database), lowercase letters modify it (`-y` refresh, `-u` upgrade, `-s` search, `-i` info, `-l` list).

> [!WARNING]
> Arch expects **full** upgrades. Installing one new package without upgrading the rest (`pacman -S something` on a stale system) can pull new libraries into an old system and break dependencies. The supported routine is `pacman -Syu`, then install.

## Package verification and trust
All three families verify package signatures against keys the distribution configured; that verification is what makes repository software trustworthy. Never bypass signature checks to force an install (`--nogpgcheck`, `SigLevel = Never`): the error is telling you something real. When auditing a system, confirm that every package traces back to an expected repository.

## Practice exercises
Do these on a matching system (Fedora/RHEL VM for dnf, Arch VM for pacman). Try every task before opening its solution.

**Exercise 1.** Identify your distribution from `/etc/os-release`, then use only that family's tools to search for `htop` and read its package metadata.

<details>
<summary>Show a worked solution</summary>

Fedora/RHEL:

```bash
sudo dnf search htop
sudo dnf info htop
```

Arch:

```bash
pacman -Ss htop
pacman -Si htop    # repository info; -Qi once installed
```

The point of the exercise is resisting the urge to type the family you already know.
</details>

**Exercise 2.** On an RPM system, find which package owns `/usr/bin/bash` and list five other files that same package owns.

<details>
<summary>Show a worked solution</summary>

```bash
rpm -qf /usr/bin/bash
rpm -ql bash | head -n 6
```

Same shape as `dpkg -S` and `dpkg -L`; only the tool names change.
</details>

**Exercise 3.** A runbook for Ubuntu says `sudo apt update && sudo apt install nginx`. Write the faithful Fedora and Arch equivalents, including each family's "correct update routine".

<details>
<summary>Show a worked solution</summary>

Fedora: `sudo dnf check-update && sudo dnf install nginx` (metadata refreshes automatically). Arch: `sudo pacman -Syu && sudo pacman -S nginx`, and the full upgrade is not optional on Arch.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** `dnf check-update` exits with status 100. Did it fail?

<details>
<summary>Show answer</summary>

No: exit 100 is how dnf reports "updates are available". Exit 0 means nothing to do. Read the output before assuming any nonzero status is an error.
</details>

**Q2.** Why is a partial upgrade dangerous on Arch specifically?

<details>
<summary>Show answer</summary>

Arch is rolling: packages are built against the current library versions. Installing new packages onto otherwise-old libraries mixes incompatible versions and breaks dependencies. `pacman -Syu` keeps the whole system on one consistent snapshot.
</details>

**Q3.** A guide tells you to disable signature verification because the install "keeps failing". What should you do instead?

<details>
<summary>Show answer</summary>

Stop and investigate the signature error: it may indicate a misconfigured keyring, a wrong repository, or tampering. Disabling verification removes the only check standing between you and an unsigned package running as root.
</details>

## Common mistakes
- Running `apt` on Fedora or `pacman` on Ubuntu.
- Partial upgrades on Arch.
- Disabling signature checks to silence an error.
- Removing a package without checking what depends on it (`dnf remove` and `pacman -R` show you; read before confirming).

## Key takeaways
Package commands are family-specific, but the mental model is identical: refresh metadata, search, inspect, install, upgrade everything, remove carefully. Identify the OS first (`/etc/os-release`), then use its supported workflow.

## Further practice
Read the official package-management guide for your distribution, then compare `rpm -qi bash` and `pacman -Qi bash` side by side if you have both VMs: the data is the same, only the flags differ.

## References
- [DNF documentation](https://dnf.readthedocs.io/)
- [RPM documentation](https://rpm.org/documentation.html)
- [Arch Wiki: pacman](https://wiki.archlinux.org/title/Pacman)
