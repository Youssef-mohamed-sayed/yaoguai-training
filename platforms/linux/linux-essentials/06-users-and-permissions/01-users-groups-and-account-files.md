# Users, Groups, and Account Databases


## Learning objectives
- Distinguish root, regular, and system accounts, and read UID/GID identity information.
- Locate and safely read the account configuration files.
- Create and modify test accounts in a disposable environment without breaking anything real.

## Core concepts
Every process on Linux runs with an identity: a **UID** (user ID) and one or more **GIDs** (group IDs). The kernel checks these numbers, not names, when deciding what a process may do. Three kinds of accounts matter:

- **root (UID 0):** the superuser. Most permission checks simply do not apply to it. Reserved for administration.
- **System accounts (low UIDs, often 1-999):** identities that run services, like `www-data` or `postgres`. They own files and processes so a compromised service does not become root. They normally have no valid password and a non-login shell, and should never be used interactively.
- **Regular accounts (UID 1000+ on most distributions):** people. Daily work belongs here.

Groups collect users for shared access: a file can grant its group read or write access, and every member inherits it. Each user has one **primary** group and any number of **supplementary** groups.

### The account files
- `/etc/passwd`: account metadata, one line per account: username, placeholder `x`, UID, primary GID, description, home directory, login shell. World-readable; password hashes are **not** here (they moved out decades ago precisely because this file must be readable).
- `/etc/shadow`: password hashes and password-aging data. Readable only by root (and the `shadow` group). Protect it accordingly: never paste its contents into tickets, notes, or chat.
- `/etc/group`: group names, GIDs, and supplementary member lists.
- `/etc/sudoers` and `/etc/sudoers.d/`: who may use `sudo` and how. **Always edit with `visudo`**, which checks syntax before saving; a broken sudoers file can lock every administrator out of privilege.

## Commands
```bash
whoami
id
groups
getent passwd "$USER"
getent group sudo
```

Sample output:

```text
$ id
uid=1000(learner) gid=1000(learner) groups=1000(learner),27(sudo)
$ getent passwd learner
learner:x:1000:1000:Learner:/home/learner:/bin/bash
```

`getent` queries the configured account databases, which may include network identity sources (LDAP, AD), not just the local files, so it is the most truthful way to ask "what accounts exist here?"

### Administrative operations (disposable VM only)
```bash
sudo useradd -m -s /bin/bash labuser
sudo passwd labuser
sudo groupadd labteam
sudo usermod -aG sudo labuser      # Debian/Ubuntu: grant admin
sudo usermod -aG labteam labuser   # add to a team group
id labuser
```

- `useradd -m` creates the home directory; `-s` sets the login shell (the default may be a non-interactive one).
- On Red Hat-family systems the administrative group is `wheel`, not `sudo`.
- `-aG` **appends** supplementary groups. `usermod -G` *without* `-a` replaces the entire supplementary list, a classic way to accidentally strip someone's `sudo` membership. Verify with `id` after every change.
- Group membership applies at login: a user already logged in must start a new session to see new groups.

## Practice exercises
Do these in your own terminal. Account creation belongs in a disposable VM. Try every task before opening its solution.

**Exercise 1.** Read your own identity: run `whoami`, `id`, and `getent passwd "$USER"`, and identify your UID, primary group, and every supplementary group by name.

<details>
<summary>Show a worked solution</summary>

```bash
whoami
id
getent passwd "$USER"
```

In `id` output like `uid=1000(learner) gid=1000(learner) groups=1000(learner),27(sudo)`, your UID is 1000, primary group `learner`, and `sudo` is a supplementary group, meaning this account may use `sudo`.
</details>

**Exercise 2.** In a disposable VM: create user `labuser` with a home directory and Bash shell, set a password, create group `labteam`, add `labuser` to it, and prove the membership.

<details>
<summary>Show a worked solution</summary>

```bash
sudo useradd -m -s /bin/bash labuser
sudo passwd labuser
sudo groupadd labteam
sudo usermod -aG labteam labuser
id labuser
```

The last command shows `groups=...(labuser),...(labteam)`. If it does not, re-check that you typed `-aG`, not `-G`.
</details>

**Exercise 3.** Find the accounts on your system that can actually log in interactively: list entries in `/etc/passwd` whose shell is a real shell.

<details>
<summary>Show a worked solution</summary>

```bash
grep -E '/(bash|sh|zsh)$' /etc/passwd
```

Typical result: `root` and the regular user accounts. System accounts point at `/usr/sbin/nologin` or `/bin/false`, which is how a service account is prevented from logging in even if its password were known.
</details>

**Exercise 4.** Clean up the test account from exercise 2, safely.

<details>
<summary>Show a worked solution</summary>

```bash
id labuser                 # confirm this is the disposable account
sudo userdel -r labuser    # removes the account and its home directory
sudo groupdel labteam
id labuser                 # confirms: no such user
```

Only ever run `userdel -r` on an account you created for the lab, after confirming the name.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Does `/etc/passwd` contain password hashes? Where are they, and why the split?

<details>
<summary>Show answer</summary>

No. Hashes live in `/etc/shadow`, readable only by root. `/etc/passwd` must stay world-readable because every program resolving names to UIDs reads it; keeping hashes out of it keeps them away from every user on the system.
</details>

**Q2.** What is wrong with `sudo usermod -G labteam labuser` when the intent was to *add* a group?

<details>
<summary>Show answer</summary>

Without `-a`, `-G` replaces the user's entire supplementary group list with just `labteam`, silently removing memberships like `sudo`. The correct command is `sudo usermod -aG labteam labuser`.
</details>

**Q3.** Why do services run as dedicated system accounts instead of root?

<details>
<summary>Show answer</summary>

Containment. If the service is compromised, the attacker inherits only that account's limited permissions instead of the whole machine.
</details>

## Common mistakes
- Assuming `/etc/passwd` contains password hashes.
- Editing `/etc/sudoers` with a plain editor instead of `visudo`.
- Using `usermod -G` without `-a` and destroying group memberships.
- Giving service accounts interactive shells "temporarily" and forgetting.
- Expecting new group membership to apply to sessions that are already logged in.

## Key takeaways
UID/GID numbers drive every ownership and access decision. Know the three account kinds, read identity with `id` and `getent`, guard `/etc/shadow`, and append groups with `-aG` every single time.

## Further practice
Read `man passwd`, `man shadow`, `man useradd`, and `man usermod`, then list the system accounts on your own machine and note what each one runs.

## References
- [passwd(5)](https://man7.org/linux/man-pages/man5/passwd.5.html)
- [shadow(5)](https://man7.org/linux/man-pages/man5/shadow.5.html)
- [sudoers(5)](https://man7.org/linux/man-pages/man5/sudoers.5.html)
