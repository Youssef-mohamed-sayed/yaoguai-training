# MAC Addresses

> Difficulty: Beginner

## What You Will Learn

- What a MAC address is and its structure
- IP vs MAC: who uses which
- Broadcast and multicast MACs

## Why This Matters in Cybersecurity

Switch security, device tracking, spoofing detection, and forensics ("which physical device was this?") all depend on MAC addresses.

## 1. Introduction

A **MAC address** (Media Access Control) is a 48-bit Layer 2 address assigned to a network interface, written as six hex pairs: `08:00:27:ab:cd:ef`.

> Analogy: IP is your current postal address (changes when you move). MAC is like a serial number stamped on your network card (identifies the hardware on the local link).

## 2. Core Concept

```text
08:00:27 : ab:cd:ef
 └ OUI ┘   └ device-specific ┘
```

- **OUI** (first 24 bits): identifies the manufacturer (e.g. `08:00:27` = VirtualBox).
- Special: `ff:ff:ff:ff:ff:ff` = **broadcast** (all devices on the local network).
- If the lowest bit of the first byte is 1, the address is **multicast**.
- MACs can be changed in software (**spoofing**).

### Mini Task 1

What is the OUI of `00:1A:2B:3C:4D:5E`? What does `ff:ff:ff:ff:ff:ff` mean?

<details>
<summary>Check Your Answer</summary>

`00:1A:2B`; broadcast to every device on the local segment.

</details>

## 3. How It Works — IP and MAC Together

- **IP** gets a packet across many networks (end to end).
- **MAC** gets a frame across one hop (link to link).

```text
PC (192.168.1.50) ──► Router (192.168.1.1) ──► Internet ──► Server (203.0.113.10)
 Frame 1: src=PC MAC,     dst=Router MAC       IP: src=192.168.1.50 dst=203.0.113.10
 Frame 2: src=Router MAC, dst=next-hop MAC     (IP stays the same, MACs change each hop)
```

To send to a local IP, a host needs the target's MAC: that is what [ARP](arp.md) provides.

### Mini Task 2

When you browse a public website, whose MAC is the destination MAC in the first frame leaving your PC?

<details>
<summary>Check Your Answer</summary>

Your default gateway (router), not the web server.

</details>

## 4. Practical Example / Exercise

Run `ip link` (Linux) or `getmac` (Windows). Find your interface MAC and look up its OUI on a public OUI lookup site.

## 5. Cybersecurity Perspective

- MAC spoofing bypasses naive MAC filters.
- Switch CAM-table flooding and ARP spoofing exploit Layer 2 trust.
- Randomised MACs on phones complicate tracking and forensics.
- Never treat a MAC as proof of identity.

## 6. Common Mistakes

Assuming MAC addresses cross routers unchanged. They do not.

## 7. CTF Challenge

**Title:** Whose Card Is That?
**Difficulty:** Easy
**Scenario:** A switch log lists a rogue device with MAC `DC:A6:32:11:22:33`.
**Objective:** Extract the vendor prefix.
**Task:** Flag = the OUI, uppercase, with no separators.
**Flag format:** `FLAG{XXXXXX}`

<details>
<summary>Show Hints</summary>

- Hint 1: OUI is the first 3 bytes.

</details>

<details>
<summary>Show Solution</summary>

First three bytes: DC, A6, 32. Flag: `FLAG{DCA632}`

</details>

## Summary

MAC = 48-bit link-layer address; first half = vendor; local scope only.

## What To Learn Next

[Subnetting](subnetting.md)
