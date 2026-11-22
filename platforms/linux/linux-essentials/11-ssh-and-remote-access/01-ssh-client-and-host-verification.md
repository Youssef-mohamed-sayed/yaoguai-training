# SSH Connections and Host-Key Verification


## Learning objectives
- Connect to a remote host using SSH.
- Specify usernames, ports, and options.
- Explain host keys and first-connection verification.

## Introduction
SSH (Secure Shell) provides encrypted remote login and command execution. It uses a client-server model: the client connects to an SSH server, commonly on TCP port 22, though servers can use another port.

## Connection syntax
```bash
ssh username@hostname
ssh -p 2222 username@192.0.2.20
ssh -v username@localhost
ssh -o ConnectTimeout=5 username@host.example
```
`-p` selects the port; `-v` prints diagnostic detail; `-o` sets a client option. Documentation address `192.0.2.0/24` is reserved for examples and is not a real target.

### Host-key verification
The server presents a host key to identify itself. SSH records accepted keys in `~/.ssh/known_hosts`. If the key changes unexpectedly, SSH warns because the server may have been rebuilt, its key rotated, DNS may point elsewhere, or a man-in-the-middle attack may be occurring.

Do not blindly disable verification with `StrictHostKeyChecking=no` or delete a warning without checking through a trusted channel. Confirm the fingerprint with the system owner or administrator.

## Configuration
Client configuration is commonly stored in `~/.ssh/config`:
```sshconfig
Host lab-vm
    HostName 192.0.2.20
    User learner
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```
Protect the file from unintended modification; `chmod 600 ~/.ssh/config` is a common setting.

## Troubleshooting
- `Connection timed out`: routing, firewall, address, or host availability.
- `Connection refused`: host reachable but no listener at that port, or actively rejected.
- `Permission denied`: username, authentication method, account policy, or key permissions.
- Host-key warning: verify identity before proceeding.

## Hands-on practice
- Connect to `localhost` if an SSH server is installed and running.
- Use `ssh -v` to observe negotiation stages.
- Configure a `Host` alias for a lab system you control.
- Hint: client and server packages are separate on some distributions.

## Common mistakes
- Using the wrong port option (`-p` for client; server configuration has its own syntax).
- Confusing server host keys with your personal user keys.
- Disabling host-key checks to make a warning disappear.
- Exposing an SSH server publicly without appropriate hardening.

## Key takeaways
SSH encrypts transport and authenticates endpoints. Host-key verification is an important defense against impersonation.

## Further practice
Read `man ssh`, `man ssh_config`, and `man sshd_config`.

## References
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
- [OpenSSH portable](https://www.openssh.com/)
