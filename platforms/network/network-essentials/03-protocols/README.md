# Module 3 — Common Protocols

> Difficulty: Beginner → Intermediate

A **protocol** is an agreed set of rules for communication. Each lesson answers the same questions: what it is, what problem it solves, layer, port, transport, how it works, example messages, security issues, how it looks in Nmap/Wireshark, and a small exercise.

| Protocol | Layer | Port | Transport | Lesson |
|----------|-------|------|-----------|--------|
| HTTP | 7 | 80 | TCP | [http-https](http-https.md) |
| HTTPS | 7 (+TLS) | 443 | TCP | [http-https](http-https.md) |
| DNS | 7 | 53 | UDP (and TCP) | [dns](dns.md) |
| DHCP | 7 | 67/68 | UDP | [dhcp](dhcp.md) |
| FTP | 7 | 21 (+data) | TCP | [ftp](ftp.md) |
| SSH | 7 | 22 | TCP | [ssh](ssh.md) |
| ARP | 2/3 | none | — (own EtherType) | [arp](arp.md) |
| ICMP | 3 | none | — (IP protocol 1) | [icmp](icmp.md) |

**Important distinctions** (memorise):

```text
IP address = which host (L3)       MAC address = which interface on the link (L2)
Port       = which service slot (L4)   Service  = the program listening on a port
Protocol   = the rules spoken       Socket   = IP address + port (+ protocol)
```
Example socket: `192.168.1.10:443/tcp`.

> Lab safety: capture and scan only your own lab or authorised systems.

- [ ] Module complete
