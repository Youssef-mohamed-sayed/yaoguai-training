# Lab: Processes, Services, and Secure Remote Access


## Lab objectives
Inspect processes and services, then connect to a Linux host you control using SSH.

## Part A: process and service inspection
```bash
ps -eo pid,ppid,user,stat,comm --sort=-%cpu | head
uptime
free -h
systemctl --type=service --state=running
journalctl -b -p warning --no-pager | tail -n 30
```
Record one process, its PID and owner, and one running service. Do not terminate an unfamiliar process.

## Part B: local SSH
On a disposable Linux VM, install and start the OpenSSH server using the correct package manager and service name for that distribution. Check `systemctl status ssh` or `sshd`, then inspect listening sockets with `ss -tlnp`.

From a client, connect to an account you control:
```bash
ssh learner@127.0.0.1
```
For a separate VM, use its lab IP and verify the host-key fingerprint through the VM console or another trusted channel.

## Part C: key authentication
Generate a key with `ssh-keygen -t ed25519`, install its public key for the test account, and connect in a second terminal. Keep the first working session open while testing. Never disable host-key verification to bypass a warning.

## Deliverable
A short operational note with process/service observations, SSH authentication method, host-key verification method, and troubleshooting performed.
