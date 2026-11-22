# Subnetting

> Difficulty: Intermediate (take it slowly)

## What You Will Learn

- Binary, octets, subnet masks, CIDR
- Network bits vs host bits
- Calculating network, broadcast, host range and host count for /24–/30
- Splitting a network into subnets

## Why This Matters in Cybersecurity

You must know exactly which addresses a scan range such as `192.168.1.0/24` covers, and recognise network segments in logs, firewall rules and scope documents.

## 1. Introduction

> Analogy: A city (network) divided into districts (subnets). Each address has a district part and a house-number part.

**Subnetting** divides an IP range into smaller networks. The **subnet mask** says which bits are the network part and which are the host part.

## 2. Core Concept — Bits

```text
IPv4 = 32 bits
11000000.10101000.00000001.00000000   = 192.168.1.0
```

Subnet mask `255.255.255.0` in binary:
```text
11111111.11111111.11111111.00000000
└──── 24 network bits ────┘└ 8 host bits ┘   → /24
```

**CIDR notation**: `/N` = the number of leading 1-bits (network bits). `192.168.1.0/24`.

Host bits `h = 32 − N`.
- Total addresses = 2^h
- Usable hosts = 2^h − 2 (minus network and broadcast)

### Mini Task 1

For `/24`: how many host bits? Total addresses? Usable hosts?

<details>
<summary>Check Your Answer</summary>

8 host bits; 256 total; 254 usable.

</details>

## 3. How To Calculate

### Mask reference

| CIDR | Mask | Host bits | Block size | Usable hosts |
|------|------|-----------|-----------|--------------|
| /24 | 255.255.255.0 | 8 | 256 | 254 |
| /25 | 255.255.255.128 | 7 | 128 | 126 |
| /26 | 255.255.255.192 | 6 | 64 | 62 |
| /27 | 255.255.255.224 | 5 | 32 | 30 |
| /28 | 255.255.255.240 | 4 | 16 | 14 |
| /29 | 255.255.255.248 | 3 | 8 | 6 |
| /30 | 255.255.255.252 | 2 | 4 | 2 |

**Block size** = 256 − (last mask value). Networks start at multiples of the block size.

### Method (for /25–/30, interesting octet = 4th)

1. Find the block size.
2. Network address = largest multiple of block size ≤ the host's last octet.
3. Broadcast = next network address − 1.
4. Usable range = network+1 … broadcast−1.

### Worked example: `192.168.1.100/28`

Block = 16. Multiples: 0, 16, … 96, 112. 100 falls in 96. 
Network `192.168.1.96`, broadcast `192.168.1.111`, usable `.97`–`.110` (14 hosts).

### Worked example: `192.168.1.10/24`

Network `192.168.1.0`, broadcast `192.168.1.255`, usable `.1`–`.254`.

### Mini Task 2 (progressive)

| # | Address | Network | Broadcast | Usable range | Hosts |
|---|---------|---------|-----------|--------------|-------|
| a | 192.168.1.10/24 | | | | |
| b | 192.168.1.130/25 | | | | |
| c | 192.168.1.70/26 | | | | |
| d | 192.168.1.45/27 | | | | |
| e | 192.168.1.20/29 | | | | |
| f | 192.168.1.5/30 | | | | |

<details>
<summary>Check Your Answer</summary>

| # | Network | Broadcast | Usable | Hosts |
|---|---------|-----------|--------|-------|
| a | .0 | .255 | .1–.254 | 254 |
| b | .128 | .255 | .129–.254 | 126 |
| c | .64 | .127 | .65–.126 | 62 |
| d | .32 | .63 | .33–.62 | 30 |
| e | .16 | .23 | .17–.22 | 6 |
| f | .4 | .7 | .5–.6 | 2 |

</details>

## 4. Splitting a Network

Split `192.168.20.0/24` into **4 equal subnets**: 4 = 2², borrow 2 bits → `/26`.

| Subnet | Network | Usable range | Broadcast |
|--------|---------|--------------|-----------|
| 1 | 192.168.20.0/26 | .1–.62 | .63 |
| 2 | 192.168.20.64/26 | .65–.126 | .127 |
| 3 | 192.168.20.128/26 | .129–.190 | .191 |
| 4 | 192.168.20.192/26 | .193–.254 | .255 |

### Exercise

You need subnets for at least 25 hosts each. What is the smallest prefix (largest /N) that works? (Hint: 2^h − 2 ≥ 25.)

<details>
<summary>Check Your Answer</summary>

h = 5 → 30 usable ≥ 25 → `/27`. (h = 4 gives only 14.)

</details>

### Lab

Take your own network from [Lab 1](ipv4.md). Write its network address, broadcast and usable range, then verify with `ipcalc` (Linux) if installed.

## 5. Cybersecurity Perspective

- Scan scope: `-sn 192.168.1.0/24` = 256 addresses; `/28` = 16. Mistakes mean scanning too much or too little.
- Segmentation: separate servers, users and guests so a compromise stays contained.
- Firewall rules and ACLs are written in CIDR.

## 6. Common Mistakes

- Forgetting the −2 (network and broadcast).
- Starting networks at wrong multiples.
- Mixing mask `255.255.255.224` with `/28` (it is `/27`).

## 7. CTF Challenge

**Title:** Carve the Subnet
**Difficulty:** Medium
**Scenario:** A lab network uses `192.168.10.0/27`. You must report its boundaries to a team lead.
**Objective:** Compute network, broadcast and usable host count.
**Task:** Build the flag from network, broadcast and number of usable hosts.
**Flag format:** `FLAG{network_broadcast_hosts}`

<details>
<summary>Show Hints</summary>

- Hint 1: /27 → 5 host bits → block size 32.
- Hint 2: Network is `.0`; the next network starts at `.32`.
- Hint 3: Broadcast is one below the next network. Usable = 32 − 2.

</details>

<details>
<summary>Show Solution</summary>

Block size 32. Network `192.168.10.0`, next `192.168.10.32`, so broadcast `192.168.10.31`. Usable `.1`–`.30` = 30 hosts.

Flag: `FLAG{192.168.10.0_192.168.10.31_30}`

</details>

**Bonus Challenge — Harder**
Host `172.16.5.200/26`. Find network, broadcast, usable count. Flag: `FLAG{network_broadcast_hosts}`

<details>
<summary>Show Solution</summary>

Block 64; multiples 0, 64, 128, 192. 200 is in 192. Network `172.16.5.192`, broadcast `172.16.5.255`, 62 hosts.

Flag: `FLAG{172.16.5.192_172.16.5.255_62}`

</details>

## Summary

Mask = network bits; /N → host bits 32−N; usable = 2^h − 2; block size = 256 − mask octet.

## What To Learn Next

[ARP](arp.md)
