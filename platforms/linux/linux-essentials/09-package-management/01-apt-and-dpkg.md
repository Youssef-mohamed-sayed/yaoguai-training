# Debian and Ubuntu: apt and dpkg


## Learning objectives
- Explain repositories and package dependencies.
- Update indexes, install, remove, and inspect packages with APT.
- Use dpkg for lower-level package inspection.

## Core concepts
A package manager installs software from configured repositories, verifies package metadata/signatures according to repository configuration, resolves dependencies, tracks installed files, and supports upgrades and removal. Repositories are software sources maintained by a distribution or trusted provider.

APT is the higher-level package manager on Debian and Ubuntu. `dpkg` works with local Debian package files and the installed package database.

## Commands (Debian/Ubuntu)
```bash
sudo apt update
apt search openssh-client
apt show openssh-client
sudo apt install tree
sudo apt upgrade
sudo apt remove tree
sudo apt purge tree
apt list --installed
dpkg -l openssh-client
dpkg -S /usr/bin/ssh
```
- `apt update` refreshes repository indexes; it does not upgrade packages.
- `apt upgrade` upgrades installed packages where possible.
- `remove` removes package files but may retain configuration; `purge` also removes package configuration.
- `dpkg -S` asks which installed package owns a path.

Install a local package with `sudo dpkg -i package.deb`; if dependencies are missing, use APT to resolve them where possible. Do not download random `.deb` files from untrusted websites.

## Troubleshooting
- Check network and repository URLs.
- Read the exact error before retrying.
- Avoid deleting lock files while package-manager processes are running.
- Do not mix repositories from unrelated Debian/Ubuntu releases.
- If a package database is interrupted, follow the distribution's recovery documentation rather than running guessed repair commands.

## Hands-on practice
- Search for `tree`, inspect its metadata, install it, and verify its path with `command -v tree`.
- Remove it after practice if you do not need it.
- Hint: package indexes must be current for accurate search results.

## Common mistakes
- Confusing `apt update` with `apt upgrade`.
- Using `dpkg -i` and assuming dependencies will be automatically resolved.
- Adding untrusted repositories to obtain a single tool.

## Key takeaways
Use APT for normal package operations and dpkg for lower-level package database tasks.

## Further practice
Read `man apt`, `man dpkg`, and Ubuntu's repository documentation.

## References
- [Debian package management](https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html)
- [Ubuntu documentation](https://help.ubuntu.com/)
