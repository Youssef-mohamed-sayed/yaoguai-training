# SSH Keys, ssh-agent, SCP, and SFTP


## Learning objectives
- Generate and use an SSH key pair, and explain the public/private split precisely.
- Load keys into ssh-agent so passphrases stop interrupting your day.
- Transfer files with SCP and SFTP, and apply the secure-server checklist.

## Key authentication
A key pair is two mathematically linked files:

- The **private key** stays secret on your client machine, protected by its permissions and (ideally) a passphrase. Anyone who copies it *becomes* you.
- The **public key** is placed on servers, in the remote account's `~/.ssh/authorized_keys`. It can be shared freely; deriving the private half from it is computationally infeasible.

During authentication the server issues a challenge that only the private key can answer; the private key itself never crosses the network. That is the whole trick, and it is why key authentication beats passwords: nothing reusable is ever transmitted, and guessing is out of reach.

Generate a modern Ed25519 pair:

```bash
ssh-keygen -t ed25519 -C "learner@lab"
```

Output:

```text
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/learner/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase):
```

Use a passphrase. It encrypts the private key at rest, so a stolen laptop or leaked backup does not hand over your identity. The private key lands at `~/.ssh/id_ed25519` (mode `600`), the public half at `~/.ssh/id_ed25519.pub`.

Deploy the public key to a server you administer:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub learner@192.0.2.20
```

`ssh-copy-id` appends to `authorized_keys` with the right permissions (not available on every platform; appending manually works if done carefully: **append**, never overwrite, or you lock out every previously installed key, including possibly your own).

## ssh-agent: type the passphrase once
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l      # list loaded identities
ssh-add -D      # remove all when done
```

The agent holds the decrypted key in memory for your session, so each SSH connection authenticates without re-asking. Many desktop sessions start an agent for you; `ssh-add -l` tells you whether one is running and what it holds.

## File transfer
```bash
scp report.txt learner@192.0.2.20:/home/learner/        # upload
scp learner@192.0.2.20:/var/log/example.log ./          # download
scp -r project/ learner@192.0.2.20:/home/learner/       # directories
sftp learner@192.0.2.20                                 # interactive session
```

SCP is a copy command over SSH: same syntax instincts as `cp`, with `host:path` for the remote side. SFTP is an interactive transfer shell (`get`, `put`, `ls`, `cd`, `exit`) for browsing before moving files. Both ride the same encrypted channel and the same keys as your logins; never fall back to plain FTP.

## Secure server principles
When the server is yours to harden:

- Prefer key-based authentication; keep OpenSSH updated.
- Restrict who can even reach the port (firewall rules, security groups).
- Disable password authentication **only after** confirming key login works in a second session and you have a recovery path.
- Disable direct root login (`PermitRootLogin no`).
- Keep host-key checking enabled everywhere.

Server options live in `/etc/ssh/sshd_config` (plus included files; defaults vary by distribution). Validate with `sudo sshd -t` before restarting, and keep one working session open while you test from a new one.

## Practice exercises
Do these against a lab VM you control. Try every task before opening its solution.

**Exercise 1.** Generate an Ed25519 key pair with a passphrase for a disposable lab identity, then inspect the resulting files' permissions.

<details>
<summary>Show a worked solution</summary>

```bash
ssh-keygen -t ed25519 -C "lab-practice" -f ~/.ssh/id_lab
ls -l ~/.ssh/id_lab ~/.ssh/id_lab.pub
```

Output:

```text
-rw------- 1 learner learner  464 Nov 25 04:30 /home/learner/.ssh/id_lab
-rw-r--r-- 1 learner learner  100 Nov 25 04:30 /home/learner/.ssh/id_lab.pub
```

Private `600`, public `644`: exactly as it should be.
</details>

**Exercise 2.** Install the public key on your lab VM and log in with it, explicitly selecting the key.

<details>
<summary>Show a worked solution</summary>

```bash
ssh-copy-id -i ~/.ssh/id_lab.pub learner@192.0.2.20
ssh -i ~/.ssh/id_lab learner@192.0.2.20 'echo key login works'
```

The last command runs one remote command and returns, a fast proof that key authentication succeeded without an interactive session.
</details>

**Exercise 3.** Load the key into an agent, then connect twice and note what changed the second time.

<details>
<summary>Show a worked solution</summary>

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_lab          # passphrase asked once, here
ssh learner@192.0.2.20 true    # no prompt
ssh learner@192.0.2.20 true    # still no prompt
ssh-add -l
```

The agent answered both connections; the passphrase was needed only at `ssh-add`.
</details>

**Exercise 4.** Create a file locally, upload it to the lab VM's home directory, download it back under a different name, and verify the round trip.

<details>
<summary>Show a worked solution</summary>

```bash
printf 'round trip\n' > ~/linux-lab/payload.txt
scp ~/linux-lab/payload.txt learner@192.0.2.20:/home/learner/
scp learner@192.0.2.20:/home/learner/payload.txt ~/linux-lab/payload-back.txt
diff ~/linux-lab/payload.txt ~/linux-lab/payload-back.txt && echo identical
```
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Which half of the key pair goes on the server, and in what file?

<details>
<summary>Show answer</summary>

The **public** key, appended to that account's `~/.ssh/authorized_keys`. The private key never leaves your client.
</details>

**Q2.** If your private key is stolen but has a strong passphrase, what does the attacker actually have?

<details>
<summary>Show answer</summary>

An encrypted file they cannot use without also cracking the passphrase. That gap is your window to remove the public key from every server's `authorized_keys` and rotate the pair.
</details>

**Q3.** Why append to `authorized_keys` instead of replacing it?

<details>
<summary>Show answer</summary>

Every line is a key someone relies on, possibly including the only key that still works. Overwriting the file can revoke all of them at once, including yours.
</details>

## Common mistakes
- Copying the private key to a server "for convenience".
- Leaving private keys at mode `644`; SSH will refuse them, and for good reason.
- Overwriting `authorized_keys` instead of appending.
- Disabling password login before proving key login works from a second session.
- Skipping the passphrase on a laptop key.

## Key takeaways
Private keys stay private and passphrase-protected; public keys go in `authorized_keys`. The agent remembers passphrases for a session, SCP/SFTP move files over the same encrypted channel, and server hardening is a checklist, not a vibe.

## Further practice
Read `man ssh-keygen`, `man ssh-agent`, and `man sftp`, then disable password authentication on your lab VM and confirm you can still get in, and back out if you cannot.

## References
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
