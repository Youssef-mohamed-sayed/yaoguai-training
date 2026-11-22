# Challenge 3 — The Man in the Middle

> Difficulty: Medium | Modules used: 2 (ARP/MAC), 3 (ARP, HTTP), 7

**Title:** The Man in the Middle
**Difficulty:** Medium

## Scenario

Users report odd behaviour on the router admin page (plain HTTP). You have an authorised lab capture and the asset inventory. The gateway `192.168.56.1` has MAC `08:00:27:aa:00:01`. The workstation `192.168.56.30` has MAC `08:00:27:cc:00:30`.

## Objective

Identify the attacker's MAC, the victim, and what credential was exposed.

## Provided Information

```text
No. Ethernet src → dst                      Info
1   08:00:27:cc:00:30 → ff:ff:ff:ff:ff:ff   ARP  Who has 192.168.56.1? Tell 192.168.56.30
2   08:00:27:aa:00:01 → 08:00:27:cc:00:30   ARP  192.168.56.1 is at 08:00:27:aa:00:01
3   08:00:27:de:ad:99 → 08:00:27:cc:00:30   ARP  192.168.56.1 is at 08:00:27:de:ad:99
4   08:00:27:de:ad:99 → 08:00:27:cc:00:30   ARP  192.168.56.1 is at 08:00:27:de:ad:99
--- later ---
5   08:00:27:cc:00:30 → 08:00:27:de:ad:99   IP 192.168.56.30 → 192.168.56.1  TCP 51022 → 80 [SYN]
6   08:00:27:cc:00:30 → 08:00:27:de:ad:99   IP 192.168.56.30 → 192.168.56.1  HTTP POST /admin/login
```
Follow-stream of packet 6:
```text
POST /admin/login HTTP/1.1
Host: 192.168.56.1
Content-Type: application/x-www-form-urlencoded

user=netadmin&pass=Lab-Only-1
```

## Task

1. Which MAC is making a false claim, and how do you know?
2. In packets 5–6 the IP destination is the gateway, but the Ethernet destination is not the gateway's MAC. What does that tell you?
3. Which account name was exposed?

**Flag format:** `FLAG{attackerMAC-no-colons-lowercase_victimIP_username}`

## Hints

<details>
<summary>Show Hints</summary>

- **Hint 1:** Compare ARP replies for 192.168.56.1 with the inventory MAC.
- **Hint 2:** Layer 3 destination = gateway; Layer 2 destination = who actually receives the frame.
- **Hint 3:** The victim is the host whose frames go to the wrong MAC.
- **Hint 4:** The username is in the POST body.

</details>

## Solution

<details>
<summary>Show Solution</summary>

1. Packet 2 matches the inventory; packets 3–4 claim the gateway IP with `08:00:27:de:ad:99` (unsolicited, repeated): ARP spoofing.
2. After poisoning, the victim sends frames meant for the gateway to the attacker's MAC, placing the attacker in the middle.
3. HTTP is cleartext, so the login (user `netadmin`) is exposed.

Flag: `FLAG{080027dead99_192.168.56.30_netadmin}`

Remediation: Dynamic ARP Inspection / port security, HTTPS for admin interfaces, rotate the exposed password, investigate the switch port of `08:00:27:de:ad:99`.

</details>

## Summary

ARP spoofing + cleartext HTTP = easy credential theft. Detect via ARP conflicts and mismatched L2/L3 destinations; prevent with encryption and Layer 2 controls.
