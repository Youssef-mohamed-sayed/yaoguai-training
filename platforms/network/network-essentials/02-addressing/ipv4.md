# IPv4 Addressing

> Difficulty: Beginner

## What You Will Learn

- What an IPv4 address is and how it is structured
- Public vs private addresses
- Network, host and broadcast addresses (preview)
- Lab: find your own network settings

## Why This Matters in Cybersecurity

Scope, scans, firewall rules and log analysis all use IP addresses. Knowing private vs public tells you whether a target is internal or Internet-facing.

## 1. Introduction

> Analogy: An IP address is like a building's street address. A port (later) is a specific door inside the building.

An **IPv4 address** is a 32-bit number identifying a device's network interface at Layer 3. We write it as four decimal numbers (octets) separated by dots: `192.168.1.10`.

## 2. Core Concept

32 bits = 4 octets × 8 bits. Each octet is 0–255.

```text
Decimal : 192      .  168      .  1        .  10
Binary  : 11000000 .  10101000 .  00000001 .  00001010
```

Converting an octet: bit values are `128 64 32 16 8 4 2 1`.
`192 = 128 + 64` → `11000000`.

### Mini Task 1

Convert `10` to binary (8 bits), and `11111111` to decimal.

<details>
<summary>Check Your Answer</summary>

10 = 8 + 2 → `00001010`. 11111111 = 255.

</details>

### Public vs Private

| Range | CIDR | Type |
|-------|------|------|
| 10.0.0.0 – 10.255.255.255 | 10.0.0.0/8 | Private |
| 172.16.0.0 – 172.31.255.255 | 172.16.0.0/12 | Private |
| 192.168.0.0 – 192.168.255.255 | 192.168.0.0/16 | Private |
| 127.0.0.0 – 127.255.255.255 | 127.0.0.0/8 | Loopback (this machine) |
| 169.254.0.0/16 | | Link-local (DHCP failed) |
| Everything else | | Public |

Private addresses are not routed on the Internet; your router uses **NAT** to share one public address.

### Mini Task 2

Private, public or special? `8.8.8.8`, `172.20.4.9`, `172.32.0.1`, `127.0.0.1`, `169.254.10.5`

<details>
<summary>Check Your Answer</summary>

Public, private, public (172.32 is outside 172.16–172.31), loopback, link-local.

</details>

## 3. How It Works — Parts of an Address

An IP address has a **network part** and a **host part**, divided by the **subnet mask** (see [Subnetting](subnetting.md)).

- **Network address**: first address of the range (host bits all 0). Names the network.
- **Host addresses**: usable for devices.
- **Broadcast address**: last address (host bits all 1). Means "everyone on this network".

Example `192.168.1.0/24`: network `192.168.1.0`, hosts `.1`–`.254`, broadcast `192.168.1.255`.

## 4. Practical Example — Lab 1: Identify Your Network

**Linux/macOS:**
```bash
ip addr          # Linux
ifconfig         # macOS (or older Linux)
ip route         # shows the default gateway on Linux
```
**Windows:**
```cmd
ipconfig /all
```

Explanation: `ip` = Linux networking tool; `addr` = show interface addresses. `ipconfig /all` = show full adapter details; `/all` adds MAC and DNS info.

Sample (Linux):
```text
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    link/ether 08:00:27:ab:cd:ef brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.50/24 brd 192.168.1.255 scope global eth0
```

### Exercise

Record: local IP, subnet mask (CIDR or dotted), default gateway, MAC. In the sample: IP `192.168.1.50`, mask `/24` (255.255.255.0), MAC `08:00:27:ab:cd:ef`, gateway comes from `ip route` (`default via ...`).

## 5. Cybersecurity Perspective

- Know your own range before scanning; never scan outside authorised scope.
- Private IPs in logs = internal host; unexpected public IPs = potential exfiltration or C2.
- Reserved addresses (127.x) help spot SSRF attempts in web security.

## 6. Common Mistakes

- Thinking an IP identifies a *person*. It identifies an interface, and may be shared (NAT) or change (DHCP).
- Forgetting that `172.16–172.31` is private but `172.32+` is not.

## 7. CTF Challenge

**Title:** Inside or Outside?
**Difficulty:** Easy
**Scenario:** A firewall log shows connections from: `10.4.2.9`, `203.0.113.77`, `192.168.0.8`, `172.31.255.1`, `172.15.0.3`.
**Objective:** Count how many sources are **public**.
**Task:** Flag = count and the first public address (in log order), joined by underscore.
**Flag format:** `FLAG{N_address}`

<details>
<summary>Show Hints</summary>

- Hint 1: Check each against the private table.
- Hint 2: 172.16.0.0–172.31.255.255 is private; 172.15.x is not.

</details>

<details>
<summary>Show Solution</summary>

10.4.2.9 private; 203.0.113.77 public; 192.168.0.8 private; 172.31.255.1 private; 172.15.0.3 public. Two public, first is 203.0.113.77.

Flag: `FLAG{2_203.0.113.77}`

</details>

## Summary

IPv4 = 32 bits, 4 octets. Private ranges: 10/8, 172.16/12, 192.168/16. Network = first, broadcast = last.

## What To Learn Next

[MAC Addresses](mac-addresses.md)
