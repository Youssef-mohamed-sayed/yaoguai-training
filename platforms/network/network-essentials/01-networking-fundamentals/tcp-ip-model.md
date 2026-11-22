# The TCP/IP Model

> Difficulty: Beginner

## What You Will Learn

- The 4-layer TCP/IP model the Internet actually uses
- Where common protocols sit

## Why This Matters in Cybersecurity

Wireshark's packet details pane is organised by these layers. Knowing them tells you what each section means.

## 1. Introduction

TCP/IP is the **practical** model behind the Internet. It has 4 layers (some books use 5 by splitting the bottom one).

## 2. Core Concept

| TCP/IP Layer | Job | Protocols |
|--------------|-----|-----------|
| Application | User-facing services | HTTP, HTTPS, DNS, DHCP, FTP, SSH |
| Transport | Process-to-process delivery (ports) | TCP, UDP |
| Internet | Addressing and routing | IPv4, IPv6, ICMP |
| Network Access (Link) | Local delivery on the medium | Ethernet, Wi-Fi, ARP |

```text
Application    ← what you see (HTTP)
Transport      ← ports (TCP 443)
Internet       ← IP addresses
Network Access ← MAC addresses, cables, Wi-Fi
```

### Mini Task 1

Which TCP/IP layer is each protocol in? `UDP`, `IPv4`, `DNS`, `Ethernet`

<details>
<summary>Check Your Answer</summary>

UDP → Transport, IPv4 → Internet, DNS → Application, Ethernet → Network Access.

</details>

## 3. How It Works

Each layer adds its own **header** to the data. At the destination each layer removes its header. See [Encapsulation](encapsulation.md).

### Mini Task 2

In Wireshark you see the rows `Ethernet II`, `Internet Protocol Version 4`, `Transmission Control Protocol`, `Hypertext Transfer Protocol`. Write the TCP/IP layer for each.

<details>
<summary>Check Your Answer</summary>

Network Access, Internet, Transport, Application.

</details>

## 4. Practical Example / Exercise

Run `curl -I http://example.com` (a site you may legitimately request). Identify: the application protocol (HTTP), the transport protocol (TCP), and the likely port (80).

## 5. Cybersecurity Perspective

Firewalls, IDS and scanners are described by layer: "port scan" = Transport, "DNS tunnelling" = Application.

## 6. Common Mistakes

Saying "TCP/IP is only TCP and IP". It is a whole suite of protocols.

## 7. CTF Challenge

**Title:** Layer Spotter
**Difficulty:** Easy
**Scenario:** A capture shows: Ethernet → IPv4 → UDP → DNS.
**Objective:** Count the TCP/IP layers present and name the Transport protocol.
**Provided information:** Protocol stack above.
**Task:** Flag = number of TCP/IP layers shown, underscore, transport protocol in lowercase.
**Flag format:** `FLAG{N_protocol}`

<details>
<summary>Show Hints</summary>

- Hint 1: Match each item to a layer from the table.
- Hint 2: The model has 4 layers; are all 4 represented?

</details>

<details>
<summary>Show Solution</summary>

Ethernet = Network Access, IPv4 = Internet, UDP = Transport, DNS = Application → 4 layers, transport is udp.

Flag: `FLAG{4_udp}`

</details>

## Summary

TCP/IP = Application, Transport, Internet, Network Access.

## What To Learn Next

[OSI vs TCP/IP](osi-vs-tcpip.md)
