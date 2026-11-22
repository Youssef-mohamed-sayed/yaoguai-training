# Introduction to Wireshark

> Difficulty: Beginner

## What You Will Learn

- What packet capture is and what a packet is
- Why packet analysis matters
- The three-pane Wireshark interface

## Why This Matters in Cybersecurity

Packets are ground truth. Logs can be wrong or missing; a capture shows what really happened. Used in SOC work, incident response, forensics, malware analysis and CTFs.

## 1. Introduction

A **packet** is a small chunk of data with headers, sent across a network. **Packet capture** (pcap) records those packets as they pass your network interface. **Wireshark** captures and decodes them into readable fields. (Command-line sibling: `tshark`; tcpdump captures too.)

> Analogy: A security camera for the network cable.

File types: `.pcap`, `.pcapng`.

## 2. The Interface

```text
┌──────────────────────────────────────────────┐
│ Display filter bar:  [ tcp.port == 80      ]  │
├──────────────────────────────────────────────┤
│ 1. PACKET LIST                                │
│ No. Time   Source   Destination Protocol Info │
├──────────────────────────────────────────────┤
│ 2. PACKET DETAILS (expandable layers)         │
│  ▸ Frame  ▸ Ethernet  ▸ IPv4  ▸ TCP  ▸ HTTP   │
├──────────────────────────────────────────────┤
│ 3. PACKET BYTES (hex + ASCII)                 │
└──────────────────────────────────────────────┘
```

| Pane | Shows |
|------|-------|
| Packet List | One row per packet: number, relative time, src, dst, protocol, summary |
| Packet Details | Decoded layers (outermost → innermost) |
| Packet Bytes | Raw hex and ASCII |

Colour rules: e.g. light blue UDP/DNS, light green HTTP, black/red errors, TCP SYN/RST often highlighted. Colours help but are not authoritative.

### Mini Task 1

Which pane shows raw hex? Which shows the Ethernet/IP/TCP layers?

<details>
<summary>Check Your Answer</summary>

Packet Bytes; Packet Details.

</details>

## 3. Practical Example

Open any sample `.pcapng` (e.g. one you captured yourself or from the Wireshark sample captures page). Click a TCP packet. In the Details pane expand Ethernet → IPv4 → TCP. Find the source IP, destination port and flags.

### Exercise

What is the first line (layer) in the Details pane for every packet, and what does it describe?

<details>
<summary>Check Your Answer</summary>

`Frame N`: metadata of the captured frame (length, capture time, interface). Not on the wire.

</details>

## 4. Cybersecurity Perspective

- IR/forensics: reconstruct events from pcaps.
- SOC: confirm alerts (is this DNS query really to a bad domain?).
- Malware analysis: observe beacons and C2 patterns.
- Web security: see actual requests/headers.
- Privacy: captures may contain credentials and personal data. Protect them.

## 5. Common Mistakes

- Capturing on the wrong interface and seeing nothing.
- Believing Wireshark decodes everything (encrypted payloads stay encrypted).

## 6. CTF Challenge

**Title:** Pane Master
**Difficulty:** Easy
**Scenario:** You need to read the raw ASCII payload of one packet.
**Objective:** Pick the right pane.
**Task:** Flag = pane number (1/2/3 as numbered in this lesson) and its name in lowercase with underscores.
**Flag format:** `FLAG{n_name}`

<details>
<summary>Show Hints</summary>

- Hint 1: ASCII appears next to hex.

</details>

<details>
<summary>Show Solution</summary>

Pane 3, packet bytes. Flag: `FLAG{3_packet_bytes}`

</details>

## Summary

Wireshark = capture + decode. Three panes: list, details, bytes.

## What To Learn Next

[Capturing Packets](capturing-packets.md)
