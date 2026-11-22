# SUID, SGID, Sticky Bit, and Least Privilege


## Learning objectives
- Recognize SUID, SGID, and sticky directory permissions.
- Inspect special permission bits.
- Explain least privilege and defensive privilege auditing.

## Special bits
- **SUID (set-user-ID):** on an executable file, a process may run with the file owner's effective UID. It is commonly represented by `s` in the owner's execute position.
- **SGID (set-group-ID):** on an executable, may set the effective group ID; on a directory, newly created entries commonly inherit the directory's group.
- **Sticky bit:** on a shared writable directory, users generally may remove or rename only entries they own (or where they have suitable privilege). `/tmp` commonly uses this bit.

Octal special-bit prefixes: SUID `4`, SGID `2`, sticky `1`. For example, `chmod 4755 file` sets SUID plus mode `755`; do not apply special bits casually.

## Inspection
```bash
ls -l /usr/bin/passwd
find /usr/bin -type f -perm -4000 -print 2>/dev/null
find / -xdev -type f -perm -2000 -print 2>/dev/null
ls -ld /tmp
```
`-perm -4000` finds files with the SUID bit set; `-xdev` avoids crossing filesystem boundaries. Results vary by distribution and installed software. A SUID file is not automatically vulnerable; it deserves review of ownership, package origin, expected behavior, and updates.

## Least privilege
Give a user, service, or process only the permissions required for its task, for only as long as needed. Avoid broad sudo rules, world-writable configuration, unnecessary SUID programs, and shared accounts. Review changes and remove temporary privileges.

## Hands-on practice
- Inspect `/tmp` permissions and explain the sticky bit.
- List SUID files on your own VM and identify which package owns one using the package manager.
- Do not modify or execute unknown privileged binaries.
- Hint: use `stat` and your distribution's package-query tool.

## Common mistakes
- Treating every SUID binary as an exploitable vulnerability.
- Removing special bits from system files without understanding package expectations.
- Setting SUID on scripts; behavior is platform- and kernel-dependent and is generally not a safe design.

## Key takeaways
Special bits affect execution identity and shared-directory behavior. Audit them carefully; do not alter them as an experiment on a production host.

## Further practice
Study Linux capabilities and service account design at a conceptual level after completing this course.

## References
- [chmod(1)](https://man7.org/linux/man-pages/man1/chmod.1.html)
- [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html)
