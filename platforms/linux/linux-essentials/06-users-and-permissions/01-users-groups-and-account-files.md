# Users, Groups, and Account Databases


## Learning objectives
- Distinguish root, regular, and system accounts.
- Read UID, GID, and group membership information.
- Locate account configuration files safely.

## Core concepts
Each process runs with user and group identity information. A **UID** identifies a user; a **GID** identifies a group. Root normally has UID 0 and broad administrative authority. System accounts run services and usually should not be used for interactive work. Regular accounts are used by people.

Important files:
- `/etc/passwd`: account metadata, including username, UID, primary GID, home directory, and login shell. Password hashes are not normally stored here.
- `/etc/shadow`: password hash and password-aging data; restricted access.
- `/etc/group`: group names, GIDs, and supplementary member lists.
- `/etc/sudoers` and `/etc/sudoers.d/`: sudo policy. Edit with `visudo`, which validates syntax.

Do not publish `/etc/shadow` contents or copy password hashes into notes.

## Commands
```bash
whoami
id
groups
getent passwd "$USER"
getent group sudo
```
`getent` queries configured account databases, which may include network identity sources, not just local files.

Administrative account operations (distribution options differ):
```bash
sudo useradd -m -s /bin/bash labuser
sudo passwd labuser
sudo usermod -aG sudo labuser   # Debian/Ubuntu convention
sudo groupadd labteam
sudo usermod -aG labteam labuser
```
On some Red Hat-family systems, the administrative group is `wheel` rather than `sudo`. `-aG` appends supplementary groups; omitting `-a` can replace the existing supplementary group list. Verify with `id labuser`.

## Hands-on practice
- Inspect your own `id`, `groups`, and `getent passwd "$USER"` output.
- In a disposable VM, create a test account and group, add the account to the group, and verify membership.
- Remove the test account only after confirming it is the account you created.
- Hint: `userdel -r labuser` removes the account and its home directory; use only for the disposable account.

## Common mistakes
- Assuming `/etc/passwd` contains password hashes.
- Editing `/etc/sudoers` with a normal text editor rather than `visudo`.
- Using `usermod -G` without `-a` and unintentionally removing group memberships.
- Giving service accounts interactive shells without a reason.

## Key takeaways
UID/GID identity drives ownership and access. Protect shadow data and grant administrative rights deliberately.

## Further practice
Read `man passwd`, `man shadow`, `man useradd`, and `man usermod`.

## References
- [passwd(5)](https://man7.org/linux/man-pages/man5/passwd.5.html)
- [shadow(5)](https://man7.org/linux/man-pages/man5/shadow.5.html)
- [sudoers(5)](https://man7.org/linux/man-pages/man5/sudoers.5.html)
