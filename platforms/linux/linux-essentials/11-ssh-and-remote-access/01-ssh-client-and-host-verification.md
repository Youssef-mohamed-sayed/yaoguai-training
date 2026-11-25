# SSH Connections and Host-Key Verification


## Learning objectives
- Connect to a remote host with SSH, specifying user, port, and options.
- Explain host keys and handle first-connection and changed-key prompts correctly.
- Read the common error messages and know what each is really telling you.

## Introduction
SSH (Secure Shell) provides encrypted remote login and command execution. A client connects to an SSH server, conventionally on TCP port 22. Nearly all remote Linux administration happens over SSH, and nearly all of it authenticates two ways: the server proves its identity to you (host key), and you prove yours to it (password or, better, a user key, covered in the next lesson).

## Connection syntax
```bash
ssh username@hostname
ssh -p 2222 username@192.0.2.20
ssh -v username@localhost
ssh -o ConnectTimeout=5 username@host.example
```

- `-p` selects the port (client option; the server sets its port in its own configuration).
- `-v` prints negotiation detail; add more v's (`-vvv`) for deeper debugging.
- `-o` sets any client option inline.

(`192.0.2.0/24` is a documentation range reserved for examples, not a real target.)

## Host-key verification: the prompt that protects you
On first connection, the server presents its **host key**, and the client asks you to confirm its fingerprint:

```text
The authenticity of host '192.0.2.20' can't be established.
ED25519 key fingerprint is SHA256:AbCdEf123...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Accept, and the key is recorded in `~/.ssh/known_hosts`. On every later connection the client checks the presented key against that record **silently**. The design assumes the first check is done carefully (ideally against a fingerprint you received through a trusted channel: the console, the cloud dashboard, the administrator).

If the key ever **changes**, SSH stops you with a loud warning. The innocent explanations: the server was rebuilt, its keys were rotated, or DNS now points elsewhere. The hostile explanation: someone is impersonating the server (a man-in-the-middle attack). You cannot tell which from the warning alone, so verify through a trusted channel before proceeding.

> [!WARNING]
> Never silence these warnings with `StrictHostKeyChecking=no`, and never just delete the `known_hosts` line and reconnect. Both train you to click through the one defense against server impersonation.

## Client configuration
Frequent connections belong in `~/.ssh/config`:

```sshconfig
Host lab-vm
    HostName 192.0.2.20
    User learner
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

Now `ssh lab-vm` expands the whole block. Protect the file: `chmod 600 ~/.ssh/config`.

## Troubleshooting: the four classic failures
| Message | What it actually means |
|---|---|
| `Connection timed out` | Packets are dying on the way: wrong address, routing, or a firewall silently dropping them. |
| `Connection refused` | The host is reachable, but nothing listens on that port (server down, wrong port) or it actively rejected you. |
| `Permission denied (publickey...)` | You reached a working server; *authentication* failed: wrong user, wrong key, or key not authorized. |
| Host-key warning | Identity mismatch; verify before doing anything else. |

Read the message, name the layer (network, service, authentication, identity), and only then start changing things.

## Practice exercises
Try every task before opening its solution. You need a target you control: a lab VM with `openssh-server` installed, or `localhost`.

**Exercise 1.** Install and start an SSH server on a lab VM, then connect to it from the same machine via `localhost`.

<details>
<summary>Show a worked solution</summary>

Debian/Ubuntu:

```bash
sudo apt update && sudo apt install -y openssh-server
sudo systemctl enable --now ssh
ssh "$USER"@localhost
```

Say yes to the first-connection prompt after reading it, then `exit`. (Client and server are separate packages on many distributions; having `ssh` does not imply having `sshd`.)
</details>

**Exercise 2.** Reconnect with `ssh -v` and identify in the output: the protocol negotiation, the host key being checked against `known_hosts`, and the authentication method that succeeded.

<details>
<summary>Show a worked solution</summary>

```bash
ssh -v "$USER"@localhost true
```

Look for lines like `debug1: Remote protocol version 2.0`, `debug1: Host 'localhost' is known and matches the ED25519 host key`, and `debug1: Authentication succeeded (publickey)`. This one flag answers most "SSH is weird today" questions.
</details>

**Exercise 3.** Write a `~/.ssh/config` entry for a lab system so that `ssh lab` connects as user `learner` on port 2222, then verify the expansion without connecting.

<details>
<summary>Show a worked solution</summary>

```sshconfig
Host lab
    HostName 192.0.2.20
    User learner
    Port 2222
```

```bash
chmod 600 ~/.ssh/config
ssh -G lab | grep -E '^(hostname|user|port) '
```

`ssh -G` prints the fully resolved configuration for an alias: the safest way to test a config block.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** After rebuilding a server, every user gets a host-key warning. Is the warning wrong?

<details>
<summary>Show answer</summary>

No, it is working exactly as designed: the key changed. Because *you* know the rebuild happened, distribute the new fingerprint through a trusted channel so users can confirm it instead of guessing.
</details>

**Q2.** `ssh -p 2222` fails with "Connection refused" but a teammate connects fine from another machine. Name two likely causes.

<details>
<summary>Show answer</summary>

You are using the wrong port or wrong address (typo, stale notes), or a local firewall/security group blocks your source while allowing theirs. "Refused" means the network path works; something at the far end actively said no.
</details>

**Q3.** Why is accepting the first-connection fingerprint sight-unseen called "trust on first use", and when is it acceptable?

<details>
<summary>Show answer</summary>

Because you trust whatever key appeared first, with no independent check. It is acceptable only when you have out-of-band knowledge (you just built the VM yourself, you read the fingerprint from the console); for anything reachable by others, compare the fingerprint through a trusted channel.
</details>

## Common mistakes
- Mixing up the client port option (`-p`) with server configuration.
- Confusing the server's host keys with your personal user keys.
- Disabling host-key checks to make a warning disappear.
- Exposing an SSH server to the internet before hardening it (key-only auth, no root login, rate limiting).

## Key takeaways
SSH encrypts transport and authenticates both endpoints. The host-key prompt is a security control, not a nuisance; and every error message names a layer: network, service, authentication, or identity.

## Further practice
Read `man ssh` and `man ssh_config`, then set up key-based authentication in the next lesson and disable password login on your lab VM.

## References
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
- [OpenSSH portable](https://www.openssh.com/)
