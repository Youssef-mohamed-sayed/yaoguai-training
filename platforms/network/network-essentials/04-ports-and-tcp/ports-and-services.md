# Ports and Services

> Difficulty: Beginner

## What You Will Learn

- What a port is and why ports exist
- Listening ports, services, sockets
- Open / closed / filtered
- Well-known ports

## Why This Matters in Cybersecurity

Every open port is a way in to a program. The list of open ports and services is the **attack surface** you map during reconnaissance.

## 1. Introduction

> Analogy: An IP address is a building; ports are numbered doors. Behind each door a different service works (web, mail, SSH).

A **port** is a 16-bit number (0–65535) at Layer 4 that identifies an endpoint for a program on a host. Without ports, a host could only run one network program.

Distinguish:

| Term | Meaning |
|------|---------|
| IP address | Host (interface) |
| MAC address | Local hardware address |
| Port | Number identifying a communication endpoint |
| Service | Program that provides functionality (e.g. nginx) |
| Protocol | Rules of the conversation (e.g. HTTP) |
| Socket | IP + port + transport, e.g. `192.168.1.10:80/tcp` |

## 2. Core Concept

Ranges: **0–1023** well-known, **1024–49151** registered, **49152–65535** dynamic/ephemeral.

| Port | Service | Transport |
|------|---------|-----------|
| 20/21 | FTP | TCP |
| 22 | SSH | TCP |
| 23 | Telnet | TCP |
| 25 | SMTP | TCP |
| 53 | DNS | UDP/TCP |
| 67/68 | DHCP | UDP |
| 80 | HTTP | TCP |
| 110 | POP3 | TCP |
| 123 | NTP | UDP |
| 143 | IMAP | TCP |
| 443 | HTTPS | TCP |
| 445 | SMB | TCP |
| 3306 | MySQL | TCP |
| 3389 | RDP | TCP |

### Mini Task 1

Fill in: SSH default port ____. HTTPS ____. DNS ____. MySQL ____.

<details>
<summary>Check Your Answer</summary>

22, 443, 53, 3306.

</details>

## 3. Client/Server Communication

The **server** *listens* on a well-known port. The **client** picks a random ephemeral source port.

```text
Client 192.168.1.50:51514  ───────►  Server 192.168.1.10:80
         (ephemeral)                      (listening)
```
A connection is uniquely identified by 4 values: src IP, src port, dst IP, dst port.

### Port States (as Nmap reports them)

| State | Meaning |
|-------|---------|
| open | A service is listening and accepting connections |
| closed | Reachable, but nothing listening (host answers with RST) |
| filtered | No clear answer; a firewall probably drops probes |
| open\|filtered | Nmap can't tell (common for UDP) |

### Mini Task 2

You probe a port and receive no response at all. Which state is most likely? You get a RST back. Which state?

<details>
<summary>Check Your Answer</summary>

filtered; closed.

</details>

## 4. Practical Example / Exercise

On your own machine:
```bash
ss -tuln           # Linux: listening TCP/UDP ports, numeric
netstat -ano       # Windows
```
`ss` = socket statistics; `-t` TCP, `-u` UDP, `-l` listening only, `-n` numbers not names. List your listening ports and name the service for each.

## 5. Cybersecurity Perspective

- Open port ≠ vulnerable service. It means *reachable*; vulnerability needs a flaw in that service/version/configuration.
- Services can run on non-standard ports (SSH on 2222), so don't trust port numbers alone: verify with service detection.
- Reduce attack surface: close unused ports, firewall the rest.

## 6. Common Mistakes

"Port 80 is always HTTP." It's only the convention.

## 7. CTF Challenge

**Title:** Name That Door
**Difficulty:** Easy
**Scenario:** A listening-ports list from a lab server:
```text
tcp LISTEN 0.0.0.0:22
tcp LISTEN 0.0.0.0:3306
tcp LISTEN 127.0.0.1:5432
udp UNCONN 0.0.0.0:53
```
**Objective:** Identify which ports are reachable from other machines.
**Task:** The `127.0.0.1` listener is only reachable locally. Flag = the numbers of the three externally-bound ports, ascending, comma-separated (no spaces).
**Flag format:** `FLAG{p1,p2,p3}`

<details>
<summary>Show Hints</summary>

- Hint 1: `0.0.0.0` means all interfaces; `127.0.0.1` means loopback only.

</details>

<details>
<summary>Show Solution</summary>

0.0.0.0:22, :3306 and :53 are externally bound. 5432 is local only.

Flag: `FLAG{22,53,3306}`

</details>

## Summary

Ports identify programs; services listen; Nmap reports open/closed/filtered.

## What To Learn Next

[TCP vs UDP](tcp-vs-udp.md)
