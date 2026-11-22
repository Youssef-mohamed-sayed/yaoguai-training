# Introduction to Nmap

> Difficulty: Beginner

## What You Will Learn

- What Nmap is and why professionals use it
- Reconnaissance vocabulary
- The scanning workflow
- **Discovery ≠ vulnerability**

## Why This Matters in Cybersecurity

You can't defend or assess what you don't know exists. Nmap builds the **inventory and attack-surface map** that every later step depends on.

## 1. Introduction

**Nmap** is a free tool that sends crafted packets to targets and analyses the replies.

| Term | Meaning |
|------|---------|
| Network reconnaissance | Gathering information about a network/target |
| Host discovery | Finding which IPs have live devices |
| Port scanning | Finding which ports respond on a host |
| Service detection | Identifying the service behind an open port |
| Version detection | Identifying the product and version of that service |
| Attack surface | Everything reachable that could be attacked |

> Analogy: Walking around a building: first find which buildings have people (hosts), then count the doors (ports), then read the signs on the doors (services/versions).

## 2. The Workflow

```text
Target
   ↓
Host discovery
   ↓
Port scanning
   ↓
Service detection
   ↓
Version detection
   ↓
Attack surface
   ↓
Further enumeration
```

### Mini Task 1

Put in order: version detection, host discovery, port scanning.

<details>
<summary>Check Your Answer</summary>

Host discovery → port scanning → version detection.

</details>

## 3. Discovery vs Vulnerability

Finding

```text
22/tcp   SSH
80/tcp   HTTP
443/tcp  HTTPS
3306/tcp MySQL
```

only tells you **what is reachable**. It does **not** say anything is vulnerable.

| Statement | True? |
|-----------|-------|
| "Port 80 is open, so the server is hackable." | ❌ |
| "Port 80 is open, so a web service is reachable and worth examining." | ✅ |
| "A host replied to ping, so it is exploitable." | ❌ |

Vulnerability requires a **flaw** (in the version, configuration, or logic) that you have **verified**. Discovery tells you where to look.

### Mini Task 2

Does `3306/tcp open mysql` prove the database can be broken into? What would you do next?

<details>
<summary>Check Your Answer</summary>

No. Next: confirm the version, check whether it should be network-exposed, test authentication policy (within authorisation), and compare with advisories.

</details>

## 4. Safe Practice

- Know your scope. Write it down.
- Start light. Aggressive scans can crash fragile devices.
- Save output (`-oN scan.txt`) for evidence and reporting.

## 5. Cybersecurity Perspective

Used by pentesters (scoping), vulnerability assessors (inventory), blue teams (exposure checks), CTF players (first step), and attackers (which is why you should expect to be scanned).

## 6. Common Mistakes

- Scanning targets you do not own.
- Treating output as a vulnerability report.
- Trusting the port number as proof of service.

## 7. CTF Challenge

**Title:** Discovery or Vulnerability?
**Difficulty:** Easy
**Scenario:** Statements: (1) "443/tcp is open." (2) "Apache 2.4.x on this host has CVE-xxxx and the vulnerable module is enabled (verified in lab)." (3) "Host 192.168.56.20 replied to a scan."
**Objective:** Which statements are *discoveries* only?
**Task:** Flag = numbers of discovery-only statements ascending, no spaces.
**Flag format:** `FLAG{n,n}`

<details>
<summary>Show Hints</summary>

- Hint 1: A vulnerability claim needs a flaw and verification.

</details>

<details>
<summary>Show Solution</summary>

(1) and (3) only show reachability. (2) is a verified-vulnerability claim.

Flag: `FLAG{1,3}`

</details>

## Summary

Nmap maps what exists and listens; interpretation turns that into leads, not verdicts.

## What To Learn Next

[Host Discovery](host-discovery.md)
