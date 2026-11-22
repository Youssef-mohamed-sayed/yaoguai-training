# ARP — Protocol Analysis

> Difficulty: Beginner → Intermediate

## What You Will Learn

- ARP packet fields
- ARP in Wireshark
- Recognising suspicious ARP behaviour

Concept intro: [Addressing → ARP](../02-addressing/arp.md).

## Why This Matters in Cybersecurity

ARP spoofing is a classic LAN man-in-the-middle technique; detecting it is a SOC skill.

## 1. Core Concept

| Property | Value |
|----------|-------|
| Layer | 2/3 boundary |
| Port / transport | None; carried directly in Ethernet (EtherType `0x0806`) |

Fields: operation (request=1, reply=2), sender MAC, sender IP, target MAC, target IP.

```text
Request:  Who has 192.168.1.1? Tell 192.168.1.20
          sender: 52:54:00:12:34:20 / 192.168.1.20
          target MAC: 00:00:00:00:00:00 (unknown) / 192.168.1.1
Reply:    192.168.1.1 is at 52:54:00:aa:00:01
```

### Mini Task 1

In a request, what is the target MAC, and why?

<details>
<summary>Check Your Answer</summary>

`00:00:00:00:00:00`, because that is exactly the unknown being asked for.

</details>

## 2. Wireshark / Nmap

Filters: `arp`, `arp.opcode == 1` (requests), `arp.opcode == 2` (replies), `arp.duplicate-address-detected`. Nmap `-sn` on the local LAN uses ARP requests, which are more reliable than ping for host discovery.

## 3. Exercise — Find It

Capture: `ping` a LAN host after clearing the cache (`sudo ip neigh flush all`). Find one request and one reply and fill in: sender IP, sender MAC, target IP, target MAC.

## 4. Cybersecurity Perspective

- Unsolicited replies ("gratuitous ARP") can poison caches.
- Signs: IP seen with 2 MACs; gateway MAC changes; many ARP replies without requests.
- Defences: DAI, port security, static entries, monitoring tools.

## 5. Common Mistakes

Concluding "attack!" from one gratuitous ARP; they are also sent legitimately (failover, boot).

## 6. CTF Challenge

**Title:** Two Replies
**Difficulty:** Medium
**Scenario:** The inventory says the gateway `192.168.1.1` has MAC `52:54:00:aa:00:01`. Capture:
```text
1 52:54:00:12:34:20 → ff:ff:ff:ff:ff:ff  ARP  Who has 192.168.1.1? Tell 192.168.1.20
2 52:54:00:aa:00:01 → 52:54:00:12:34:20  ARP  192.168.1.1 is at 52:54:00:aa:00:01
3 52:54:00:66:66:66 → 52:54:00:12:34:20  ARP  192.168.1.1 is at 52:54:00:66:66:66
```
**Objective:** Identify the suspicious MAC.
**Task:** Flag = the MAC that is claiming the gateway IP but is not the inventory MAC.
**Flag format:** `FLAG{xx:xx:xx:xx:xx:xx}`

<details>
<summary>Show Hints</summary>

- Hint 1: Compare each reply's MAC to the inventory.
- Hint 2: One IP, two different MACs claimed.

</details>

<details>
<summary>Show Solution</summary>

Packet 2 matches inventory. Packet 3 is a second claim for the same IP from `52:54:00:66:66:66`, consistent with ARP spoofing. Verify by checking switch port logs and the victim's ARP cache.

Flag: `FLAG{52:54:00:66:66:66}`

</details>

## Summary

ARP = Ethernet-level IP→MAC lookup with no authentication.

## What To Learn Next

[ICMP](icmp.md)
