# Reading Captures Like an Analyst

> Difficulty: Intermediate

## What You Will Learn

- A repeatable method for unknown captures
- Spotting suspicious or unusual behaviour
- Statistics tools

## Why This Matters in Cybersecurity

SOC, IR, forensics and threat hunting all start with "here's a pcap, what happened?".

## 1. Method

1. **Overview**: Statistics → Capture File Properties, Protocol Hierarchy, Conversations, Endpoints.
2. **Who** talks: internal vs external IPs (see [IPv4](../02-addressing/ipv4.md)).
3. **What protocols**: expected or odd?
4. **Timeline**: sort by time; look for bursts and periodic patterns.
5. **Drill down**: filter → follow stream → inspect fields.
6. **Conclude carefully**: what is proven vs suspected?

## 2. Unusual Behaviour Cheat-List

| Observation | Possible meaning |
|-------------|------------------|
| One IP sending SYNs to many ports/hosts | Port scan / sweep |
| Many RSTs back | Closed ports (scan) or blocked connections |
| Repeated identical-sized packets every N seconds | Beaconing |
| Very long or random-looking DNS names | DNS tunnelling / DGA |
| Two MACs claiming one IP | ARP spoofing |
| Cleartext credentials | Insecure protocol use |
| Large outbound transfer to an unknown external IP | Possible exfiltration |
| Unexpected protocol on a port (e.g. SSH on 53) | Evasion or misconfiguration |

These are *indicators*, not proof. Always verify.

### Mini Task 1

Which two observations suggest a port scan? (a) many SYN to different ports, (b) one GET /, (c) many RST replies, (d) one ARP request.

<details>
<summary>Check Your Answer</summary>

(a) and (c).

</details>

## 3. Practical Exercise — Spot the Scan

Given:
```text
1  10.0.0.99 → 10.0.0.5  TCP  40001 → 21   [SYN]
2  10.0.0.5  → 10.0.0.99 TCP  21 → 40001   [RST, ACK]
3  10.0.0.99 → 10.0.0.5  TCP  40001 → 22   [SYN]
4  10.0.0.5  → 10.0.0.99 TCP  22 → 40001   [SYN, ACK]
5  10.0.0.99 → 10.0.0.5  TCP  40001 → 22   [RST]
6  10.0.0.99 → 10.0.0.5  TCP  40001 → 23   [SYN]
7  10.0.0.5  → 10.0.0.99 TCP  23 → 40001   [RST, ACK]
8  10.0.0.99 → 10.0.0.5  TCP  40001 → 80   [SYN]
9  10.0.0.5  → 10.0.0.99 TCP  80 → 40001   [SYN, ACK]
10 10.0.0.99 → 10.0.0.5  TCP  40001 → 80   [RST]
```
1. What is likely happening?
2. Which ports are open? Which closed?
3. Why did 10.0.0.99 send RST after SYN-ACK?

<details>
<summary>Check Your Answer</summary>

1. A SYN (half-open) scan from 10.0.0.99 against 10.0.0.5. 2. Open: 22, 80. Closed: 21, 23. 3. A SYN scanner never completes the handshake; it resets the connection after learning the port is open.

</details>

## 4. Cybersecurity Perspective

Link what you see back to the course: handshake behaviour (Module 4), Nmap scan types (Module 6), protocol fields (Module 3).

## 5. Common Mistakes

- Declaring compromise from one anomaly.
- Ignoring time (when it happened, how often).
- Forgetting legitimate causes (backups, monitoring tools, vulnerability scanners).

## 6. CTF Challenge

**Title:** Who Scanned Us?
**Difficulty:** Medium
**Scenario:** Use the capture in section 3.
**Objective:** Identify the scanner and the open ports.
**Task:** Flag = scanner IP, then open ports ascending separated by commas, joined by underscore.
**Flag format:** `FLAG{ip_p1,p2}`

<details>
<summary>Show Hints</summary>

- Hint 1: Who initiates the SYNs?
- Hint 2: SYN-ACK = open; RST,ACK in reply to SYN = closed.

</details>

<details>
<summary>Show Solution</summary>

Scanner is 10.0.0.99; SYN-ACKs came from ports 22 and 80.

Flag: `FLAG{10.0.0.99_22,80}`

</details>

## Summary

Overview → who/what → timeline → drill down → careful conclusion.

## What To Learn Next

[Module 8 — Final Challenges](../08-final-challenges/README.md)
