# SSH — Secure Shell

> Difficulty: Beginner

## What You Will Learn

- What SSH provides: encryption, integrity, authentication
- How a session is established at a high level
- Host keys, known_hosts, and key-based login
- Using SSH safely for remote administration

## Why This Matters in Cybersecurity

SSH is how nearly every Linux server is administered - which makes it both the tool defenders rely on and a prime target for brute-force attacks and key theft. Analysts see SSH in logs daily; understanding it is non-negotiable.

## 1. Introduction

**SSH** (Secure Shell) gives encrypted remote login and command execution. It replaced Telnet, which sent everything - passwords included - in cleartext. SSH also carries file transfer (SFTP, `scp`) and tunneling (port forwarding).

| Property | Value |
|----------|-------|
| Layer | 7 |
| Port | 22 |
| Transport | TCP |

## 2. How a Session Starts

At a high level, three things happen when you run `ssh user@server`:

1. **Key exchange** (Diffie-Hellman family): client and server agree on a shared session key over the open network, without ever sending it. All later traffic is encrypted with that key.
2. **Server authentication:** the server proves its identity with its **host key**. Your client checks it against `~/.ssh/known_hosts`. A changed host key triggers the loud "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED" - treat it as a possible man-in-the-middle until verified.
3. **User authentication:** password, or better, a **key pair**: the private key stays on your machine, the public key sits in the server's `~/.ssh/authorized_keys`, and the server challenges you to prove you hold the private half.

```text
$ ssh admin@192.168.56.20
The authenticity of host '192.168.56.20' can't be established.
ED25519 key fingerprint is SHA256:7kQf...
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

### Mini Task 1

What two things does SSH authenticate before a session is usable?

<details>
<summary>Check Your Answer</summary>

The server to the client (host key), and the user to the server (password or key pair).

</details>

### Mini Task 2

Why is a changed host key warning worth investigating instead of clicking through?

<details>
<summary>Check Your Answer</summary>

Because it means the server no longer proves the identity your client recorded - either the server was rebuilt/rekeyed (benign) or someone is intercepting the connection (attack). Verify the new fingerprint out-of-band before accepting.

</details>

## 3. Practical Example / Exercise

In an authorised lab:

```bash
ssh-keygen -t ed25519 -C "lab key"     # generate a key pair
ssh-copy-id user@192.168.56.20         # install your public key
ssh user@192.168.56.20                 # passwordless login
```

**Exercise.** After setting up key login, run `ssh -v user@host` and find the lines where the client offers the public key and the server accepts it. Which authentication method does the verbose log name?

<details>
<summary>Check Your Answer</summary>

Look for `debug1: Offering public key` and `debug1: Authentication succeeded (publickey)`. The method is `publickey` - password authentication is skipped entirely once the key works.

</details>

**Nmap:** `22/tcp open ssh OpenSSH 9.2p1` - the version banner matters for vulnerability lookup. In Wireshark, SSH after the banner is encrypted: you can see *that* a session exists, not what it says.

## 4. Cybersecurity Perspective

- **Brute force:** internet-facing port 22 gets hammered constantly. Defenses: key-only login (`PasswordAuthentication no`), rate limiting (fail2ban), non-default users with sudo, and ` PermitRootLogin no`.
- **Key hygiene:** private keys are as sensitive as passwords; they belong encrypted with a passphrase and never in git or chat.
- **Tunneling cuts both ways:** `ssh -L/-R/-D` forwards ports - legitimately for admin access, and abused by attackers to pivot through a compromised host.
- In captures, SSH banners (`SSH-2.0-OpenSSH_9.2`) are visible; everything after the key exchange is ciphertext.

## 5. Common Mistakes

Reusing one key pair everywhere (one theft unlocks everything), ignoring host-key warnings, and leaving password login enabled on internet-facing servers.

## 6. CTF Challenge

**Title:** The Wrong Door
**Difficulty:** Easy
**Scenario:** An authorised lab auth log shows:
```text
Oct 10 03:14:15 srv sshd[812]: Failed password for root from 203.0.113.7 port 51122 ssh2
Oct 10 03:14:18 srv sshd[812]: Failed password for root from 203.0.113.7 port 51124 ssh2
Oct 10 03:14:21 srv sshd[812]: Failed password for root from 203.0.113.7 port 51126 ssh2
```
**Objective:** Identify the attack pattern.
**Task:** Flag = the two-word name of this attack, lowercase with a dash.
**Flag format:** `FLAG{attack-name}`

<details>
<summary>Show Hints</summary>

- Hint 1: Same account, same source, many rapid failures.
- Hint 2: The defense section above names it.

</details>

<details>
<summary>Show Solution</summary>

Flag: `FLAG{brute-force}`. Repeated password attempts against one account from one IP is the brute-force signature; key-only login and fail2ban are the standard counters.

</details>

## Summary

SSH: TCP 22, encrypted remote access. Key exchange builds the session key, host keys authenticate the server, key pairs (better than passwords) authenticate the user. Watch for brute force; disable password login where possible.

## What To Learn Next

[ICMP](icmp.md)
