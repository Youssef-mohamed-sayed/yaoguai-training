# FTP — File Transfer Protocol

> Difficulty: Beginner

## What You Will Learn

- How FTP transfers files over two separate connections
- Active vs passive mode and why firewalls care
- Why FTP is insecure and what replaced it
- Seeing credentials in a capture

## Why This Matters in Cybersecurity

FTP is a classic example of cleartext protocols exposing credentials, and a frequent finding in scans and CTFs. Misconfigured anonymous FTP still leaks files on real assessments, and the two-channel design is the standard interview question about why protocols and firewalls clash.

## 1. Introduction

**FTP** moves files between client and server. It is one of the oldest application protocols still found on networks (1971 origins), which explains both its quirks and why it appears so often in legacy systems.

| Property | Value |
|----------|-------|
| Layer | 7 |
| Ports | 21 (control), 20 (active-mode data) or high ports (passive) |
| Transport | TCP |

## 2. How It Works

FTP uses **two TCP connections**: a control channel (port 21, stays open for the session, carries commands and replies) and a data channel (opened per transfer, carries files and listings).

```text
S: 220 Welcome to FTP
C: USER admin
S: 331 Password required
C: PASS Summer2024!
S: 230 Login successful
C: PASV
S: 227 Entering Passive Mode (192,168,56,20,195,80)
C: LIST
S: 150 Here comes the directory listing
S: 226 Directory send OK
```

The `227` reply encodes the IP and port for the data connection: the last two numbers are port-high and port-low bytes, so 195×256 + 80 = port 50000.

**Active vs passive mode:**

- **Active:** the client says `PORT` and the *server* connects back to the client from port 20. Client-side NAT and firewalls usually break this.
- **Passive:** the client asks `PASV`, the server opens a high port, and the *client* makes both connections. This is the default today because outbound connections pass NAT easily.

Reply codes: 2xx success, 3xx need more info, 4xx temporary failure, 5xx error. The first digit is enough for most reading.

### Mini Task 1

What does 230 mean? What does `USER` send?

<details>
<summary>Check Your Answer</summary>

Login successful; the username.

</details>

### Mini Task 2

A server replies `227 Entering Passive Mode (10,0,0,5,19,136)`. Which IP and port should the client connect to for the data channel?

<details>
<summary>Check Your Answer</summary>

IP 10.0.0.5, port 19×256 + 136 = 5000.

</details>

## 3. Practical Example / Exercise

In an authorised lab with an FTP server: `ftp 192.168.56.20`. Capture with Wireshark (`tcp.port == 21`) and right-click → Follow TCP Stream to see the commands.

**Exercise.** Predict what you will see in the capture before you run it: which packets contain the password, and will `LIST` output travel over port 21?

<details>
<summary>Check Your Answer</summary>

The password appears in the `PASS` command on the control channel (port 21), readable as plain text. The `LIST` output travels over the separate data channel - in passive mode, a high port chosen by the server - so filtering only port 21 shows the commands but not the file data.

</details>

**Nmap:** `21/tcp open ftp vsftpd 3.0.5`. Check Nmap script `ftp-anon` (anonymous login) only on authorised targets.

## 4. Cybersecurity Perspective

- Credentials and data are **cleartext** - anyone on the path can read them, as the CTF below shows.
- Anonymous FTP (`USER anonymous`) may expose sensitive files; check for it in assessments.
- The historic **FTP bounce** attack abused the `PORT` command to make a server connect to third parties - a reason modern servers restrict it.
- Alternatives: SFTP (over SSH, port 22), FTPS (FTP over TLS). Both encrypt; only SFTP is a single-connection protocol.
- Passive-mode data ports complicate firewall rules: the server must open a fixed high-port range and the firewall must allow it.

## 5. Common Mistakes

Confusing SFTP with FTPS; they are different protocols. SFTP is a subsystem of SSH with one encrypted channel; FTPS is classic FTP wrapped in TLS and still uses two channels. Also common: assuming port 21 carries files, when it only carries commands.

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

FTP: TCP 21 control + separate data channel, active (server calls back) vs passive (client connects twice), cleartext credentials, replaced by SFTP/FTPS.

## What To Learn Next

[SSH](ssh.md)
