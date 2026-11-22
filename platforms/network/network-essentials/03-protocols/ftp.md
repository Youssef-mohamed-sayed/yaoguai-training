# FTP — File Transfer Protocol

> Difficulty: Beginner

## What You Will Learn

- How FTP transfers files
- Why it is insecure
- Seeing credentials in a capture

## Why This Matters in Cybersecurity

FTP is a classic example of cleartext protocols exposing credentials, and a frequent finding in scans and CTFs.

## 1. Introduction

**FTP** moves files between client and server.

| Property | Value |
|----------|-------|
| Layer | 7 |
| Ports | 21 (control), 20 (active-mode data) or high ports (passive) |
| Transport | TCP |

## 2. How It Works

Two connections: a **control** channel (commands) and a **data** channel (file/listing).

```text
S: 220 Welcome to FTP
C: USER admin
S: 331 Password required
C: PASS Summer2024!
S: 230 Login successful
C: LIST
S: 150 Here comes the directory listing
```
Reply codes: 2xx success, 3xx need more info, 4xx temporary failure, 5xx error.

### Mini Task 1

What does 230 mean? What does `USER` send?

<details>
<summary>Check Your Answer</summary>

Login successful; the username.

</details>

## 3. Practical Example / Exercise

In an authorised lab with an FTP server: `ftp 192.168.56.20`. Capture with Wireshark (`tcp.port == 21`) and right-click → Follow TCP Stream to see the commands.

**Nmap:** `21/tcp open ftp vsftpd 3.0.5`. Check Nmap script `ftp-anon` (anonymous login) only on authorised targets.

## 4. Cybersecurity Perspective

- Credentials and data are **cleartext**.
- Anonymous FTP may expose sensitive files.
- Alternatives: SFTP (over SSH, port 22), FTPS (FTP over TLS).
- Passive-mode data ports complicate firewalls.

## 5. Common Mistakes

Confusing SFTP with FTPS; they are different protocols.

## 6. CTF Challenge

**Title:** Plain Sight
**Difficulty:** Easy
**Scenario:** From an authorised lab capture:
```text
C: USER backup
S: 331 Password required for backup
C: PASS Winter#42
S: 230 Login successful
```
**Objective:** Recover the credentials.
**Task:** Flag = username and password joined by underscore.
**Flag format:** `FLAG{user_password}`

<details>
<summary>Show Hints</summary>

- Hint 1: Look at USER and PASS commands.

</details>

<details>
<summary>Show Solution</summary>

Flag: `FLAG{backup_Winter#42}`. Lesson: FTP exposes credentials in plain text; use SFTP/FTPS.

</details>

## Summary

FTP: TCP 21, two channels, cleartext.

## What To Learn Next

[SSH](ssh.md)
