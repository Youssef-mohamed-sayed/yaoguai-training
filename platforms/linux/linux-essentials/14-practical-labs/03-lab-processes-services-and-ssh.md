# Lab: Processes, Services, and Secure Remote Access


## Lab objectives
Inspect processes and services on a live system, then set up key-based SSH access to a host you control, verifying host identity the right way.

## Safety and prerequisites
A disposable Linux VM with a snapshot taken. Part C assumes module 11. Never disable host-key verification to bypass a warning, and keep one working session open whenever you change SSH settings.

## Part A: process and service inspection
```bash
ps -eo pid,ppid,user,stat,comm --sort=-%cpu | head
uptime
free -h
systemctl --type=service --state=running
journalctl -b -p warning --no-pager | tail -n 30
```

Record one process (PID, PPID, owner, state) and one running service (unit name, enabled state, main PID from `systemctl status`). Do not terminate any process you cannot name.

**Validation.**

**Check 1.** Which process is PID 1 on your system, and what does that tell you about the init system?

<details>
<summary>Show answer</summary>

```bash
ps -p 1 -o pid=,comm=
```

`systemd` on mainstream distributions. Anything else (`init`, a shell in a container) tells you `systemctl` may not manage services here.
</details>

**Check 2.** From the `ss -tlnp` output in Part B, which address is SSH bound to, and what would `127.0.0.1:22` versus `0.0.0.0:22` each mean?

<details>
<summary>Show answer</summary>

`127.0.0.1:22` accepts only connections from the machine itself; `0.0.0.0:22` accepts them on every network interface, including from the network. A fresh server offering `0.0.0.0:22` to the world should be a deliberate, hardened choice.
</details>

## Part B: local SSH
Install and start the OpenSSH server with the correct package manager and unit name for your distribution:

```bash
sudo apt update && sudo apt install -y openssh-server   # Debian/Ubuntu: unit "ssh"
sudo systemctl enable --now ssh
systemctl status ssh --no-pager
ss -tlnp | grep ':22'
```

Connect to an account you control:

```bash
ssh "$USER"@127.0.0.1
```

Read the first-connection host-key prompt before accepting it. For a separate VM, use its lab IP and verify the fingerprint through the VM console or another trusted channel. Then `exit`.

## Part C: key authentication
```bash
ssh-keygen -t ed25519 -C "lab" -f ~/.ssh/id_lab
ssh-copy-id -i ~/.ssh/id_lab.pub "$USER"@127.0.0.1
ssh -i ~/.ssh/id_lab "$USER"@127.0.0.1 'echo key login works'
```

Keep the first working session open while testing key login from a second terminal.

**Validation.**

**Check 3.** Where did the server's host key get recorded, and how could you confirm the fingerprint independently?

<details>
<summary>Show answer</summary>

In the client's `~/.ssh/known_hosts`. Independently: on the server run `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` and compare with the fingerprint the client showed at first connection.
</details>

**Check 4.** What two lines prove passwordless key auth succeeded (not password fallback)?

<details>
<summary>Show answer</summary>

From `ssh -v`: `debug1: Offering public key` followed by `debug1: Authentication succeeded (publickey)`. If it says `password` or prompts for one, the key was not accepted: check `authorized_keys` content, `~/.ssh` mode `700`, and key mode `600` on both ends.
</details>

## Troubleshooting reference
| Symptom | First thing to check |
|---|---|
| `Connection refused` | `systemctl status ssh` and `ss -tlnp` on the server |
| `Permission denied (publickey)` | key installed for the *right account*, file permissions on both sides |
| Prompts for password after key setup | `ssh -v` to see which keys were offered and rejected |

## Deliverable
A short operational note: process/service observations from Part A, the SSH authentication method you ended with, how you verified the host key, and any troubleshooting you performed.

## Common mistakes
- Installing only the client package and wondering why nothing listens on port 22.
- Testing key login by closing the only working session first.
- Accepting host-key prompts without reading them.
