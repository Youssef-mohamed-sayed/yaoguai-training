# Capturing Packets

> Difficulty: Beginner

## What You Will Learn

- Choosing a capture interface
- Starting/stopping, saving
- Lab 5: capture and identify protocols

## Why This Matters in Cybersecurity

A clean, scoped capture is the base of any analysis.

## 1. Core Concept

1. Open Wireshark → the start screen lists **interfaces** (`eth0`, `Wi-Fi`, `lo` loopback, VM adapters).
2. The interface with a moving sparkline has traffic.
3. Double-click it (or press the blue shark fin) to start; the red square stops.
4. Save: File → Save As (`.pcapng`).

| Term | Meaning |
|------|---------|
| Interface | The network adapter you capture on |
| Promiscuous mode | Accept frames not addressed to you (on a switch you still mostly see only your traffic) |
| Capture filter (BPF) | Limits what is *recorded* e.g. `port 80`, set before capture |
| Display filter | Limits what is *shown* afterwards (next lesson) |

On Linux you may need permission: run as root or add your user to the `wireshark` group.

### Mini Task 1

Is `port 80` a capture or display filter style? Which is applied before capture?

<details>
<summary>Check Your Answer</summary>

Capture filter (BPF syntax). Capture filters are applied before capture; display filters (e.g. `tcp.port == 80`) afterwards.

</details>

## 2. Lab 5 — Capture Traffic

1. Start capturing on your main interface.
2. In a terminal run: `ping -c 4 192.168.1.1` (your gateway), `nslookup example.com`, and `curl http://example.com`.
3. Stop the capture and save as `lab5.pcapng`.
4. In the packet list, find one packet each for ARP, ICMP, DNS, TCP, HTTP. Fill in:

| Protocol | Packet No. | Source | Destination | Info |
|----------|-----------|--------|-------------|------|
| ARP | | | | |
| ICMP | | | | |
| DNS | | | | |
| TCP SYN | | | | |
| HTTP | | | | |

Use **Statistics → Protocol Hierarchy** to see the protocol mix, and **Statistics → Conversations** for who talked to whom.

### Check Your Answer

Your numbers will differ. Expected order of events: ARP (if cache empty) → ICMP echo req/reply → DNS query/response (UDP 53) → TCP SYN/SYN-ACK/ACK (port 80) → HTTP GET/200.

## 3. Cybersecurity Perspective

- Capture only what you're allowed to; keep PCAPs secure (may contain secrets).
- On busy networks use capture filters to keep files manageable.
- Encrypted traffic: you can still see IPs, ports, timing, and the TLS server name (SNI) in most cases.

## 4. Common Mistakes

- Starting the capture *after* the interesting traffic.
- Wrong interface; VPN adapters change what you see.
- Forgetting to stop and save.

## 5. CTF Challenge

**Title:** First Packets
**Difficulty:** Easy
**Scenario:** You capture `curl http://example.com` after clearing DNS and ARP caches.
**Objective:** Predict order.
**Task:** Flag = protocol names in order of first appearance among DNS, TCP-SYN, HTTP-GET, joined by dashes (uppercase).
**Flag format:** `FLAG{A-B-C}`

<details>
<summary>Show Hints</summary>

- Hint 1: You need an IP before connecting.
- Hint 2: You need a connection before sending HTTP.

</details>

<details>
<summary>Show Solution</summary>

DNS resolves the name, TCP handshake (SYN) opens the connection, then HTTP GET is sent.

Flag: `FLAG{DNS-SYN-GET}`

</details>

## Summary

Pick an interface, capture, stop, save; use capture filters sparingly and display filters freely.

## What To Learn Next

[Display Filters](display-filters.md)
