# TCP vs UDP

> Difficulty: Beginner

## What You Will Learn

- The two main transport protocols
- When each is used
- How their behaviour affects scanning

## Why This Matters in Cybersecurity

TCP scans are fast and reliable; UDP scans are slow and ambiguous. Knowing why avoids misreading results.

## 1. Core Concept

> Analogy: TCP is a phone call (connect, confirm, hang up). UDP is posting a postcard (send and hope).

Both live at Layer 4 and use **ports** to hand data to the right application - that part is identical. Everything else is a trade-off. TCP spends extra packets and time buying guarantees: a connection (the three-way handshake), acknowledgment of every segment, retransmission of losses, and in-order delivery. UDP spends nothing and guarantees nothing: each datagram is independent, may be lost, duplicated, or arrive out of order, and nobody will tell you.

The practical reading: TCP moves data that must be complete and correct (web pages, files, logins). UDP moves data that must be *fast* or *simple* (a DNS lookup is one packet each way; a lost video frame is not worth a retransmit that arrives too late to show).

| Feature | TCP | UDP |
|---------|-----|-----|
| Connection | Yes (handshake) | No |
| Reliable delivery | Yes (ACKs, retransmit) | No |
| Ordering | Yes | No |
| Overhead | Higher | Lower |
| Speed | Slower | Faster |
| PDU | Segment | Datagram |
| Uses | Web, SSH, FTP, email | DNS, DHCP, VoIP, streaming, games |

### Mini Task 1

Which would you pick for a live voice call: TCP or UDP? Why? Name 2 TCP protocols.

<details>
<summary>Check Your Answer</summary>

UDP: low delay matters more than perfect delivery. TCP: HTTP, SSH, FTP, HTTPS (any two).

</details>

## 2. Header Comparison

```text
UDP header (8 bytes):  src port | dst port | length | checksum
TCP header (20+ bytes): src port | dst port | seq | ack | flags | window | checksum ...
```

The header sizes tell the design story. UDP's 8 bytes are just enough to deliver a datagram. TCP's 20+ bytes carry the machinery of reliability: sequence numbers (so bytes can be reordered and gaps detected), acknowledgment numbers (so the sender learns what arrived), flags (SYN/ACK/FIN/RST drive the connection lifecycle), and a window field for flow control.

### Mini Task 2

Why does a "reliable" protocol need sequence numbers at all?

<details>
<summary>Check Your Answer</summary>

IP can deliver packets out of order or lose them. Sequence numbers let the receiver reassemble bytes in order and notice a gap; the missing range is then re-requested via the ACK numbers.

</details>

## 3. Practical Example / Exercise

Wireshark filters: `tcp`, `udp`. Run `nslookup example.com` and capture it. Which transport does the query use and what is the destination port?

Then load any HTTPS page while capturing `tcp`. Before looking, predict the first three packets between your host and the server.

<details>
<summary>Check Your Answer</summary>

The DNS query uses UDP to destination port 53 (one request packet, one response packet). The HTTPS capture starts with SYN, SYN-ACK, ACK - the three-way handshake every TCP connection opens with, covered in the next lesson.

</details>

## 4. Cybersecurity Perspective

- TCP scan result is decided by handshake responses: SYN-ACK = open, RST = closed, silence = filtered.
- UDP scans are slow and ambiguous: closed ports usually return ICMP "port unreachable", but silence means `open|filtered` - the scanner cannot tell a listening service from a dropped packet, so Nmap retransmits and waits, which is why `-sU` crawls.
- UDP-based amplification (DNS, NTP) is used in DDoS: a small spoofed query yields a large answer aimed at the victim, and UDP's connectionlessness makes source spoofing trivial.

## 5. Common Mistakes

Believing UDP is "unreliable so unused". Much critical traffic (DNS, DHCP) uses it.

## 6. CTF Challenge

**Title:** Transport Detective
**Difficulty:** Easy
**Scenario:** Packet fields: src port 53014, dst port 53, 8-byte transport header, no flags field.
**Objective:** Identify the transport protocol and the likely application protocol.
**Task:** Flag = transport (lowercase), underscore, application protocol (lowercase).
**Flag format:** `FLAG{transport_app}`

<details>
<summary>Show Hints</summary>

- Hint 1: 8-byte header and no flags suggests the simpler protocol.
- Hint 2: Port 53 = ?

</details>

<details>
<summary>Show Solution</summary>

8-byte header, no flags → UDP. Port 53 → DNS.

Flag: `FLAG{udp_dns}`

</details>

## Summary

TCP = reliable, ordered, connection-based (20+ byte header, handshake, ACKs, retransmit). UDP = fast, connectionless (8-byte header, no guarantees). Choose TCP when correctness matters, UDP when latency or simplicity does - and expect UDP scan results to be inherently ambiguous.

## What To Learn Next

[The TCP Three-Way Handshake](tcp-handshake.md)
