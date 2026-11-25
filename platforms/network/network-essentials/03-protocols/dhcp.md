# DHCP — Dynamic Host Configuration Protocol

> Difficulty: Beginner

## What You Will Learn

- How devices automatically get IP settings
- The DORA process
- DHCP-related attacks

## Why This Matters in Cybersecurity

DHCP logs map IPs to devices at a time - the first place investigators look when an alert names only an IP. Rogue DHCP servers can redirect all of a victim's traffic without touching any other part of the network.

## 1. Introduction

When you join a network you need four things before anything works: an **IP address**, a **subnet mask**, a **default gateway**, and a **DNS server**. Configuring them by hand on every laptop and phone does not scale, so **DHCP** hands them out automatically the moment a device connects.

A DHCP assignment is a **lease**, not a gift: it expires (commonly 24 hours on home networks, shorter on busy ones). Halfway through the lease the client tries to renew with the same server; if the server is gone, the client keeps the address until expiry and then starts over with Discover. This is why "my IP changed overnight" is normal behavior, not a fault.

| Property | Value |
|----------|-------|
| Layer | 7 |
| Ports | Server UDP 67, client UDP 68 |
| Transport | UDP |

## 2. How It Works — DORA

```text
Client                              Server
  Discover (broadcast) ───────────►   "Is there a DHCP server?"
           ◄─────────── Offer          "Here is 192.168.1.134"
  Request  ───────────►                "I'll take 192.168.1.134"
           ◄─────────── Acknowledge    "Confirmed, lease 24h"
```
The client starts with source `0.0.0.0` and destination `255.255.255.255` (it has no IP yet). Discover and Offer are broadcasts, which is why DHCP cannot cross routers without a **DHCP relay** (the `ip helper-address` feature on enterprise gear).

Why UDP and not TCP? TCP needs addresses on both ends before the handshake - impossible when the client has no address. Broadcast UDP works with zero configuration, which is exactly the situation DHCP exists for.

### Mini Task 1.5

A capture shows a Discover from source 0.0.0.0 port 68 to 255.255.255.255 port 67. Why can the client send this before it owns an address?

<details>
<summary>Check Your Answer</summary>

0.0.0.0 means "this host, no address yet" and 255.255.255.255 is the local broadcast address - every host on the segment receives it, so the client can be found and answered without knowing anything.

</details>

### Mini Task 1

Put in order: Request, Discover, Ack, Offer.

<details>
<summary>Check Your Answer</summary>

Discover, Offer, Request, Ack.

</details>

## 3. Example Message

```text
DHCP Offer
  Your (client) IP : 192.168.1.134
  Subnet mask      : 255.255.255.0
  Router           : 192.168.1.1
  DNS server       : 192.168.1.1
  Lease time       : 86400 s
```

## 4. Practical Example / Exercise

- Windows: `ipconfig /renew`. Linux: `sudo dhclient -v` (on your lab machine).
- Wireshark filter: `bootp` (older name) or `dhcp`. Capture while renewing; find the four DORA messages.

**Exercise.** While capturing, run a renewal and then look at your own lease: `ipconfig /all` (Windows) or `cat /var/lib/dhcp/dhclient.leases` / NetworkManager's `nmcli` on Linux. Write down your lease's expiry time and the server that issued it.

<details>
<summary>Check Your Answer</summary>

The lease file (or `ipconfig /all` under "Lease Obtained / Lease Expires") shows both timestamps - commonly 24 hours apart on home networks. The issuing server is usually your router (e.g. 192.168.1.1). If the expiry is missing or the server is unexpected, that is worth investigating.

</details>

**Nmap:** `67/udp open|filtered dhcps`.

## 5. Cybersecurity Perspective

- **Rogue DHCP server**: DHCP has no authentication - the *first* Offer a client receives usually wins. An attacker's server answers faster than the real one and hands the victim a malicious gateway/DNS, turning the attacker into a man-in-the-middle for everything the victim does.
- **DHCP starvation**: requesting thousands of leases with spoofed MAC addresses until the pool is empty, so legitimate clients get nothing (and a rogue server can then serve them).
- Mitigation: DHCP snooping on switches.
- Forensics: lease logs map IP → MAC → time.

## 6. Common Mistakes

Assuming a device's IP is permanent. Leases expire and change.

## 7. CTF Challenge

**Title:** Order of Events
**Difficulty:** Easy
**Scenario:** A capture lists these messages in scrambled order:
1. DHCP Request  2. DHCP Discover  3. DHCP ACK  4. DHCP Offer
**Objective:** Restore the real order.
**Task:** Flag = message numbers in correct order, dash-separated.
**Flag format:** `FLAG{a-b-c-d}`

<details>
<summary>Show Hints</summary>

- Hint 1: DORA = Discover, Offer, Request, Acknowledge.

</details>

<details>
<summary>Show Solution</summary>

Discover(2) → Offer(4) → Request(1) → ACK(3).

Flag: `FLAG{2-4-1-3}`

</details>

## Summary

DHCP automates addressing via DORA (Discover, Offer, Request, ACK) on UDP 67/68. Leases expire and renew; broadcast-based, unauthenticated, and therefore both essential and spoofable - DHCP snooping is the standard defense.

## What To Learn Next

[FTP](ftp.md)
