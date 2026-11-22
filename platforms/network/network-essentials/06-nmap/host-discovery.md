# Host Discovery with Nmap

> Difficulty: Beginner

## What You Will Learn

- `-sn` (ping scan / host discovery)
- CIDR scan ranges
- What Nmap actually checks and how to read it

## Why This Matters in Cybersecurity

Step 1 of every assessment: *which devices exist?* (asset inventory, rogue device detection).

## 1. The Command

```bash
nmap -sn 192.168.56.0/24
```

```text
nmap           → the program
-sn            → host discovery only (no port scan; older name "-sP")
192.168.56.0/24→ target range: 256 addresses, .0 to .255 (see Subnetting)
```

### What Nmap Actually Does

- **On your local subnet** (as root/admin): sends **ARP requests** and records replies (very reliable, also gives MAC addresses).
- **Across routers**: sends ICMP echo, TCP SYN to 443, TCP ACK to 80, and ICMP timestamp. Any reply marks the host as "up".
- Hosts that block all probes can look down even when up.

### Sample Output

```text
Starting Nmap 7.9x ( https://nmap.org ) at 2026-11-21 10:00 EET
Nmap scan report for 192.168.56.1
Host is up (0.00030s latency).
MAC Address: 0A:00:27:00:00:00 (Unknown)
Nmap scan report for 192.168.56.20
Host is up (0.00061s latency).
MAC Address: 08:00:27:3C:9A:11 (Oracle VirtualBox virtual NIC)
Nmap scan report for 192.168.56.30
Host is up (0.0011s latency).
MAC Address: DC:A6:32:44:55:66 (Raspberry Pi Trading)
Nmap scan report for 192.168.56.101
Host is up.
Nmap done: 256 IP addresses (4 hosts up) scanned in 2.1 seconds
```

### Interpretation

- 256 addresses probed, **4 responded**.
- "Host is up" = at least one probe got an answer, nothing more.
- MAC vendor gives hints (VM, Raspberry Pi), not proof.
- The last host (no MAC line) is your own machine.

### Mini Task 1

What does `/24` mean here? What does `-sn` *not* do?

<details>
<summary>Check Your Answer</summary>

24 network bits → 256 addresses (254 usable). It does not scan ports.

</details>

## 2. More Variations

```bash
nmap -sn 192.168.56.20          # one host
nmap -sn 192.168.56.20-40       # a range
nmap -sn 192.168.56.0/28        # 16 addresses
nmap -Pn 192.168.56.20          # skip discovery; treat host as up (useful if ping is blocked)
```
`-Pn` = "no ping": assume up and go straight to port scan.

### Mini Task 2 — Command completion

```bash
nmap ______ 10.0.0.0/28       # discover hosts only
```
How many addresses does that range contain?

<details>
<summary>Check Your Answer</summary>

`-sn`; 16 addresses (14 usable).

</details>

## 3. Practical Task (Lab)

1. Determine your subnet with `ip addr` / `ipconfig` (Lab 1).
2. Run `nmap -sn <your-subnet>` on **your own** network or lab.
3. List each host's IP, MAC and vendor. Identify devices you can't explain, and decide if they are expected.

## 4. Cybersecurity Perspective

- Unknown host = possible rogue device or shadow IT.
- Compare against an asset list regularly.
- Attackers do this first, so detecting sweeps (many ARP/ICMP from one source) is a blue-team skill.

## 5. Common Mistakes

- Scanning too wide (/16 when you meant /24).
- Reading "down" as "nonexistent".

## 6. CTF Challenge

**Title:** Who's Home?
**Difficulty:** Easy
**Scenario:** Use the sample output above (lab network `192.168.56.0/24`).
**Objective:** Count live hosts and find the Raspberry Pi.
**Task:** Flag = number of hosts up, underscore, IP of the Raspberry Pi device.
**Flag format:** `FLAG{N_ip}`

<details>
<summary>Show Hints</summary>

- Hint 1: Last line of the scan summarises hosts up.
- Hint 2: Read the MAC vendor in parentheses.

</details>

<details>
<summary>Show Solution</summary>

4 hosts up; the Raspberry Pi Trading MAC belongs to 192.168.56.30.

Flag: `FLAG{4_192.168.56.30}`

</details>

## Summary

`nmap -sn` finds live hosts via ARP (local) or probes (remote). "Up" is not "vulnerable".

## What To Learn Next

[Port Scanning](port-scanning.md)
