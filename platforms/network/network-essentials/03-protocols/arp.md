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

ARP has one job: translate an IP address into a MAC address on the local network. IP gets a packet to the right network; the final hop on the LAN is delivered by Ethernet, which understands only MAC addresses. When a host knows *what* to send but not *where the NIC is*, it ARPs.

Fields: operation (request=1, reply=2), sender MAC, sender IP, target MAC, target IP.

Results are cached in the **ARP table** (`arp -a`, or `ip neigh` on Linux) for a few minutes, so repeat traffic to the same host skips the broadcast. Nothing in a reply is authenticated: any host may answer any query, and the *last* reply wins. That single design fact is why ARP spoofing exists.

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

### Mini Task 2

Why does ARP only work on the local network, and what happens when the destination IP is remote?

<details>
<summary>Check Your Answer</summary>

ARP requests are Ethernet broadcasts, which routers do not forward. For a remote destination the host ARPs for its *default gateway's* MAC instead and sends the frame there; each router along the path repeats the process on its own local segments.

</details>

## 2. Wireshark / Nmap

Filters: `arp`, `arp.opcode == 1` (requests), `arp.opcode == 2` (replies), `arp.duplicate-address-detected`. Nmap `-sn` on the local LAN uses ARP requests, which are more reliable than ping for host discovery.

## 3. Exercise — Find It

Capture: `ping` a LAN host after clearing the cache (`sudo ip neigh flush all`). Find one request and one reply and fill in: sender IP, sender MAC, target IP, target MAC.

Then run `ip neigh` (or `arp -a`) twice, a few minutes apart, and explain any difference.

<details>
<summary>Check Your Answer</summary>

The request is broadcast to `ff:ff:ff:ff:ff:ff` with target MAC zeroed; the reply is unicast from the owner of the queried IP, carrying its MAC. The ARP cache ages out entries (typically 1-20 minutes depending on OS), so idle entries disappear or show as STALE between the two runs - the next packet to that host triggers a fresh ARP exchange.

</details>

## 4. Cybersecurity Perspective

- **ARP spoofing/poisoning:** an attacker answers "who has the gateway?" with their own MAC, and separately tells the gateway *they* are the victim. Traffic now flows through the attacker - a man-in-the-middle on the LAN, enabling sniffing and tampering. Unsolicited replies ("gratuitous ARP") make this cheap: no waiting for a question.
- Signs: one IP claimed by 2 MACs; the gateway's MAC suddenly changing; bursts of replies without matching requests.
- Defences: Dynamic ARP Inspection (DAI) on managed switches, port security, static ARP entries for critical hosts, and monitoring (arpwatch).

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
