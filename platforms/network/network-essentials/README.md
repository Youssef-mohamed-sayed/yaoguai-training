# Network Essentials

Learn networking from zero to cybersecurity fundamentals.

> Difficulty: Beginner → Intermediate | Format: read → try → check → practice → CTF

## Introduction

This course teaches how networks work **and** how to inspect them like a security professional. You will calculate subnets by hand, scan authorized targets with **Nmap**, and read traffic in **Wireshark**. Every lesson follows the same loop:

```text
Simple explanation → Small example → Mini task → Check understanding
        → Deeper explanation → Hands-on task → CTF challenge
```

## Prerequisites

- None in networking. Basic comfort with a terminal helps.
- A computer (Linux, macOS or Windows) where you can install Nmap and Wireshark.
- A **lab**: your own machines, a VM network (VirtualBox/VMware host-only), or a CTF platform.

## ⚠️ Authorization Rule (applies to the whole course)

Scan and capture **only**:

- your own machines,
- local lab environments you built,
- CTF/training environments,
- systems where you have **explicit written authorization**.

Scanning or sniffing networks you do not own or have permission to test can be illegal. Never guess "it's probably fine".

## Learning Objectives

By the end you can: explain OSI/TCP-IP; calculate subnets; recognise HTTP, DNS, DHCP, FTP, SSH, ARP, ICMP on the wire; explain the TCP handshake; run and interpret Nmap scans; capture and filter traffic in Wireshark; separate **discovery** from **vulnerability**; solve beginner reconnaissance CTFs.

## Recommended Order

Follow the modules top to bottom. Each builds on the previous one.

| # | Module | Lessons |
|---|--------|---------|
| 1 | [Networking Fundamentals](01-networking-fundamentals/README.md) | [OSI](01-networking-fundamentals/osi-model.md), [TCP/IP](01-networking-fundamentals/tcp-ip-model.md), [OSI vs TCP/IP](01-networking-fundamentals/osi-vs-tcpip.md), [Encapsulation](01-networking-fundamentals/encapsulation.md) |
| 2 | [Addressing](02-addressing/README.md) | [IPv4](02-addressing/ipv4.md), [MAC](02-addressing/mac-addresses.md), [Subnetting](02-addressing/subnetting.md), [ARP](02-addressing/arp.md) |
| 3 | [Common Protocols](03-protocols/README.md) | [HTTP/HTTPS](03-protocols/http-https.md), [DNS](03-protocols/dns.md), [DHCP](03-protocols/dhcp.md), [FTP](03-protocols/ftp.md), [SSH](03-protocols/ssh.md), [ARP](03-protocols/arp.md), [ICMP](03-protocols/icmp.md) |
| 4 | [Ports & TCP](04-ports-and-tcp/README.md) | [Ports & Services](04-ports-and-tcp/ports-and-services.md), [TCP vs UDP](04-ports-and-tcp/tcp-vs-udp.md), [Handshake](04-ports-and-tcp/tcp-handshake.md) |
| 5 | [Devices & Topologies](05-network-devices/README.md) | [Topologies](05-network-devices/network-topologies.md) |
| 6 | [Nmap](06-nmap/README.md) | [Intro](06-nmap/introduction.md), [Host Discovery](06-nmap/host-discovery.md), [Port Scanning](06-nmap/port-scanning.md), [Service Detection](06-nmap/service-detection.md), [Reading Results](06-nmap/reading-results.md) |
| 7 | [Wireshark](07-wireshark/README.md) | [Intro](07-wireshark/introduction.md), [Capturing](07-wireshark/capturing-packets.md), [Filters](07-wireshark/display-filters.md), [Streams](07-wireshark/following-streams.md), [Protocol Analysis](07-wireshark/protocol-analysis.md), [Reading Captures](07-wireshark/reading-captures.md) |
| 8 | [Final Challenges](08-final-challenges/README.md) | [01](08-final-challenges/challenge-01.md), [02](08-final-challenges/challenge-02.md), [03](08-final-challenges/challenge-03.md) |

## Course Progress

- [ ] Networking Fundamentals
- [ ] IP Addressing
- [ ] Subnetting
- [ ] Common Protocols
- [ ] Ports & TCP
- [ ] Network Devices & Topologies
- [ ] Nmap
- [ ] Wireshark
- [ ] Packet Analysis
- [ ] Final Challenges

## Challenge Format

Every CTF challenge has: Title, Difficulty, Scenario, Objective, Provided information, Task, Hints (progressive), Flag format, Hidden solution. Try before opening hints; try hints one at a time before the solution.

## How This Course Connects to Security

| Skill | Used in |
|-------|---------|
| Subnetting, scanning | Recon, pentesting, vulnerability assessment |
| Packet reading | SOC analysis, incident response, forensics |
| Protocol knowledge | Threat hunting, malware analysis, web security |
| All of it | CTFs |

This is an **analysis** course, not an exploitation course.
