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

## 3. Practical Example / Exercise

Wireshark filters: `tcp`, `udp`. Run `nslookup example.com` and capture it. Which transport does the query use and what is the destination port?

## 4. Cybersecurity Perspective

- TCP scan result is decided by handshake responses.
- UDP closed ports return ICMP "port unreachable"; silence = `open|filtered`.
- UDP-based amplification (DNS, NTP) is used in DDoS.

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

TCP = reliable, connection-based. UDP = fast, connectionless.

## What To Learn Next

[The TCP Three-Way Handshake](tcp-handshake.md)
