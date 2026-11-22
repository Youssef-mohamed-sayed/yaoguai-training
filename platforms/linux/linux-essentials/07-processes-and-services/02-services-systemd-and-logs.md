# Services, systemd, and Logs


## Learning objectives
- Explain services and daemons.
- Inspect and manage systemd units.
- Read service logs with journalctl.

## Core concepts
A **daemon** is a background process that provides a service. **systemd** is a common init and service manager, but not universal. A **unit** describes a managed resource such as a service, socket, timer, or mount.

Stopping a service asks the service manager to stop the managed unit and may trigger configured cleanup. Killing a process sends a signal to one process and can bypass service-level management. A service manager may restart a killed process according to policy.

## Commands (systemd systems)
```bash
systemctl status ssh
systemctl is-active ssh
systemctl list-units --type=service --state=running
sudo systemctl start ssh
sudo systemctl stop ssh
sudo systemctl restart ssh
sudo systemctl enable ssh
sudo systemctl disable ssh
journalctl -u ssh --since today
journalctl -b -p warning
```
The service may be named `ssh` (Debian/Ubuntu) or `sshd` (many RPM-based systems). `enable` configures startup at boot; it does not necessarily start the service immediately. `start` starts it now; it does not necessarily enable it at boot.

`journalctl -u UNIT` filters by unit. `-b` selects the current boot; `-p warning` filters priority. Access to some logs may require elevated permissions or membership in a log-reading group.

## Hands-on practice
- Run `systemctl status` on a known service.
- Read recent logs for that unit.
- In a disposable VM, stop and start a noncritical service, then inspect its status.
- Do not stop networking or remote-access services on a remote machine unless you have console recovery.
- Hint: check the exact unit name with `systemctl list-unit-files`.

## Common mistakes
- Assuming systemd exists in every container or WSL instance.
- Confusing `enable` with `start`.
- Restarting SSH remotely without a recovery path.
- Reading logs without considering timestamps and boot selection.

## Key takeaways
Use `systemctl` for managed services and `journalctl` for the systemd journal. Verify unit names for your distribution.

## Further practice
Read `man systemctl`, `man journalctl`, and `man systemd`.

## References
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
- [journalctl(1)](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
