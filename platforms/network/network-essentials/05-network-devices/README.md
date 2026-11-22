# Module 5 — Network Devices

> Difficulty: Beginner

Devices are the physical/logical machines that move and filter traffic. Next lesson: [Network Topologies](network-topologies.md).

## Device Overview

| Device | Primary layer | Works with | What it does | Everyday example | Security relevance |
|--------|---------------|-----------|--------------|------------------|--------------------|
| **Host** | All | — | Any device on a network | Laptop, phone | Endpoints are the targets |
| **Client** | 7 | — | Host that requests services | Browser | Phishing, malware |
| **Server** | 7 | IP+port | Host that provides services | Web server | Exposed services = attack surface |
| **Switch** | 2 | MAC addresses | Forwards frames only to the right port | Office LAN box | CAM flooding, VLAN hopping, port security |
| **Router** | 3 | IP addresses | Connects networks, picks routes | Home router | Routing tables, ACLs, default creds |
| **Firewall** | 3–7 | IP, ports, (apps) | Allows/blocks traffic by rules | Network or host firewall | Misconfigured rules, rule review |
| **Access Point (AP)** | 1–2 | Radio, MAC/SSID | Connects wireless clients to wired LAN | Wi-Fi AP | Rogue AP, weak Wi-Fi security |
| **Modem** | 1–2 | Signals | Converts ISP medium ↔ digital | Cable/DSL modem | Rarely managed; firmware issues |
| **Gateway** | 3+ | IP | Exit point to another network | "Default gateway" (often the router) | Key MITM target |
| **Proxy** | 7 | Requests/URLs | Makes requests on behalf of clients | Web/forward proxy | Filtering, logging, hiding origin |

Hub (legacy): repeats bits to all ports (Layer 1); a switch is smarter.

### Mini Task 1

Which device uses MAC addresses to forward? Which uses IP to choose a path? Which sits between your LAN and the Internet and often performs NAT?

<details>
<summary>Check Your Answer</summary>

Switch; router; router/gateway (home routers combine router + switch + AP + modem sometimes).

</details>

## How They Fit Together

```text
[Laptop]──┐
[Phone]───┤(Wi-Fi AP)
[Server]──┤
          └──[Switch]──[Firewall]──[Router/Gateway]──[Modem]──► Internet
```

### Mini Task 2

A frame arrives at a switch with destination MAC `aa:aa:aa:aa:aa:03`. The switch's table maps it to port 3. What does it do? What if the MAC is unknown?

<details>
<summary>Check Your Answer</summary>

Forwards only out port 3. If unknown it floods out all other ports (this is what CAM-table overflow attacks exploit).

</details>

## Cybersecurity Perspective

- **Segmentation:** VLANs and firewalls limit lateral movement.
- **Where to sniff:** a switch limits what you see; a SPAN/mirror port or hub-like setup is needed to capture others' traffic (on authorised networks only).
- **Logs:** firewall, router and proxy logs are core SOC evidence.
- **Hardening:** change default credentials, update firmware, restrict management interfaces.

## CTF Challenge

**Title:** Which Device Logged It?
**Difficulty:** Easy
**Scenario:** A log line: `ALLOW tcp 10.0.1.7:50122 -> 10.0.2.9:443`. Another: `port 4 learned aa:bb:cc:00:00:07`.
**Objective:** Identify the device types producing each log.
**Task:** Flag = first device (filters by IP/port), underscore, second device (learns MAC→port), both lowercase.
**Flag format:** `FLAG{device_device}`

<details>
<summary>Show Hints</summary>

- Hint 1: Allow/deny with IP and port = rule-based filter.
- Hint 2: MAC learning on numbered ports = a Layer 2 device.

</details>

<details>
<summary>Show Solution</summary>

Flag: `FLAG{firewall_switch}`

</details>

## Summary

Switches work with MACs (L2), routers with IPs (L3), firewalls with rules (L3–L7).

## What To Learn Next

[Network Topologies](network-topologies.md)
