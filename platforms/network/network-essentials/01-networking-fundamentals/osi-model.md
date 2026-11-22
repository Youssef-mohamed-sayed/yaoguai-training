# The OSI Model

> Difficulty: Beginner

## What You Will Learn

- What a network is and why layers exist
- The 7 OSI layers and what each does
- Data units (PDUs) at each layer

## Why This Matters in Cybersecurity

Analysts say "that's a Layer 2 attack" or "the firewall works at Layer 7". Layers tell you **where** to look when something is wrong, and which tool or device is relevant.

## 1. Introduction

A **network** is two or more devices that can exchange data. Sending data is complicated (cables, addresses, errors, apps), so the job is split into **layers**. Each layer solves one problem and relies on the layer below.

> Analogy: Sending a parcel. You write a letter (application), put it in an envelope with an address (network), a courier van carries it (data link), and roads are the physical medium. Each step has one job.

The **OSI model** (Open Systems Interconnection) is a *reference model* with 7 layers.

## 2. Core Concept — The 7 Layers

| # | Layer | Job | PDU | Examples |
|---|-------|-----|-----|----------|
| 7 | Application | Services the user/program uses | Data | HTTP, DNS, SSH, FTP |
| 6 | Presentation | Formats, encodes, encrypts | Data | TLS/SSL (often placed here), JPEG, ASCII |
| 5 | Session | Starts/keeps/ends conversations | Data | RPC, NetBIOS sessions |
| 4 | Transport | End-to-end delivery, ports | Segment (TCP) / Datagram (UDP) | TCP, UDP |
| 3 | Network | Addressing and routing between networks | Packet | IP, ICMP, routers |
| 2 | Data Link | Delivery on the local link, MAC addresses | Frame | Ethernet, Wi-Fi, ARP*, switches |
| 1 | Physical | Raw bits on a medium | Bits | Cables, radio, hubs |

Memory trick (7→1): **A**ll **P**eople **S**eem **T**o **N**eed **D**ata **P**rocessing.
*ARP is usually described as sitting between Layers 2 and 3.

### Mini Task 1

Fill in the blanks:

1. IP addresses live at Layer ____.
2. MAC addresses live at Layer ____.
3. TCP and UDP live at Layer ____.
4. The PDU at Layer 2 is called a ____.

<details>
<summary>Check Your Answer</summary>

1. 3 (Network) 2. 2 (Data Link) 3. 4 (Transport) 4. Frame

</details>

## 3. How It Works

When you open a website: the browser creates an HTTP request (L7) → TLS encrypts it (L6) → a session is kept (L5) → TCP adds ports (L4) → IP adds addresses (L3) → Ethernet adds MAC addresses (L2) → electrical/radio signals carry it (L1).

### Mini Task 2 — Which layer?

| Scenario | Layer? |
|----------|--------|
| A cable is unplugged | |
| A router picks a path using an IP address | |
| A switch looks at a destination MAC | |
| Browser sends `GET /index.html` | |

<details>
<summary>Check Your Answer</summary>

1 (Physical), 3 (Network), 2 (Data Link), 7 (Application)

</details>

## 4. Practical Example

Open a terminal and run `ping 127.0.0.1`. Ping uses ICMP, which is carried inside IP → Layer 3 activity. No ports are involved: ports belong to Layer 4.

### Exercise

Name the main layer of: switch, router, a basic packet-filter firewall. (Wireshark is different: it shows all layers.)

<details>
<summary>Check Your Answer</summary>

Switch → L2, router → L3, packet-filter firewall → L3/L4.

</details>

## 5. Cybersecurity Perspective

- L1: cable tapping, rogue devices plugged in
- L2: MAC spoofing, ARP spoofing
- L3: IP spoofing, ICMP abuse
- L4: port scanning, SYN floods
- L7: SQL injection, phishing, malware C2 over HTTP

## 6. Common Mistakes

- Thinking OSI is "what the internet runs". The Internet runs TCP/IP; OSI is a teaching/reference model.
- Mixing up PDU names (segment vs packet vs frame).

## 7. CTF Challenge

**Title:** Wrong Layer
**Difficulty:** Easy
**Scenario:** A SOC analyst sees traffic where one device claims two different MAC addresses for the same IP. A teammate says "it's an application-layer attack."
**Objective:** Decide which OSI layer(s) are involved.
**Provided information:** The attack manipulates the mapping between IP and MAC addresses on the local network.
**Task:** Give the layer number where MAC addresses live and the layer number where IP lives, joined by a dash (MAC first).
**Flag format:** `FLAG{X-Y}`

<details>
<summary>Show Hints</summary>

- Hint 1: Which layers contain *addresses*?
- Hint 2: MAC = hardware address on the local link.
- Hint 3: IP = logical address used for routing.

</details>

<details>
<summary>Show Solution</summary>

MAC addresses → Layer 2. IP addresses → Layer 3. The attack (ARP spoofing) abuses the mapping between them, so it is not Layer 7.

Flag: `FLAG{2-3}`

</details>

## Summary

Seven layers, each with one job, each with a PDU: bits, frames, packets, segments/datagrams, data.

## What To Learn Next

[The TCP/IP Model](tcp-ip-model.md)
