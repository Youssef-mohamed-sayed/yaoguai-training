# Packet and Protocol Analysis

> Difficulty: Intermediate

## What You Will Learn

- Inspect a packet layer by layer
- Find the TCP handshake in a capture
- Recognise DNS, HTTP, ICMP, ARP on the wire

## Why This Matters in Cybersecurity

Alerts say "suspicious traffic". This lesson teaches you to open the packet and prove what happened.

## 1. Layer by Layer

```text
Ethernet
    ↓
IPv4
    ↓
TCP
    ↓
HTTP
```

| Layer | Fields to find | Wireshark filter field |
|-------|----------------|------------------------|
| Ethernet | Source MAC, Destination MAC, EtherType (0x0800 IPv4, 0x0806 ARP) | `eth.src`, `eth.dst`, `eth.type` |
| IPv4 | Source IP, Destination IP, TTL, Protocol (6 TCP, 17 UDP, 1 ICMP) | `ip.src`, `ip.dst`, `ip.ttl`, `ip.proto` |
| TCP | Source/Dest port, Seq, Ack, Flags, Window size | `tcp.srcport`, `tcp.dstport`, `tcp.seq`, `tcp.ack`, `tcp.flags`, `tcp.window_size` |
| HTTP | Method, URI, Host, Headers, Status | `http.request.method`, `http.request.uri`, `http.host`, `http.response.code` |
| DNS | Query name, type, answers | `dns.qry.name`, `dns.a` |

### Mini Task 1 — Identify

A packet has EtherType 0x0800, IP protocol 17, destination port 53. Which protocol stack is it?

<details>
<summary>Check Your Answer</summary>

Ethernet / IPv4 / UDP / DNS.

</details>

## 2. TCP Handshake Exercise

Capture a connection to a lab web server, filter `tcp.port == 80`. Example capture:

```text
No.  Source              Destination         Proto Info
1    192.168.56.101      192.168.56.20       TCP   51514 → 80 [SYN] Seq=0 Win=64240
2    192.168.56.20       192.168.56.101      TCP   80 → 51514 [SYN, ACK] Seq=0 Ack=1 Win=65160
3    192.168.56.101      192.168.56.20       TCP   51514 → 80 [ACK] Seq=1 Ack=1 Win=64240
4    192.168.56.101      192.168.56.20       HTTP  GET / HTTP/1.1
```

Fill in a table: for each of packets 1–3 identify Source IP, Destination IP, Source Port, Destination Port, TCP flags, Seq, Ack, and what it means.

<details>
<summary>Check Your Answer</summary>

| # | Src IP:port | Dst IP:port | Flags | Seq | Ack | Meaning |
|---|-------------|-------------|-------|-----|-----|---------|
| 1 | 192.168.56.101:51514 | 192.168.56.20:80 | SYN | 0 (relative) | – | Client asks to open a connection |
| 2 | 192.168.56.20:80 | 192.168.56.101:51514 | SYN, ACK | 0 | 1 | Server accepts, says it expects client byte 1 |
| 3 | 192.168.56.101:51514 | 192.168.56.20:80 | ACK | 1 | 1 | Client confirms: connection established |

Packet 4 is the first application data (HTTP GET). Wireshark shows relative sequence numbers (turn off at Edit → Preferences → Protocols → TCP → Relative sequence numbers to see raw ISNs).

</details>

Helpful filter: `tcp.flags.syn == 1` (SYN and SYN-ACK).

## 3. Protocol-Specific Exercises

### DNS

Filter `dns`. Find:

| Item | Where |
|------|-------|
| DNS query | `Standard query` row; Info shows `A example.com` |
| DNS response | `Standard query response`; same Transaction ID |
| Requested domain | Queries → Name |
| Returned IP | Answers → Address |

Expected pattern:
```text
10  192.168.56.101 → 192.168.56.1   DNS  Standard query 0x4f21 A www.lab.local
11  192.168.56.1 → 192.168.56.101   DNS  Standard query response 0x4f21 A www.lab.local A 192.168.56.20
```
**Task:** Requested domain? Returned IP? Transport and port?

