# The TCP Three-Way Handshake

> Difficulty: Intermediate

## What You Will Learn

- SYN, SYN-ACK, ACK
- Sequence and acknowledgment numbers
- Connection termination and RST
- Why it matters for scanning and defence

## Why This Matters in Cybersecurity

Port scanners, SYN floods, firewall behaviour and connection logs are all about the handshake.

## 1. Introduction

Before sending data, TCP establishes a connection so both sides agree they are ready and on what sequence numbers to use.

```text
Client                    Server
  SYN  -------------------->
       <-------------------- SYN-ACK
  ACK  -------------------->
  (connection established; data flows)
```

## 2. Core Concept

| Flag | Meaning |
|------|---------|
| SYN | Synchronise: "I want to connect; my starting sequence number is X" |
| ACK | Acknowledge: "I received everything up to number N−1; next I expect N" |
| FIN | "I am finished sending" |
| RST | Reset: abort/refuse the connection |
| PSH | Push data to the application now |

**Sequence number**: counts bytes sent. The first value is the **ISN** (initial sequence number), random.
**Acknowledgment number**: the next sequence number the receiver expects.

Example with ISNs 2500 (client) and 9000 (server):

| Step | Direction | Flags | Seq | Ack |
|------|-----------|-------|-----|-----|
| 1 | C → S | SYN | 2500 | – |
| 2 | S → C | SYN, ACK | 9000 | 2501 |
| 3 | C → S | ACK | 2501 | 9001 |

Why +1? A SYN consumes one sequence number.

### Mini Task 1

Which comes first: ACK, SYN or SYN-ACK? In step 2, why is Ack 2501?

<details>
<summary>Check Your Answer</summary>

SYN, then SYN-ACK, then ACK. Because the server expects the client's next byte number, 2500 + 1.

</details>

## 3. Termination and RST

Graceful close: `FIN → ACK`, `FIN → ACK` (each side closes its direction).
```text
A: FIN, ACK ──►   B: ACK ──►   B: FIN, ACK ──►   A: ACK ──►
```
**RST** = immediate stop. A closed port answers a SYN with `RST, ACK`.

### Mini Task 2

You send a SYN to a closed port. What comes back? What if a firewall silently drops it?

<details>
<summary>Check Your Answer</summary>

`RST, ACK` (Nmap: closed). Nothing (Nmap: filtered).

</details>

## 4. Packet-Analysis Exercise

```text
No. Source              Destination         Info
1   192.168.1.50:51514  93.184.216.34:80    [SYN] Seq=0
2   93.184.216.34:80    192.168.1.50:51514  [SYN, ACK] Seq=0 Ack=1
3   192.168.1.50:51514  93.184.216.34:80    [ACK] Seq=1 Ack=1
```
(Wireshark shows *relative* numbers by default.) Answer:

1. Which packet is SYN-ACK?
2. Client IP and port? Server IP and port?
3. Which service is probably running?

<details>
<summary>Check Your Answer</summary>

1. Packet 2. 2. Client 192.168.1.50:51514, server 93.184.216.34:80. 3. HTTP (port 80).

</details>

## 5. Cybersecurity Perspective

- **SYN scan** (`nmap -sS`): send SYN; if SYN-ACK comes back, port is open; scanner replies RST and never completes the handshake.
- **SYN flood**: many SYNs exhaust a server's half-open connection table.
- **Connect scan** (`-sT`) completes the full handshake and is more visible in logs.
- Stateful firewalls track handshakes to allow only legitimate replies.

## 6. Common Mistakes

Thinking "SYN-ACK" means data was exchanged. It only means the port accepted a connection request.

## 7. CTF Challenge

**Title:** Complete the Handshake
**Difficulty:** Medium
**Scenario:** A partial capture (raw sequence numbers) from a lab web connection:
```text
1  10.0.0.5:44120 → 10.0.0.9:80   [SYN]       Seq=1500
2  10.0.0.9:80 → 10.0.0.5:44120   [SYN, ACK]  Seq=7000 Ack=?
3  10.0.0.5:44120 → 10.0.0.9:80   [ACK]       Seq=?    Ack=?
```
**Objective:** Fill in the missing values.
**Task:** Flag = Ack in packet 2 and Ack in packet 3, underscore-joined.
**Flag format:** `FLAG{ack2_ack3}`

<details>
<summary>Show Hints</summary>

- Hint 1: SYN consumes one sequence number.
- Hint 2: Packet 2 acks the client's ISN + 1.
- Hint 3: Packet 3 acks the server's ISN + 1.

</details>

<details>
<summary>Show Solution</summary>

Packet 2 Ack = 1500 + 1 = 1501. Packet 3 has Seq 1501, Ack = 7000 + 1 = 7001.

Flag: `FLAG{1501_7001}`

</details>

## Summary

SYN → SYN-ACK → ACK establishes TCP; FIN closes gracefully; RST aborts; scans abuse the handshake responses.

## What To Learn Next

[Module 5 — Network Devices & Topologies](../05-network-devices/README.md)
