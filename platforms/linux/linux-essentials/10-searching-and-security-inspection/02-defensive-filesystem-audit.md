# Defensive Filesystem and Permission Auditing


## Learning objectives
- Identify risky file permissions for review.
- Understand why credentials and configuration files require protection.
- Document findings without changing the system.

## What to inspect
A basic defensive review may look for:
- World-writable files and directories outside intended shared locations.
- Unexpected SUID/SGID executables.
- Sensitive files readable by unintended users.
- Unexpected ownership under application and configuration directories.
- Private SSH keys with overly broad permissions.
- Secrets accidentally committed to source trees or written into logs.

Examples:
```bash
find /etc -type f -perm -0002 -ls 2>/dev/null
find / -xdev -type f -perm -4000 -ls 2>/dev/null
find /home -type f -name 'id_*' -ls 2>/dev/null
stat ~/.ssh ~/.ssh/authorized_keys 2>/dev/null
```
These are discovery commands, not proof of a vulnerability. Interpret findings in context. Some applications legitimately need special permissions. Do not alter system-owned files without a change plan.

### Protecting secrets
- Store private keys with restrictive permissions (commonly `600` for a private key file).
- Limit access to configuration files containing credentials.
- Avoid putting passwords in shell history, command-line arguments, or source code.
- Use a secrets manager or protected service configuration where appropriate.
- Rotate credentials if exposure is suspected.

## Hands-on practice
- Audit only `~/linux-lab`, not the entire host.
- Create one deliberately world-readable sample file and one private sample file.
- Compare `stat` output and explain the access difference.
- Write a short finding with path, owner, mode, expected state, and recommendation.

## Common mistakes
- Calling every world-readable file sensitive.
- Treating a scan result as proof of exploitability.
- Changing permissions before recording the original state.
- Running untrusted scripts with root privileges to “fix” findings.

## Key takeaways
Auditing is evidence gathering. Record context and recommend least-privilege changes rather than blindly modifying files.

## Further practice
Repeat the audit on a disposable VM and compare the result with a clean installation.

## References
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
