# Display Filters

> Difficulty: Beginner → Intermediate

## What You Will Learn

- How to narrow a capture to what matters
- Core filters, operators and combinations

## Why This Matters in Cybersecurity

Real captures have thousands of packets. Filters are how you find the three that matter.

## 1. How Filters Work

Type in the filter bar; **green** = valid syntax, **red** = invalid. Press Enter.
Operators: `==` equals, `!=` not equals, `&&`/`and`, `||`/`or`, `!`/`not`, `contains`.

## 2. Core Filters

| Filter | Meaning |
|--------|---------|
| `ip.addr == 192.168.1.10` | Packets where the IP is **source or destination** |
| `ip.src == 192.168.1.10` | Packets **from** that IP |
| `ip.dst == 192.168.1.10` | Packets **to** that IP |
| `tcp` | Only TCP segments |
| `udp` | Only UDP datagrams |
| `icmp` | Only ICMP (ping etc.) |
| `dns` | DNS queries and responses |
| `http` | HTTP (cleartext) |
| `tcp.port == 80` | TCP where **either** port is 80 |
| `tcp.port == 443` | TCP where either port is 443 (HTTPS/TLS) |

Why `ip.addr` vs `ip.src`? A conversation has two directions. `ip.addr` catches both; `src`/`dst` restricts to one.

### Mini Task 1

Which filter shows only packets *sent by* 10.0.0.5? Which shows only traffic *to or from* port 443?

<details>
<summary>Check Your Answer</summary>

`ip.src == 10.0.0.5`; `tcp.port == 443`.

</details>

## 3. Combining and Refining

```text
ip.addr == 192.168.1.10 && tcp.port == 80       (host AND port)
dns || icmp                                     (either protocol)
!arp                                            (hide ARP)
http.request.method == "POST"                   (HTTP POSTs)
http.host contains "lab.local"                  (text match)
dns.qry.name contains "example"                 (DNS names)
tcp.flags.syn == 1 && tcp.flags.ack == 0        (initial SYNs)
tcp.flags.reset == 1                            (RSTs)
frame contains "password"                       (text anywhere in packet; lab data only)
```

### Mini Task 2 — Write the filter

1. HTTP traffic from 192.168.1.50.
2. DNS responses only (hint: `dns.flags.response == 1`).
3. All traffic except ARP and DNS.

<details>
<summary>Check Your Answer</summary>

1. `http && ip.src == 192.168.1.50`
2. `dns.flags.response == 1`
3. `!arp && !dns`

</details>

## 4. Practical Exercise

Open your Lab 5 capture and answer using filters only:

1. How many DNS packets? (Status bar shows "Displayed".)
2. Which IP did `example.com` resolve to?
3. Which source port did your `curl` use?

Tip: right-click any field → **Apply as Filter** → **Selected** to build filters without typing.

## 5. Cybersecurity Perspective

- Hunt scans: `tcp.flags.syn == 1 && tcp.flags.ack == 0` with many destination ports from one IP.
- Hunt exfiltration: large uploads, `http.request.method == "POST"`.
- Odd DNS: very long `dns.qry.name`.
- RST bursts: closed/blocked ports or aborted sessions.

## 6. Common Mistakes

- `ip.addr == A && ip.addr == B` is valid but `ip.addr != A` behaves surprisingly; use `!(ip.addr == A)`.
- Confusing capture-filter syntax (`port 80`) with display-filter syntax (`tcp.port == 80`).

## 7. CTF Challenge

**Title:** Find the Needle
**Difficulty:** Medium
**Scenario:** A pcap has 10,000 packets. You need only DNS queries (not responses) from 10.0.0.20 to the resolver.
**Objective:** Write the correct combined filter.
**Task:** The correct filter is `dns && ip.src == 10.0.0.20 && dns.flags.response == 0`. Flag = number of `&&` operators in it, underscore, the value after the last `==`.
**Flag format:** `FLAG{n_value}`

<details>
<summary>Show Hints</summary>

- Hint 1: Three conditions need two `&&`.
- Hint 2: Response flag is 0 for queries.

</details>

<details>
<summary>Show Solution</summary>

`dns && ip.src == 10.0.0.20 && dns.flags.response == 0` has 2 `&&` and last value 0.

Flag: `FLAG{2_0}`

</details>

## Summary

Filters narrow the view; learn `ip.addr`, `tcp.port`, protocol names, combine with `&&`, `||`, `!`.

## What To Learn Next

[Following Streams](following-streams.md)
