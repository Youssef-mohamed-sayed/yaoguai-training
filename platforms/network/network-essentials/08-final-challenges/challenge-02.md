# Challenge 2 — Quiet Resolver

> Difficulty: Medium | Modules used: 3 (DNS), 4, 7

**Title:** Quiet Resolver
**Difficulty:** Medium

## Scenario

A SOC alert says host `192.168.56.50` sends unusual DNS queries. You have an authorised lab capture excerpt.

## Objective

Determine whether the queries are suspicious and recover the data hidden in them.

## Provided Information

```text
No. Time   Source          Destination    Proto Info
1   0.00   192.168.56.50   192.168.56.1   DNS   Standard query A www.lab.local
2   0.01   192.168.56.1    192.168.56.50  DNS   Response www.lab.local A 192.168.56.20
3   5.02   192.168.56.50   192.168.56.1   DNS   Standard query A 2.735f74346c6b73.t.lab.example
4   5.03   192.168.56.50   192.168.56.1   DNS   Standard query A 1.464c41477b646e.t.lab.example
5   5.04   192.168.56.50   192.168.56.1   DNS   Standard query A 3.5f6d7563687d.t.lab.example
6   5.05   192.168.56.1    192.168.56.50  DNS   Response (NXDOMAIN) x3
```

## Task

1. Which transport protocol and port carry these packets?
2. Which queries are normal and which are suspicious, and why?
3. Order the suspicious queries by their first label (the sequence number), concatenate the second labels, and decode the hex to text.

**Flag format:** `FLAG{...}` (the decoded text)

## Hints

<details>
<summary>Show Hints</summary>

- **Hint 1:** Packets 1–2 are an ordinary lookup. Packets 3–5 use strange subdomains and return NXDOMAIN.
- **Hint 2:** The first label (1, 2, 3) is a sequence number; packets arrive out of order.
- **Hint 3:** The middle label is hexadecimal. Join chunks 1, 2, 3.
- **Hint 4:** `echo <hex> | xxd -r -p` converts hex to text.

</details>

## Solution

<details>
<summary>Show Solution</summary>

1. DNS = UDP port 53.
2. Packets 1–2 are normal. Packets 3–5 are suspicious: sequence-numbered hex-like subdomains of an unusual zone, all NXDOMAIN, resembling **DNS tunnelling/exfiltration**.
3. Order: 1 → `464c41477b646e`, 2 → `735f74346c6b73`, 3 → `5f6d7563687d`. Joined: `464c41477b646e735f74346c6b735f6d7563687d`.
```bash
echo 464c41477b646e735f74346c6b735f6d7563687d | xxd -r -p
```
Output: `FLAG{dns_t4lks_much}`

Flag: `FLAG{dns_t4lks_much}`

Defender takeaways: monitor DNS query length/entropy, NXDOMAIN rates and unusual domains; restrict outbound DNS to approved resolvers.

</details>

## Summary

DNS can carry hidden data. Anomalies: odd names, repeated queries, NXDOMAIN bursts.
