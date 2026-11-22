# Encapsulation and Decapsulation

> Difficulty: Beginner

## What You Will Learn

- How data is wrapped in headers on the way down the stack
- Names of data units at each layer

## Why This Matters in Cybersecurity

A captured packet *is* nested envelopes. Reading a capture means opening them layer by layer.

## 1. Introduction

> Analogy: A letter goes in an envelope, which goes in a courier bag, which goes in a van. At the destination you unpack in reverse order.

**Encapsulation** = adding a header (and sometimes a trailer) at each layer when sending.
**Decapsulation** = removing them layer by layer when receiving.

## 2. Core Concept

```text
Application:  [      DATA      ]
Transport:    [TCP hdr][ DATA ]                               ← Segment
Internet:     [IP hdr][TCP hdr][ DATA ]                       ← Packet
Link:         [Eth hdr][IP hdr][TCP hdr][ DATA ][Eth trailer] ← Frame
Physical:     0101101001...                                   ← Bits
```

| Layer | Header contains |
|-------|-----------------|
| Transport | Source/destination **port**, sequence numbers, flags |
| Internet | Source/destination **IP**, TTL, protocol |
| Link | Source/destination **MAC**, EtherType |

### Mini Task 1

Which header holds the destination port? Which holds the source MAC?

<details>
<summary>Check Your Answer</summary>

TCP/UDP (Transport) header; Ethernet (Link) header.

</details>

## 3. How It Works

Sending: Application → Transport → Internet → Link → Physical.
Receiving: Physical → Link (check MAC) → Internet (check IP) → Transport (check port) → Application.

A **router** removes the Ethernet header and builds a new one for the next hop, but the IP addresses stay the same (except with NAT).

### Mini Task 2

Order these steps for a received packet: (A) read the port, (B) check the MAC, (C) read the IP.

<details>
<summary>Check Your Answer</summary>

B, C, A.

</details>

## 4. Practical Example / Exercise

In Wireshark (later) click any HTTP packet: the details pane lists Frame → Ethernet → IP → TCP → HTTP. That is encapsulation, outermost first.

## 5. Cybersecurity Perspective

- Tunnelling (VPN, DNS tunnelling) puts one protocol inside another.
- Firewalls inspect different headers at different depths.
- Fragmentation or odd header values can hide traffic from weak filters.

## 6. Common Mistakes

Calling everything a "packet". Precisely: frame (L2), packet (L3), segment (L4 TCP), datagram (L4 UDP).

## 7. CTF Challenge

**Title:** Peel the Onion
**Difficulty:** Easy
**Scenario:** You see this stack in a capture (outer → inner): `Ethernet / IPv4 / TCP / HTTP`.
**Objective:** Name the data unit after removing only the Ethernet header.
**Task:** Flag = lowercase PDU name remaining, underscore, the OSI layer number that adds source/destination IP.
**Flag format:** `FLAG{pdu_layer}`

<details>
<summary>Show Hints</summary>

- Hint 1: Removing the frame header leaves an IP-level unit.
- Hint 2: IP addresses are OSI Layer 3.

</details>

<details>
<summary>Show Solution</summary>

Ethernet removed → IP header + payload = packet. IP is Layer 3.

Flag: `FLAG{packet_3}`

</details>

## Summary

Down the stack: wrap. Up the stack: unwrap. PDUs: data, segment/datagram, packet, frame, bits.

## What To Learn Next

[Module 2 — Addressing](../02-addressing/README.md)
