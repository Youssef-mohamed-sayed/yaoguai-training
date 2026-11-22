# Service and Version Detection

> Difficulty: Intermediate

## What You Will Learn

- `-sV` service/version detection
- `-O` OS detection, `-A` aggressive mode
- What the VERSION column does and doesn't tell you

## Why This Matters in Cybersecurity

Knowing **what** is behind a port (product + version) lets you target enumeration and compare with security advisories.

## 1. The Command

```bash
nmap -sV 192.168.56.20
```
```text
nmap → program
-sV  → probe open ports to determine service name and version
192.168.56.20 → target
```
How it works: after finding open ports, Nmap sends probes and matches replies/banners against a signature database.

Sample:
```text
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u3 (protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.57 ((Debian))
2222/tcp open  ssh     OpenSSH 8.4p1 Debian 5 (protocol 2.0)
3306/tcp open  mysql   MySQL 8.0.36
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Interpretation

- Port 2222 runs **SSH**, even though the standard SSH port is 22 → services can use any port.
- Version strings are *reported by the service*; distros often backport security fixes without changing the visible version, so a version alone doesn't prove a vulnerability.
- `Service Info` is extra hints (OS, CPE).

### Mini Task 1

Which two ports run SSH? Does `Apache httpd 2.4.57` prove the server is vulnerable?

<details>
<summary>Check Your Answer</summary>

22 and 2222. No: it's a version identification; you'd need to check applicable advisories and configuration (and backported patches).

</details>

## 2. Other Options

| Option | Meaning |
|--------|---------|
| `-O` | OS detection (guess from TCP/IP stack behaviour); needs root |
| `-A` | Aggressive: `-sV -O` + default scripts + traceroute |
| `-sV --version-intensity 0-9` | How hard to probe |
| `-oN file.txt` | Save normal output |

```bash
sudo nmap -O 192.168.56.20
sudo nmap -A -p 22,80 192.168.56.20
```
OS output example:
```text
Running: Linux 5.X
OS details: Linux 5.4 - 5.15
```
OS detection is a **guess**; lists give probabilities.

⚠️ `-A` is noisy (runs scripts). Use it only where permitted.

### Mini Task 2 — Command completion

```bash
nmap ______ -p 80,443 192.168.56.20      # service/version on those ports
sudo nmap ______ 192.168.56.20           # OS detection
```

<details>
<summary>Check Your Answer</summary>

`-sV`; `-O`.

</details>

## 3. Practical Task (Lab)

Run `nmap -sV` against your lab VM and make a table: port | service | product/version | what you'd enumerate next (e.g. web content for HTTP, authentication policy for SSH).

## 4. Cybersecurity Perspective

- Service detection finds services on non-standard ports (evasion or misconfiguration).
- Versions guide further enumeration; check vendor advisories and CVE databases and *verify* before claiming a vulnerability.
- Banners can be hidden or faked; absence of a version isn't proof of safety.

## 5. Common Mistakes

- Saying "OpenSSH 8.4 → vulnerable" without checking context and patches.
- Believing `-O` results as fact.

## 6. CTF Challenge

**Title:** Hidden SSH
**Difficulty:** Easy
**Scenario:** Use the sample `-sV` output above. A policy says SSH must only be on port 22.
**Objective:** Find the non-compliant SSH listener and its version.
**Task:** Flag = port and product version token joined by underscore (e.g. `OpenSSH_8.4p1`).
**Flag format:** `FLAG{port_OpenSSH_x.yp1}`

<details>
<summary>Show Hints</summary>

- Hint 1: Look for `ssh` in the SERVICE column on a port other than 22.

</details>

<details>
<summary>Show Solution</summary>

Port 2222 runs OpenSSH 8.4p1.

Flag: `FLAG{2222_OpenSSH_8.4p1}`

</details>

## Summary

`-sV` identifies product/version, `-O` guesses OS, `-A` bundles more (and is noisy). Identification ≠ vulnerability.

## What To Learn Next

[Reading Nmap Results](reading-results.md)
