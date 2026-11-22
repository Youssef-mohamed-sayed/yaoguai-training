# Port Scanning with Nmap

> Difficulty: Beginner → Intermediate

## What You Will Learn

- Default scan, `-p`, `-p-`
- Scan types `-sS`, `-sT`, `-sU`
- Port states in output

## Why This Matters in Cybersecurity

Open ports show exposed services: the attack surface.

## 1. Default Scan

```bash
nmap 192.168.56.20
```
```text
nmap           → program
192.168.56.20  → target
```
With no options Nmap checks the **1000 most common TCP ports** and discovers whether the host is up first.

Sample output:
```text
Nmap scan report for 192.168.56.20
Host is up (0.00061s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE    SERVICE
22/tcp   open     ssh
80/tcp   open     http
139/tcp  filtered netbios-ssn
445/tcp  open     microsoft-ds
3306/tcp open     mysql
```
Interpretation: 4 open ports, 1 filtered, 995 closed. The **SERVICE** column is guessed from the port number (from a lookup table), not verified.

### Mini Task 1

How many ports were scanned in total? Which port is filtered?

<details>
<summary>Check Your Answer</summary>

1000 (995 + 5 listed). 139.

</details>

## 2. Choosing Ports

```bash
nmap -p 22,80,443 192.168.56.20
```
```text
-p 22,80,443 → scan exactly these ports (comma list)
-p 1-1024    → a range
-p-          → all 65535 TCP ports
--top-ports 100 → the 100 most common ports
```
`nmap -p- 192.168.56.20` is thorough but slower, and finds services on odd ports (like SSH on 2222).

### Mini Task 2 — Command completion

```bash
nmap ______ 22,3306 192.168.56.20    # scan only ports 22 and 3306
nmap ______ 192.168.56.20            # scan all 65535 TCP ports
```

<details>
<summary>Check Your Answer</summary>

`-p`; `-p-`.

</details>

## 3. Scan Types

| Option | Name | How it works | Notes |
|--------|------|--------------|-------|
| `-sS` | SYN ("half-open") scan | Sends SYN; SYN-ACK → open; RST → closed; no reply → filtered; then Nmap sends RST | Needs root/admin; default when privileged |
| `-sT` | TCP connect scan | Completes the full handshake using the OS | Default without privileges; more logged |
| `-sU` | UDP scan | Sends UDP probes; ICMP port-unreachable → closed; silence → open\|filtered | Slow; finds DNS (53), DHCP (67), SNMP (161) |

```bash
sudo nmap -sS -p 1-1000 192.168.56.20
nmap -sT -p 80 192.168.56.20
sudo nmap -sU -p 53,161 192.168.56.20
```
Sample UDP output:
```text
PORT    STATE         SERVICE
53/udp  open          domain
161/udp open|filtered snmp
```
`open|filtered` = no response; could be open or blocked.

### Mini Task 3

Which scan completes the 3-way handshake? Which needs privileges to craft raw packets? Why is UDP scanning ambiguous?

<details>
<summary>Check Your Answer</summary>

`-sT`; `-sS`; because open UDP services often send no reply, which looks like a dropped probe.

</details>

## 4. Practical Task (Lab)

1. Run `nmap 192.168.56.20` on your lab target.
2. Run `nmap -p- 192.168.56.20`. Did new ports appear?
3. Capture the scan in Wireshark (filter `tcp.flags.syn == 1 && tcp.flags.ack == 0`). Count the SYN probes and see RSTs or SYN-ACKs come back.

## 5. Cybersecurity Perspective

- Open ports → candidate services to enumerate.
- Unexpected open port on a server → misconfiguration or compromise sign.
- Defenders: scanning appears as many SYNs to many ports from one IP, which IDS tools detect.
- **Open ≠ vulnerable.**

## 6. Common Mistakes

- Using only default scan (misses ports above the top 1000).
- Running UDP scans on large ranges (very slow).
- Trusting the SERVICE name without `-sV`.

## 7. CTF Challenge

**Title:** Count the Doors
**Difficulty:** Easy
**Scenario:** Use the sample default-scan output above.
**Objective:** Count open and filtered ports.
**Task:** Flag = number of open ports, underscore, number of filtered ports.
**Flag format:** `FLAG{open_filtered}`

<details>
<summary>Show Hints</summary>

- Hint 1: Count only rows whose STATE is exactly `open`.
- Hint 2: `Not shown` ports are closed.

</details>

<details>
<summary>Show Solution</summary>

Open: 22, 80, 445, 3306 = 4. Filtered: 139 = 1.

Flag: `FLAG{4_1}`

</details>

## Summary

Default scan = top 1000 TCP; `-p`/`-p-` choose ports; `-sS` stealthier half-open, `-sT` full connect, `-sU` UDP.

## What To Learn Next

[Service & Version Detection](service-detection.md)
