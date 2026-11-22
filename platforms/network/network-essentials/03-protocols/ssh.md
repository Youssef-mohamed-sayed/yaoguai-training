# SSH — Secure Shell

> Difficulty: Beginner

## What You Will Learn

- What SSH is and why it replaced Telnet
- What is visible (and not) in a capture
- Banners and Nmap results

## Why This Matters in Cybersecurity

SSH is the main remote-admin protocol on servers. Exposed SSH is a prime target for password guessing; it's a common finding in recon.

## 1. Introduction

**SSH** gives encrypted remote command-line access (and file transfer via SFTP/SCP).

| Property | Value |
|----------|-------|
| Layer | 7 |
| Port | 22 |
| Transport | TCP |

## 2. How It Works

```text
1. TCP handshake to port 22
2. Banners exchanged: SSH-2.0-OpenSSH_9.2p1 ...
3. Key exchange → encrypted channel
4. Server host key verified by client (first-use "fingerprint")
5. User authentication (password / public key)
6. Encrypted shell session
```
### Mini Task 1

What is the default SSH port? Is the session content readable in Wireshark?

<details>
<summary>Check Your Answer</summary>

22; no, only the banner and handshake metadata are visible.

</details>

## 3. Practical Example / Exercise

```bash
ssh student@192.168.56.20
```
`ssh` = client; `student` = account; `@192.168.56.20` = target host. Use only on lab machines. Verify the host key fingerprint prompt.

**Nmap:** `22/tcp open ssh OpenSSH 9.2p1 Debian`. **Wireshark:** filter `ssh` or `tcp.port == 22`.

## 4. Cybersecurity Perspective

- Brute-force/password-spray attempts against SSH are very common: use keys, disable root login, rate-limit.
- Old versions/protocols have had real vulnerabilities, but seeing a banner does **not** prove a vulnerability.
- SSH tunnelling can hide traffic; detect via unusual long-lived sessions.

## 5. Common Mistakes

Ignoring the host-key warning ("WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED"). It can indicate interception.

## 6. CTF Challenge

**Title:** Banner Grab
**Difficulty:** Easy
**Scenario:** A lab Nmap scan shows `22/tcp open ssh` and a banner `SSH-2.0-OpenSSH_9.2p1 Debian-2+deb12u3`.
**Objective:** Identify the software and version.
**Task:** Flag = software and version token from the banner.
**Flag format:** `FLAG{OpenSSH_x.yp1}`

<details>
<summary>Show Hints</summary>

- Hint 1: After `SSH-2.0-` comes the software identification.

</details>

<details>
<summary>Show Solution</summary>

Flag: `FLAG{OpenSSH_9.2p1}`. (Knowing the version is discovery; checking it against vulnerability data is a separate step.)

</details>

## Summary

SSH = encrypted remote access on TCP 22.

## What To Learn Next

[ARP (protocol analysis)](arp.md)