<details>
<summary>Check Your Answer</summary>

`www.lab.local`; `192.168.56.20`; UDP, port 53.

</details>

### HTTP

Filter `http`. Find: request, method, Host header, URI, response, status code.
```text
GET /admin/login.php HTTP/1.1
Host: www.lab.local
...
HTTP/1.1 200 OK
```
**Task:** Method? Host? URI? Status?

<details>
<summary>Check Your Answer</summary>

GET; `www.lab.local`; `/admin/login.php`; 200.

</details>

### ICMP

Filter `icmp`. Echo request = Type 8, Echo reply = Type 0.
```text
21  192.168.56.101 → 192.168.56.20  ICMP  Echo (ping) request id=0x0001 seq=1 ttl=64
22  192.168.56.20 → 192.168.56.101  ICMP  Echo (ping) reply   id=0x0001 seq=1 ttl=64
```
**Task:** Which packet is the request? What links request and reply? 

<details>
<summary>Check Your Answer</summary>

Packet 21 (Type 8). The identifier and sequence number match.

</details>

### ARP

Filter `arp`. Find: request, reply, Sender IP/MAC, Target IP/MAC.
```text
5  08:00:27:aa:aa:01 → ff:ff:ff:ff:ff:ff  ARP  Who has 192.168.56.20? Tell 192.168.56.101
6  08:00:27:bb:bb:02 → 08:00:27:aa:aa:01  ARP  192.168.56.20 is at 08:00:27:bb:bb:02
```
**Task:** In packet 6: Sender IP, Sender MAC, Target IP, Target MAC?

<details>
<summary>Check Your Answer</summary>

Sender IP 192.168.56.20, Sender MAC 08:00:27:bb:bb:02, Target IP 192.168.56.101, Target MAC 08:00:27:aa:aa:01 (the original asker).

</details>

## 4. Cybersecurity Perspective

- Unusual TTLs, odd flags (e.g. SYN+FIN), or huge DNS names flag tooling and tunnels.
- Window size, retransmissions and RSTs hint at filtering or instability.
- The same fields appear in IDS rules, firewall logs and forensic timelines.

## 5. Common Mistakes

- Reading the Info column only and not expanding details.
- Missing that Wireshark shows *relative* sequence numbers by default.

## 6. CTF Challenge

**Title:** Reconstruct the Events
**Difficulty:** Medium
**Scenario:** Authorised lab capture (condensed):
```text
1  192.168.56.101 → 192.168.56.1    DNS   A intranet.lab.local
2  192.168.56.1 → 192.168.56.101    DNS   A intranet.lab.local → 192.168.56.40
3  192.168.56.101 → 192.168.56.40   TCP   49200 → 80 [SYN]
4  192.168.56.40 → 192.168.56.101   TCP   80 → 49200 [SYN, ACK]
5  192.168.56.101 → 192.168.56.40   TCP   49200 → 80 [ACK]
6  192.168.56.101 → 192.168.56.40   HTTP  GET /backup.zip HTTP/1.1
7  192.168.56.40 → 192.168.56.101   HTTP  HTTP/1.1 200 OK (application/zip)
```
**Objective:** Describe what happened.
**Task:** Flag = resolved IP, requested URI, response status, joined by underscores.
**Flag format:** `FLAG{ip_uri_status}`

<details>
<summary>Show Hints</summary>

- Hint 1: Packet 2 gives the IP.
- Hint 2: Packet 6 has the request line.
- Hint 3: Packet 7 has the status code.

</details>

<details>
<summary>Show Solution</summary>

Client resolved `intranet.lab.local` to 192.168.56.40, completed a TCP handshake to port 80, requested `/backup.zip` and received `200 OK`.

Flag: `FLAG{192.168.56.40_/backup.zip_200}`

</details>

## Summary

Inspect Ethernet → IP → TCP/UDP → application. Know the key fields per layer.

## What To Learn Next

[Reading Captures](reading-captures.md)
