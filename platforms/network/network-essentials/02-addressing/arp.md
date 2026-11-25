# ARP — Linking IP to MAC

> Difficulty: Beginner

## What You Will Learn

- Why ARP exists
- How IP ↔ MAC resolution works
- The ARP cache

(Full protocol analysis is in [Protocols → ARP](../03-protocols/arp.md).)

## Why This Matters in Cybersecurity

ARP has no authentication. Understanding it explains local-network attacks and how to detect them.

## 1. Introduction

Two addressing systems operate at once on your LAN: **IP addresses** route packets across networks, but the final delivery on the local segment happens inside **Ethernet frames**, which are addressed by **MAC addresses**. Your PC knows the destination IP (from DNS or config) but cannot transmit until it knows which network card to address. **ARP** (Address Resolution Protocol) bridges that gap by asking the local network: "Who has this IP?"

> Analogy: Shouting in a room, "Who is Alice?" and Alice replying "I am, here is my desk."

Every IP packet your PC sends on the LAN - to a local host or to the gateway for forwarding - goes through this resolution first. Without ARP, IP and Ethernet could not cooperate.

## 2. Core Concept

```text
PC A (192.168.1.50)                       All hosts on LAN
   │ ARP Request (broadcast ff:ff:ff:ff:ff:ff):
   │   "Who has 192.168.1.1? Tell 192.168.1.50"
   │ ───────────────────────────────────────────►
   │ ARP Reply (unicast to A):
   │   "192.168.1.1 is at aa:bb:cc:dd:ee:01"
   │ ◄───────────────────────────────────────────
```

Results are stored in the **ARP cache** for a short time (typically 1-20 minutes). The cache is the reason your PC does not broadcast for every single packet - and the attack surface, because entries are accepted without any authentication. A forged reply that arrives last simply overwrites the truth.

### Mini Task 2

Why does a host ARP again for an address it resolved an hour ago?

<details>
<summary>Check Your Answer</summary>

The cache entry expired. ARP entries are deliberately short-lived so that changed hardware or readdressed hosts are picked up automatically - the cost is periodic re-broadcasting.

</details>

### Mini Task 1

Is an ARP request unicast or broadcast? And ARP works across routers: true or false?

<details>
<summary>Check Your Answer</summary>

Broadcast. False: ARP stays inside the local network.

</details>

## 3. Practical Example — Lab: View Your ARP Cache

```bash
arp -a        # Windows, macOS, many Linux
ip neigh      # Linux
```
Sample:
```text
? (192.168.1.1) at aa:bb:cc:dd:ee:01 on eth0
```
Now `ping 192.168.1.1` (your own gateway) then run it again and observe entries.

**Exercise 2.** Flush the cache (`sudo ip neigh flush all` on Linux), ping your gateway once, and check the table immediately. How many ARP exchanges did one ping need?

<details>
<summary>Check Your Answer</summary>

One: the first ping packet triggers a single request/reply pair for the gateway, and every packet after it uses the cached entry. Subsequent pings need no ARP at all until the entry expires.

</details>

### Exercise

For a destination **outside** your subnet, whose MAC does your PC ARP for?

<details>
<summary>Check Your Answer</summary>

The default gateway's MAC (it ARPs for the gateway IP).

</details>

## 4. Cybersecurity Perspective

Any host can claim any IP ("ARP spoofing/poisoning"), enabling man-in-the-middle on a LAN. Defences: Dynamic ARP Inspection, static entries for critical hosts, monitoring for duplicate IP→MAC changes.

## 5. Common Mistakes

Thinking ARP is part of IP. It is a separate helper protocol (often placed at L2/L3 boundary).

## 6. CTF Challenge

**Title:** Who Has It?
**Difficulty:** Easy
**Scenario:** Your `arp -a` shows `192.168.1.1 at aa:bb:cc:dd:ee:01` and `192.168.1.77 at aa:bb:cc:dd:ee:01`.
**Objective:** Explain what is suspicious.
**Task:** Flag = the shared MAC, uppercase, no colons.
**Flag format:** `FLAG{MAC}`

<details>
<summary>Show Hints</summary>

- Hint 1: Two IPs, one MAC. Is that normal for a router? For an attacker?
- Hint 2: A gateway and a normal host sharing a MAC can indicate poisoning (or a legitimate proxy ARP setup).

</details>

<details>
<summary>Show Solution</summary>

Both entries show MAC `aa:bb:cc:dd:ee:01`. Not proof of attack, but worth investigating.

Flag: `FLAG{AABBCCDDEE01}`

</details>

## Summary

ARP maps IP → MAC on the local network via broadcast request and unicast reply.

## What To Learn Next

[Module 3 — Common Protocols](../03-protocols/README.md)
