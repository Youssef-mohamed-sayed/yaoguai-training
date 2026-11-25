# Services, systemd, and Logs


## Learning objectives
- Explain what a service/daemon is and how a service manager supervises one.
- Inspect and manage systemd units without confusion between similar commands.
- Read service logs with `journalctl`, filtered to exactly what you need.

## Core concepts
A **daemon** is a background process that provides a service: `sshd` answers remote logins, `cron` runs scheduled jobs, a web server answers requests. Daemons are not meant to be started and babysat by hand; that is the job of the **init system / service manager**.

**systemd** is the service manager on most mainstream distributions (Ubuntu, Debian, Fedora, RHEL, Arch), but it is not universal: containers, WSL sessions, and some minimal systems run without it. Check before assuming.

A **unit** is systemd's description of a managed resource. The common types: `.service` (a daemon), `.timer` (scheduled activation, the modern cron), `.socket` (start on connection), `.mount`. You will mostly touch services and timers.

### Stop a service vs kill a process
Stopping a service (`systemctl stop`) asks the manager to shut the unit down through its configured procedure. Killing a process sends a signal to one PID and bypasses that management entirely, and the manager may simply restart the process according to its policy. For managed services, always talk to the manager.

## Commands (systemd systems)
```bash
systemctl status ssh
systemctl is-active ssh
systemctl list-units --type=service --state=running
systemctl list-unit-files --type=service
sudo systemctl start ssh
sudo systemctl stop ssh
sudo systemctl restart ssh
sudo systemctl reload ssh
sudo systemctl enable ssh
sudo systemctl disable ssh
```

The unit may be named `ssh` (Debian/Ubuntu) or `sshd` (RPM family); check with `list-unit-files` when in doubt.

The two pairs everyone confuses:

- `start`/`stop` control what is happening **now**.
- `enable`/`disable` control what happens **at boot** (by creating or removing a symlink). Enabling does not start; starting does not enable. `sudo systemctl enable --now ssh` does both.

`reload` asks a service to re-read its configuration without dropping connections, when the service supports it; `restart` is the heavier hammer.

Sample status output:

```text
$ systemctl status ssh
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (...; enabled; preset: enabled)
     Active: active (running) since Tue 2026-11-25 03:58:11 EET; 20min ago
   Main PID: 812 (sshd)
```

The leading `●` is green when active. `Loaded: ... enabled` means it starts at boot; `Active: active (running)` means it is up now.

## Reading the journal
```bash
journalctl -u ssh --since today
journalctl -u ssh -f                    # follow live
journalctl -b -p warning                # this boot, warnings and worse
journalctl --since "2026-11-25 03:00" --until "2026-11-25 04:00"
journalctl -b -1                        # the previous boot (crashes)
```

- `-u UNIT` filters to one service; `-f` follows like `tail -f`.
- `-b` selects a boot: current, or `-b -1` for the previous one, invaluable after an unexpected reboot.
- `-p warning` filters by priority (debug < info < notice < warning < err < crit < alert < emerg).
- Full journal access may require root or membership in the `systemd-journal` group.

> [!CAUTION]
> Never stop or restart `ssh`/`sshd` (or networking) on a remote machine unless you have an out-of-band console recovery path. Locking yourself out is one command away.

## Practice exercises
Do these in your own terminal; use a disposable VM for start/stop practice. Try every task before opening its solution.

**Exercise 1.** Pick a running service, read its full status, and answer from the output: is it enabled at boot, since when is it active, and what is its main PID?

<details>
<summary>Show a worked solution</summary>

```bash
systemctl list-units --type=service --state=running | head
systemctl status ssh
```

Read the `Loaded:` line for the boot setting (`enabled`/`disabled`), the `Active:` line for the start time, and `Main PID:` for the process ID.
</details>

**Exercise 2.** Find the exact unit name for your remote-access service on this system, then read today's logs for it.

<details>
<summary>Show a worked solution</summary>

```bash
systemctl list-unit-files | grep -i ssh
journalctl -u ssh --since today | tail -n 20
```

On Debian/Ubuntu the unit is `ssh.service`; on Fedora/RHEL it is `sshd.service`. Use whichever name the first command reveals.
</details>

**Exercise 3.** In a disposable VM: stop a noncritical service, confirm its state, start it again, and confirm. Then check whether it is enabled at boot.

<details>
<summary>Show a worked solution</summary>

```bash
sudo systemctl stop cron
systemctl is-active cron        # inactive
sudo systemctl start cron
systemctl is-active cron        # active
systemctl is-enabled cron       # enabled (boot setting, unchanged by start/stop)
```

Notice `is-enabled` did not change: runtime state and boot state are independent.
</details>

**Exercise 4.** Your machine rebooted unexpectedly last night. Write the command that shows errors and worse from the *previous* boot.

<details>
<summary>Show a worked solution</summary>

```bash
journalctl -b -1 -p err
```

`-b -1` selects the previous boot, `-p err` filters to priority err and above. Read the last lines of that boot first; the reason for the reboot is usually there.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** You ran `sudo systemctl enable myapp` and rebooted a week later, but the service was not running until then. Why was `enable` not enough at the time?

<details>
<summary>Show answer</summary>

`enable` only configures boot-time startup. To start it immediately you also need `start` (or `enable --now` in one step).
</details>

**Q2.** You killed a misbehaving service's process with `kill -9`, and thirty seconds later it was back with a new PID. What happened?

<details>
<summary>Show answer</summary>

The service manager supervises the unit and its restart policy (`Restart=on-failure` or similar) started a fresh process. To stop it for real, use `systemctl stop`; to debug, `systemctl status` and `journalctl -u`.
</details>

**Q3.** Why might `journalctl` show you nothing as a regular user while root sees plenty?

<details>
<summary>Show answer</summary>

Journal access is permission-controlled: system units' logs are visible to root and to members of the `systemd-journal` group (and sometimes `adm`). Add the user to the group or use sudo.
</details>

## Common mistakes
- Assuming systemd exists in every container or WSL instance.
- Confusing `enable` with `start`.
- Restarting SSH remotely without a recovery path.
- Reading logs without checking which boot and which timestamps you are looking at.
- Editing unit files in `/etc` when the change belongs in a drop-in (`systemctl edit`).

## Key takeaways
Services are daemons supervised by a manager; talk to the manager. `start/stop` is now, `enable/disable` is boot, and `journalctl -u UNIT --since` is how a service tells you its side of the story.

## Further practice
Read `man systemctl` and `man journalctl`, then write a throwaway unit file for a `sleep` command in your lab VM and manage it through its whole lifecycle.

## References
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
- [journalctl(1)](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
