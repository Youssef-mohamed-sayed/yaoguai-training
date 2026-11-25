# OSI vs TCP/IP

> Difficulty: Beginner

## What You Will Learn

- Why two layering models exist and how they line up
- Translating fluently between OSI numbers and TCP/IP names
- Which model actually runs your network (and which one people talk in)

## Why This Matters in Cybersecurity

Reports use OSI numbers ("Layer 7 attack", "L3/L4 filtering"); tools and documentation use TCP/IP structure. Misreading the layer means misreading the finding: a "Layer 4" issue is about ports and connections, a "Layer 7" issue is about application content like HTTP. You must translate between the two without thinking.

## 1. Core Concept

```text
OSI                         TCP/IP
7 Application   ┐
6 Presentation  ├─────────► Application
5 Session       ┘
4 Transport     ──────────► Transport
3 Network       ──────────► Internet
2 Data Link     ┐
1 Physical      ┴─────────► Network Access
```

| Aspect | OSI | TCP/IP |
|--------|-----|--------|
| Layers | 7 | 4 |
| Nature | Reference/teaching model | Real protocol suite |
| Application stuff | Split in 3 layers | One layer |
| Origin | ISO standard (1984) | Grew with the actual Internet |

**Why keep both?** History. TCP/IP won the implementation war - nothing on the wire "is OSI". But OSI's finer split turned out to be a better *vocabulary*, so the industry kept OSI's numbering for conversation and TCP/IP's structure for engineering. When someone says "Layer 2 switch" or "Layer 7 WAF" they are speaking OSI about TCP/IP networks.

A rough phrase for each layer, bottom to top: wires and signals (L1), local delivery with MAC addresses (L2), routing between networks with IPs (L3), end-to-end connections with ports (L4), then everything applications say to each other (L5-7, folded into TCP/IP "Application").

### Mini Task 1

OSI Layer 3 maps to which TCP/IP layer? OSI Layer 5?

<details>
<summary>Check Your Answer</summary>

Internet; Application.

</details>

### Mini Task 2

A colleague says "the firewall is Layer 3 only". What can it filter on, and what can it not see?

<details>
<summary>Check Your Answer</summary>

It can filter on IP addresses (and generally Layer 4 ports), but it cannot understand application content - it cannot block a specific URL, username, or command inside the traffic, because those live at Layer 7.

</details>

## 2. Practical Example

"The firewall inspects Layer 7" means it understands application content (e.g. HTTP URLs), not just IPs and ports.

### Exercise

Classify as OSI layer number and TCP/IP layer: (a) MAC address, (b) TCP port, (c) HTTP header.

<details>
<summary>Check Your Answer</summary>

(a) L2, Network Access. (b) L4, Transport. (c) L7, Application.

</details>

## 3. Cybersecurity Perspective

When an alert says "L3/L4 filtering", expect IP/port rules. "L7" implies deep inspection (WAF, proxy). Attack classification follows the same vocabulary: a SYN flood is a Layer 4 attack (connection state exhaustion), an HTTP flood or SQL injection is Layer 7 (valid-looking application requests), and ARP spoofing is Layer 2 (local network only). Knowing the layer tells you the blast radius and the right defense.

## 4. Common Mistakes

Treating OSI layers 5 and 6 as separate things you can see in Wireshark. They are folded into "Application" in practice.

## 5. CTF Challenge

**Title:** Translate the Report
**Difficulty:** Easy
**Scenario:** An incident report says: "Attacker sent forged packets at Layer 4 to exhaust server connections."
**Objective:** Identify the TCP/IP layer name.
**Task:** Flag = lowercase TCP/IP layer name for OSI Layer 4.
**Flag format:** `FLAG{layername}`

<details>
<summary>Show Hints</summary>

- Hint 1: Use the mapping diagram.

</details>

<details>
<summary>Show Solution</summary>

OSI L4 = Transport. Flag: `FLAG{transport}`

</details>

## Summary

OSI teaches; TCP/IP runs. OSI's 7 numbers are the industry's shared vocabulary ("Layer 7 attack", "Layer 2 switch") even though real networks follow TCP/IP's 4-layer structure. Map L1-2 to Network Access, L3 to Internet, L4 to Transport, L5-7 to Application.

## What To Learn Next

[Encapsulation](encapsulation.md)
