# DHCP — Dynamic Host Configuration Protocol

> Difficulty: Beginner

## What You Will Learn

- How devices automatically get IP settings
- The DORA process
- DHCP-related attacks

## Why This Matters in Cybersecurity

DHCP logs map IPs to devices at a time. Rogue DHCP servers can redirect all of a victim's traffic.

## 1. Introduction

When you join a network you need an IP, mask, gateway and DNS server. **DHCP** hands these out automatically.

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
The client starts with source `0.0.0.0` and destination `255.255.255.255` (it has no IP yet).

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

**Nmap:** `67/udp open|filtered dhcps`.

## 5. Cybersecurity Perspective

- **Rogue DHCP server** gives victims a malicious gateway/DNS.
- **DHCP starvation**: exhausting the pool.
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

DHCP automates addressing via DORA on UDP 67/68.

## What To Learn Next

[FTP](ftp.md)
