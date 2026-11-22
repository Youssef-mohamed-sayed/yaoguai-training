# ICMP — Internet Control Message Protocol

> Difficulty: Beginner

## What You Will Learn

- What ICMP is for
- Echo request/reply (ping), TTL, traceroute
- How ICMP looks in Wireshark and Nmap

## Why This Matters in Cybersecurity

Ping is often the first reachability test. ICMP also leaks network information and can be misused (tunnelling, floods).

## 1. Introduction

**ICMP** carries error and diagnostic messages for IP. It is **not** a transport like TCP/UDP: no ports.

| Property | Value |
|----------|-------|
| Layer | 3 |
| Port | None |
| Carried in | IP protocol number 1 |

## 2. Core Concept

| Type | Meaning |
|------|---------|
| 8 | Echo Request (ping) |
| 0 | Echo Reply |
| 3 | Destination Unreachable |
| 11 | Time Exceeded (TTL hit 0; used by traceroute) |

**TTL** (Time To Live) decreases by 1 at every router; at 0 the packet is dropped and a Type 11 is returned.

### Mini Task 1

Type for ping request? Does ICMP use ports?

<details>
<summary>Check Your Answer</summary>

8; no.

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

ICMP = IP's diagnostic messenger; ping, traceroute, errors; no ports.

## What To Learn Next

[Module 4 — Ports & TCP](../04-ports-and-tcp/README.md)
