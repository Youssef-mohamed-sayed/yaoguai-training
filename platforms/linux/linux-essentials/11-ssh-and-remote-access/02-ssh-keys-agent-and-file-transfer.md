# SSH Keys, ssh-agent, SCP, and SFTP


## Learning objectives
- Generate and use an SSH key pair.
- Explain public versus private keys.
- Transfer files with SCP and SFTP.

## Key authentication
A key pair has a **private key** kept secret on your client and a **public key** placed in the remote account's `~/.ssh/authorized_keys`. During authentication, the client proves possession of the private key without sending it to the server.

Generate a modern Ed25519 key:
```bash
ssh-keygen -t ed25519 -C "learner@lab"
```
Use a passphrase where practical. The private key is commonly stored under `~/.ssh/id_ed25519`; the public key ends in `.pub`. Never share the private key.

Copy the public key to a server you administer:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub learner@192.0.2.20
```
`ssh-copy-id` may not be installed on every platform. Alternatively, append the public key through a secure, verified setup process.

### ssh-agent
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l
```
The agent holds decrypted key material in memory for a session. Protect your account and remove keys from the agent when no longer needed (`ssh-add -D` removes all identities from the agent).

### File transfer
```bash
scp report.txt learner@192.0.2.20:/home/learner/
scp learner@192.0.2.20:/var/log/example.log ./example.log
sftp learner@192.0.2.20
```
SCP copies files over SSH. SFTP provides an interactive file-transfer protocol; common commands include `get`, `put`, `ls`, and `exit`.

## Secure server principles
- Prefer key-based authentication and strong account controls.
- Keep OpenSSH updated.
- Restrict access using firewall rules and account policy.
- Disable password authentication only after confirming key access and recovery.
- Avoid direct root login where practical.
- Keep host-key checking enabled.

Server options belong in `/etc/ssh/sshd_config` or included configuration files, and exact defaults vary. Validate changes and keep console access before restarting SSH.

## Hands-on practice
- Generate a key pair for a disposable lab account.
- Inspect permissions with `ls -l ~/.ssh`.
- Transfer a harmless text file to a host you control using SCP or SFTP.
- Hint: private key files should not be readable by other users.

## Common mistakes
- Copying the private key to the server.
- Setting a private key to mode `644`.
- Overwriting `authorized_keys` instead of appending a new key.
- Disabling password login before testing key login in a second session.

## Key takeaways
Keep private keys private, verify host identity, and use SSH file-transfer tools rather than insecure legacy protocols.

## Further practice
Read `man ssh-keygen`, `man ssh-agent`, `man scp`, and `man sftp`.

## References
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
