# SUID, SGID, Sticky Bit, and Least Privilege


## Learning objectives
- Recognize SUID, SGID, and sticky directory permissions in listings.
- Inspect special permission bits on a real system.
- Explain least privilege and perform a defensive privilege audit without breaking anything.

## The three special bits
Beyond `rwx`, three extra bits change how execution and shared directories behave:

- **SUID (set-user-ID, value 4):** on an executable file, the process runs with the **file owner's** effective UID instead of the caller's. Shown as `s` in the owner's execute position. This is how `passwd` lets an ordinary user change a password stored in root-owned `/etc/shadow`: `/usr/bin/passwd` is SUID root, so it briefly acts with root's authority for that one, carefully reviewed task.
- **SGID (set-group-ID, value 2):** on an executable, the process runs with the file's group. On a **directory**, new files and subdirectories inherit the directory's group instead of the creator's primary group, which is exactly what shared team directories need. Shown as `s` in the group's execute position.
- **Sticky bit (value 1):** on a shared writable directory, users may delete or rename only entries they own. `/tmp` is the classic example: everyone may create files there, but you cannot remove someone else's. Shown as `t` in others' execute position.

Octal prefix: special bits form a leading digit, `chmod 4755 file` = SUID + `755`, `chmod 2770 dir` = SGID + `770`, `chmod 1777 dir` = sticky + `777`.

## Inspecting them
```bash
ls -l /usr/bin/passwd
ls -ld /tmp
find /usr/bin -type f -perm -4000 -print 2>/dev/null
find / -xdev -type f -perm -2000 -print 2>/dev/null
```

Sample output:

```text
-rwsr-xr-x 1 root root 68208 Nov 12  2024 /usr/bin/passwd
drwxrwxrwt 14 root root 4096 Nov 25 04:25 /tmp
```

`-perm -4000` finds files with SUID set; `-perm -2000` finds SGID; `-xdev` keeps the search on one filesystem. On any normal system you will find a handful of SUID binaries (`passwd`, `sudo`, `su`, `ping` on some systems). A SUID file is **not automatically a vulnerability**, but each one is code that runs with elevated authority, so each deserves review: expected package origin, correct owner, current updates.

> [!WARNING]
> Never experiment with special bits on a production host, and never set SUID on scripts. Script SUID behavior is platform-dependent and historically insecure; if a task needs privilege, use a reviewed SUID binary or a narrow sudo rule.

## Least privilege
The organizing principle for everything in this module: **give a user, service, or process only the permissions its task requires, for only as long as the task lasts.** In practice that means:

- No broad `sudo` rules ("this user may run anything") when three specific commands would do.
- No world-writable configuration or shared directories without the sticky bit.
- No unnecessary SUID programs; audit the ones you have.
- No shared human accounts; shared access belongs to groups.
- Temporary privileges get reviewed and removed.

## Practice exercises
Do these in your own terminal (a VM for the write operations). Try every task before opening its solution.

**Exercise 1.** Explain the permissions on `/tmp` from its `ls -ld` output, field by field, including the final `t`.

<details>
<summary>Show a worked solution</summary>

```bash
ls -ld /tmp
```

`drwxrwxrwt`: a directory; owner root has `rwx`; group root has `rwx`; others have `rwx` **plus sticky** (`t`). The world-writable mode lets every user create temp files; the sticky bit stops users deleting each other's files. World-writable *without* sticky would be a problem; with sticky it is the intended design.
</details>

**Exercise 2.** List the SUID binaries on your system, pick one, and identify which package owns it.

<details>
<summary>Show a worked solution</summary>

```bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
dpkg -S /usr/bin/passwd      # Debian/Ubuntu
rpm -qf /usr/bin/passwd      # Fedora/RHEL
```

Every result should trace back to a package from your distribution. A SUID binary no package claims is a finding worth investigating.
</details>

**Exercise 3.** Build a proper shared directory: create `/srv/team` owned by group `labteam`, group-writable, with SGID so new files stay in `labteam`, then create a file inside and verify its group.

<details>
<summary>Show a worked solution</summary>

```bash
sudo groupadd labteam
sudo usermod -aG labteam "$USER"
sudo mkdir -p /srv/team
sudo chown root:labteam /srv/team
sudo chmod 2770 /srv/team
# new login session (or: newgrp labteam), then:
touch /srv/team/shared.txt
ls -l /srv/team/shared.txt
```

The new file's group is `labteam` even though your primary group is your own; that inheritance is the SGID bit working. Mode `2770` = SGID + owner/group full access + nothing for others.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** In `-rwsr-xr-x`, what does the `s` mean, and whose privileges does the program run with?

<details>
<summary>Show answer</summary>

SUID is set: the program runs with the file *owner's* effective UID (here root), no matter who launches it.
</details>

**Q2.** Two teammates share `/srv/team` and keep creating files the other cannot edit, because new files land in each creator's private group. Which bit fixes the directory, and why?

<details>
<summary>Show answer</summary>

SGID on the directory: new entries inherit the directory's group (`labteam`), so group write permission actually reaches both teammates.
</details>

**Q3.** You find a SUID-root binary in `/home/someuser/bin` that no package owns. React?

<details>
<summary>Show answer</summary>

Treat it as a security finding, not a curiosity: do not execute it, record it (`stat`, `file`, hash), and report/remove it through your change process. Unowned SUID-root files in user-writable locations are a classic persistence and privilege-escalation technique.
</details>

## Common mistakes
- Treating every SUID binary as an exploitable vulnerability; review, don't panic.
- Removing special bits from system files without understanding what the package expects.
- Setting SUID on scripts.
- Making shared directories `777` instead of `2770` with a proper group.

## Key takeaways
SUID borrows the owner's identity, SGID shares a group, sticky protects entries in shared directories. Audit special bits regularly, and let least privilege decide every grant.

## Further practice
After this course, study Linux capabilities (`man 7 capabilities`) and how services drop privileges; they are the modern refinement of everything in this lesson.

## References
- [chmod(1)](https://man7.org/linux/man-pages/man1/chmod.1.html)
- [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html)
