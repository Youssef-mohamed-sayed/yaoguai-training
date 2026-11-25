# Debian and Ubuntu: apt and dpkg


## Learning objectives
- Explain repositories, dependencies, and package signatures.
- Update indexes, install, remove, and inspect software with APT.
- Use dpkg for the lower-level questions APT does not answer.

## Core concepts
A package manager is the difference between installing software and *maintaining* it. It downloads packages from configured **repositories** (software sources maintained by the distribution or a trusted provider), verifies their signatures against the repository's keys, resolves **dependencies** (the other packages the software needs), tracks every installed file, and handles upgrades and removal cleanly. Installing software any other way (random downloads, `curl | sh`) abandons all of those guarantees.

On Debian and Ubuntu, two tools share the work:

- **APT** (`apt`) is the high-level manager: repositories, dependencies, upgrades.
- **dpkg** is the low-level tool: the local package database and individual `.deb` files.

## Commands
```bash
sudo apt update                 # refresh the repository indexes
apt search openssh-client       # find packages by name/description
apt show openssh-client         # metadata: version, size, dependencies
sudo apt install tree           # install
sudo apt upgrade                # upgrade installed packages
sudo apt remove tree            # remove, keep configuration
sudo apt purge tree             # remove including configuration
apt list --installed            # everything installed
dpkg -l openssh-client          # installed status of one package
dpkg -S /usr/bin/ssh            # which package owns this file?
dpkg -L openssh-client          # which files does this package own?
```

The pair everyone confuses: `apt update` refreshes the **list of available packages** and changes nothing on disk; `apt upgrade` actually installs newer versions. The routine is always `update` first, then `upgrade`.

`remove` versus `purge` matters months later: `remove` leaves the package's configuration in `/etc` (so reinstalling restores your settings); `purge` deletes that too.

### Local .deb files
```bash
sudo dpkg -i package.deb
sudo apt --fix-broken install
```

`dpkg -i` installs a local file but does not fetch dependencies; if it complains about missing ones, `apt --fix-broken install` resolves them from the repositories. Only install `.deb` files from sources you trust as much as the distribution itself: a package installs **as root** and can run scripts during installation.

## Troubleshooting
- Read the exact error before retrying anything.
- Check network reachability and the repository URLs in `/etc/apt/sources.list` and `/etc/apt/sources.list.d/`.
- Never delete APT/dpkg lock files while a package process is running; find the process (`ps aux | grep -E 'apt|dpkg'`) and let it finish.
- Do not mix repositories from different releases (a PPA built for 22.04 on a 24.04 system) or, worse, from other distributions.
- If an interrupted operation left the database inconsistent, follow the distribution's recovery documentation rather than guessing at repair commands.

## Practice exercises
Do these in your own terminal (a VM for installs). Try every task before opening its solution.

**Exercise 1.** Refresh your package indexes, search for `tree`, read its metadata, install it, and prove it runs.

<details>
<summary>Show a worked solution</summary>

```bash
sudo apt update
apt search '^tree$'
apt show tree
sudo apt install tree
command -v tree && tree --version
```

If `apt search` finds nothing, the indexes were stale; `update` is the fix.
</details>

**Exercise 2.** Answer with dpkg: which package owns `/usr/bin/ssh`, and what version is installed?

<details>
<summary>Show a worked solution</summary>

```bash
dpkg -S /usr/bin/ssh
dpkg -l openssh-client | tail -n 1
```

Output:

```text
openssh-client: /usr/bin/ssh
ii  openssh-client 1:9.6p1-3ubuntu13  amd64  secure shell (SSH) client...
```

`ii` means intended-installed, currently-installed.
</details>

**Exercise 3.** List every file the `tree` package installed, then remove it completely including its configuration, and verify it is gone.

<details>
<summary>Show a worked solution</summary>

```bash
dpkg -L tree
sudo apt purge tree
dpkg -l tree 2>/dev/null || echo "tree is gone"
command -v tree || echo "no tree on PATH"
```
</details>

**Exercise 4.** A colleague says "I ran `apt update` yesterday, so the system is fully patched." Correct them in one sentence.

<details>
<summary>Show a worked solution</summary>

`apt update` only refreshes the package *lists*; nothing was upgraded until `apt upgrade` (or `apt full-upgrade`) runs.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You removed a package and reinstalled it a month later; your old settings were still there. Why, and how would you have prevented it?

<details>
<summary>Show answer</summary>

`apt remove` leaves configuration files in `/etc`. `apt purge` removes those too.
</details>

**Q2.** Why is `dpkg -i random-file.deb` riskier than `apt install something`?

<details>
<summary>Show answer</summary>

`dpkg -i` does not resolve dependencies and, more importantly, the file's origin is on you: packages install as root and can execute maintainer scripts. APT installs only from configured, signature-verified repositories.
</details>

**Q3.** Which command tells you every file a package owns, and which tells you what package owns a file?

<details>
<summary>Show answer</summary>

`dpkg -L package` lists a package's files; `dpkg -S /path` finds the owning package.
</details>

## Common mistakes
- Confusing `apt update` with `apt upgrade`.
- Expecting `dpkg -i` to fetch dependencies.
- Adding untrusted repositories to get one tool.
- Killing lock files while a package operation runs.

## Key takeaways
APT for repository operations, dpkg for database questions. `update` then `upgrade`, `purge` when you mean "completely", and trust only signed repositories.

## Further practice
Read `man apt` and `man dpkg`, then inspect three packages on your system: what they own, what owns them, and when they were last upgraded (`grep` the dpkg log).

## References
- [Debian package management](https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html)
- [Ubuntu documentation](https://help.ubuntu.com/)
