# Least Privilege and Defensive Linux Administration


## Learning objectives
- Explain the principle of least privilege.
- Recognize common privilege and configuration risks.
- Build a safe, evidence-based review workflow.

## Core concepts
Linux security is built from multiple controls: identity, permissions, process isolation, kernel security features, network policy, package trust, service configuration, and monitoring. No single permission listing proves a host is secure.

Least privilege means:
1. Use a regular account for routine work.
2. Elevate only the command that requires administration.
3. Give services dedicated accounts and only required access.
4. Avoid broad sudo rules and shared credentials.
5. Remove obsolete accounts, keys, and services through an approved process.

## Defensive review commands
```bash
id
sudo -l
getent passwd
getent group sudo
ss -tulpen
systemctl --type=service --state=running
find / -xdev -type f -perm -4000 -print 2>/dev/null
```
`sudo -l` shows commands the current user may run under sudo policy. `ss` inspects sockets; `-t` TCP, `-u` UDP, `-l` listening, `-p` process, `-e` extended, `-n` numeric. Some process details require root. These commands are for systems you administer or are authorized to audit.

## Security interpretation
- A listening port is not automatically a vulnerability; identify the service and exposure.
- A privileged executable is not automatically exploitable; check package origin and expected behavior.
- A writable configuration file may allow unauthorized changes; determine who needs write access.
- A log entry is evidence of an event, not necessarily proof of compromise.

## Hands-on practice
- Record your account identity and sudo permissions.
- List listening sockets and map each to a service where possible.
- Identify one configuration file and document its owner and mode without changing it.
- Hint: use `ss -tulpen` and `stat`.

## Common mistakes
- Running privilege-escalation scripts on machines without authorization.
- Changing ownership or permissions to silence an error.
- Treating all open ports or SUID files as exploitable.
- Leaving test credentials and accounts behind.

## Key takeaways
Security work starts with understanding intended behavior and collecting evidence. Use least privilege and make changes through a controlled process.

## Further practice
Combine this lesson with the filesystem audit and process/service modules.

## References
- [Linux kernel security documentation](https://docs.kernel.org/security/)
- [sudo documentation](https://www.sudo.ws/docs/)
