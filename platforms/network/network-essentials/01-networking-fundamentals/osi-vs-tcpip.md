# OSI vs TCP/IP

> Difficulty: Beginner

## What You Will Learn

How the two models line up and why both are used.

## Why This Matters in Cybersecurity

Reports use OSI numbers ("Layer 7 attack"); tools use TCP/IP structure. You must translate between them.

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

### Mini Task 1

OSI Layer 3 maps to which TCP/IP layer? OSI Layer 5?

<details>
<summary>Check Your Answer</summary>

Internet; Application.

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

When an alert says "L3/L4 filtering", expect IP/port rules. "L7" implies deep inspection (WAF, proxy).

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

OSI teaches; TCP/IP runs. Know both.

## What To Learn Next

[Encapsulation](encapsulation.md)
