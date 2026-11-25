# The TCP/IP Model

> Difficulty: Beginner

## What You Will Learn

- The 4-layer TCP/IP model the Internet actually uses
- Where common protocols sit

## Why This Matters in Cybersecurity

Wireshark's packet details pane is organised by these layers. Knowing them tells you what each section means.

## 1. Introduction

TCP/IP is the **practical** model behind the Internet - the one your packets actually follow. It has 4 layers (some books use 5 by splitting the bottom one into Physical and Data Link).

A model is just a way of dividing labor. Each layer solves one problem and trusts the layer below to do its job: the application writes HTTP without caring about IP; IP routes without caring about cables; Ethernet delivers frames without caring what they contain. This separation is why a web page can cross fiber, Wi-Fi, and a satellite hop without the web server knowing the difference.

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

One addressing fact ties the bottom three layers together: a packet is guided by **three different addresses at three different layers** - the port says which program, the IP says which host, the MAC says which NIC on the current local hop. When you read a capture top-to-bottom you are reading all three at once, which is why the layers stop being abstract the first time you open Wireshark.

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

Then, for the same request, answer at each layer: which address identifies the web *program* on the server, which identifies the *machine*, and which would change if the packet crossed to a different router hop?

<details>
<summary>Check Your Answer</summary>

The destination port (80) identifies the program - Transport layer. The destination IP identifies the machine - Internet layer, and it stays constant end to end. The destination MAC identifies the next hop's NIC - Network Access layer, and it changes at every router along the path.

</details>

## 5. Cybersecurity Perspective

Firewalls, IDS and scanners are described by layer: "port scan" = Transport, "DNS tunnelling" = Application, "ARP spoofing" = Network Access, "IP spoofing" = Internet. The layer vocabulary tells you the blast radius and the right countermeasure before you know any other detail - an L2 attack needs switch-level defenses (DAI, port security), an L7 attack needs application-level ones (WAF, rate limits).

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
