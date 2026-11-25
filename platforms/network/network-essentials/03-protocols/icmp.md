# ICMP — Internet Control Message Protocol

> Difficulty: Beginner

## What You Will Learn

- What ICMP is for
- Echo request/reply (ping), TTL, traceroute
- How ICMP looks in Wireshark and Nmap

## Why This Matters in Cybersecurity

Ping is often the first reachability test. ICMP also leaks network information and can be misused (tunnelling, floods).

## 1. Introduction

**ICMP** carries error and diagnostic messages for IP itself. When a router cannot deliver your packet, or a destination port is closed, or you just want to know "is that host alive?", ICMP is the messenger. It is **not** a transport like TCP/UDP: it carries no user data and has no ports - it sits directly inside IP packets.

This position in the stack confuses people, so be precise: ICMP does not run *on top of* TCP or UDP; it is a separate protocol identified by the IP header's protocol field.

| Property | Value |
|----------|-------|
| Layer | 3 |
| Port | None |
| Carried in | IP protocol number 1 |

## 2. Core Concept

Every ICMP message has a **type** and a **code**. The types you will actually read:

| Type | Meaning |
|------|---------|
| 8 | Echo Request (ping) |
| 0 | Echo Reply |
| 3 | Destination Unreachable (code tells why: 3 = port unreachable) |
| 11 | Time Exceeded (TTL hit 0; used by traceroute) |
| 5 | Redirect ("send that via a better gateway") |

**TTL** (Time To Live) decreases by 1 at every router; at 0 the packet is dropped and a Type 11 is returned to the sender. This prevents packets from looping the Internet forever - and traceroute weaponizes it: it sends probes with TTL 1, 2, 3... so each router along the path reveals itself by returning Time Exceeded. That is the whole trick.

"Port unreachable" (Type 3, Code 3) deserves a special note: it is how UDP-based tools learn a port is closed. Nmap's UDP scan interprets it exactly this way - an answer at all means *something* is there.

### Mini Task 1

Type for ping request? Does ICMP use ports?

<details>
<summary>Check Your Answer</summary>

8; no.

</details>

### Mini Task 2

Traceroute shows 9 lines of output. What did it send, and what did it receive, to produce them?

<details>
<summary>Check Your Answer</summary>

It sent probes with increasing TTLs (1, 2, 3, ...) and received ICMP Time Exceeded (Type 11) messages - one from each of the 9 routers where the TTL expired. The last line is usually the destination itself replying.

</details>

## 3. Practical Example — Lab 2: Test Connectivity

```bash
ping -c 4 192.168.1.1        # Linux/macOS
ping -n 4 192.168.1.1        # Windows
traceroute example.com       # Linux/macOS (tracert on Windows)
```
`ping` = send echo requests. `-c 4` / `-n 4` = send 4 packets. Output:
```text
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.42 ms
4 packets transmitted, 4 received, 0% packet loss
```
Read: `ttl` (remaining hops), `time` (round trip), packet loss.

### Exercise

Run `ping` while capturing with filter `icmp`. Find an Echo request and its reply; note the sequence number and TTL.

Then predict: if you ping a host on your own LAN and the same host across the Internet, which reply should show the lower TTL - and why?

<details>
<summary>Check Your Answer</summary>

The Internet host: its reply crossed more routers, so more was subtracted from its initial TTL. A LAN host one hop away returns nearly its full initial TTL (e.g. 64 → 64 directly connected). Comparing TTLs is a rough distance meter.

</details>

**Nmap:** `nmap -sn` uses ICMP echo (plus other probes); `nmap -Pn` skips host discovery.

## 4. Cybersecurity Perspective

- Many firewalls block ping, so "no reply" does **not** mean "host down".
- TTL hints at OS family/distance (initial 64 Linux/macOS, 128 Windows, 255 network gear): a heuristic, not proof.
- ICMP tunnelling hides data in echo payloads; large/odd payloads are suspicious.
- Ping floods = DoS.

## 5. Common Mistakes

Treating a non-responsive ping as a dead host.

## 6. CTF Challenge

**Title:** How Far Away?
**Difficulty:** Easy
**Scenario:** An echo reply arrives with `ttl=126`. The reply source is a Windows-like host (common initial TTL 128).
**Objective:** Estimate initial TTL and hops traversed.
**Task:** Flag = initial TTL and number of routers the reply passed through.
**Flag format:** `FLAG{initial_hops}`

<details>
<summary>Show Hints</summary>

- Hint 1: Hops = initial − received.

</details>

<details>
<summary>Show Solution</summary>

128 − 126 = 2 hops. Flag: `FLAG{128_2}`

</details>

## Summary

ICMP = IP's diagnostic messenger: echo (ping), errors (unreachable), and Time Exceeded (traceroute's engine). No ports, no transport-layer session, and "no reply" never proves "host down".

## What To Learn Next

[Module 4 — Ports & TCP](../04-ports-and-tcp/README.md)
