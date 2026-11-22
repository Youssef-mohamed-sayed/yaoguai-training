# DNS — Domain Name System

> Difficulty: Beginner

## What You Will Learn

- What DNS does and common record types
- How a lookup flows
- Lab: use `nslookup` / `dig`

## Why This Matters in Cybersecurity

DNS shows where hosts try to connect. Analysts hunt malware via suspicious domains; attackers abuse DNS (spoofing, tunnelling).

## 1. Introduction

Humans use names (`example.com`); networks use IPs. **DNS** translates names to IPs (the Internet's phonebook).

| Property | Value |
|----------|-------|
| Layer | 7 |
| Port | 53 |
| Transport | UDP for most queries; TCP for large responses/zone transfers |

## 2. Core Concept

| Record | Meaning |
|--------|---------|
| A | Name → IPv4 |
| AAAA | Name → IPv6 |
| CNAME | Alias to another name |
| MX | Mail server |
| NS | Authoritative name server |
| TXT | Free text (SPF, verification) |
| PTR | IP → name (reverse) |

Lookup flow:
```text
Browser → local cache → Resolver (e.g. router/ISP) → Root → TLD (.com) → Authoritative NS → answer
```

### Mini Task 1

Which record type maps a name to an IPv4 address? Which port does DNS use?

<details>
<summary>Check Your Answer</summary>

A; 53.

</details>

## 3. Example Messages

```text
Query:    Standard query 0x1a2b  A www.shop.example
Response: Standard query response 0x1a2b  A www.shop.example A 203.0.113.25
```
The **transaction ID** (0x1a2b) matches a response to its query.

## 4. Practical Example — Lab 3: DNS

```bash
nslookup example.com
dig example.com A
dig +short example.com
```
`nslookup` = simple lookup tool. `dig` = detailed tool; `A` = record type; `+short` = print only the answer. In `dig` output read: QUESTION (what you asked), ANSWER (the result), `SERVER` (which resolver answered).

### Exercise

Lookup the MX record for a domain you own or a public domain: `dig example.com MX`. What priority numbers appear?

**Nmap/Wireshark:** `53/udp open domain`; filter `dns` or `udp.port == 53`.

## 5. Cybersecurity Perspective

- DNS cache poisoning / spoofing redirects users.
- DNS tunnelling hides data in long, odd subdomains.
- Zone transfer (AXFR) misconfiguration leaks all records.
- Threat hunting: look for newly seen or algorithmically generated domains (DGA).
- Open resolvers can be abused for amplification attacks.

## 6. Common Mistakes

Thinking DNS is only UDP, or forgetting DNS answers can be cached (stale data).

## 7. CTF Challenge

**Title:** Where Did It Go?
**Difficulty:** Easy
**Scenario:** A host queried a suspicious name. A capture shows:
```text
192.168.1.50:53011 → 192.168.1.1:53  DNS query  A www.shop.example
192.168.1.1:53 → 192.168.1.50:53011  DNS response  www.shop.example A 203.0.113.25
```
**Objective:** Find what the client learned.
**Task:** Flag = the returned IP.
**Flag format:** `FLAG{ip}`

<details>
<summary>Show Hints</summary>

- Hint 1: Port 53 means DNS.
- Hint 2: Read the response line, not the query.

</details>

<details>
<summary>Show Solution</summary>

The response maps the name to 203.0.113.25.

Flag: `FLAG{203.0.113.25}`

</details>

## Summary

DNS maps names to data; UDP/TCP 53; A, AAAA, CNAME, MX, NS, TXT, PTR.

## What To Learn Next

[DHCP](dhcp.md)
