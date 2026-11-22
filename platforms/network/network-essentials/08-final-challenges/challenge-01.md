# Challenge 1 — Operation Lantern

> Difficulty: Hard | Modules used: 2, 3, 4, 6, 7

**Title:** Operation Lantern
**Difficulty:** Hard

## Scenario

You are a junior analyst on an **authorised** lab assessment. Your analysis VM is on the lab network. You must map the network, find the web server, and read a captured exchange to recover a debug token left in an HTTP response.

## Objective

Recover the final flag by completing all stages.

## Provided Information

**Artifact A — your interface**
```text
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    link/ether 08:00:27:11:22:33 brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.101/27 scope global eth0
```

**Artifact B — host discovery**
```text
$ nmap -sn 192.168.56.96/27
Nmap scan report for 192.168.56.97
Host is up (0.00040s latency).
MAC Address: 0A:00:27:00:00:00 (Unknown)
Nmap scan report for 192.168.56.110
Host is up (0.00070s latency).
MAC Address: 08:00:27:AA:BB:10 (Oracle VirtualBox virtual NIC)
Nmap scan report for 192.168.56.122
Host is up (0.0012s latency).
MAC Address: 3C:2A:F4:00:12:22 (Brother Industries)
Nmap scan report for 192.168.56.101
Host is up.
Nmap done: 32 IP addresses (4 hosts up) scanned in 1.8 seconds
```

**Artifact C — service scans**
```text
$ nmap -sV 192.168.56.110
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u3 (protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.57 ((Debian))

$ nmap -sV 192.168.56.122
PORT     STATE SERVICE    VERSION
9100/tcp open  jetdirect?
```

**Artifact D — packet capture excerpt (condensed)**
```text
No. Source              Destination         Info
1   192.168.56.101      192.168.56.110      49200 → 80 [SYN] Seq=4000
2   192.168.56.110      192.168.56.101      80 → 49200 [SYN, ACK] Seq=9000 Ack=4001
3   192.168.56.101      192.168.56.110      49200 → 80 [ACK] Seq=4001 Ack=9001
4   192.168.56.101      192.168.56.110      GET /status HTTP/1.1  (Host: lab-web.local)
5   192.168.56.110      192.168.56.101      HTTP/1.1 200 OK
```
Follow-TCP-Stream output for packets 4–5:
```text
GET /status HTTP/1.1
Host: lab-web.local
User-Agent: curl/8.5.0

HTTP/1.1 200 OK
Server: Apache/2.4.57 (Debian)
X-Debug-Token: RkxBR3tuM3R3MHJrX3IzYzBuX200c3Qzcn0=
Content-Type: text/plain
Content-Length: 2

OK
```

## Task

Work through the stages. Each has a checkpoint; the final flag is produced in Stage 6.

1. **Network info:** From Artifact A, what are the network address and broadcast address of your subnet, and how many usable hosts?
2. **Discovery:** How many hosts other than yours are up? Which device is probably a printer, and why is that only a *guess*?
3. **Ports/services:** Which host runs the web service, and on which port/product?
4. **Handshake:** In Artifact D, what is the server's ISN and the Ack number in packet 3?
5. **Application layer:** What are the HTTP method, URI, status code, and the name of the unusual response header?
6. **Decode:** Decode the header value to get the flag.

**Flag format:** `FLAG{...}` (produced by Stage 6)

## Hints

<details>
<summary>Show Hints</summary>

- **Hint 1:** /27 → block size 32. Your host is .101, between .96 and .127.
- **Hint 2:** The MAC vendor of .122 (Brother) and port 9100 suggest a printer.
- **Hint 3:** The web service is on the host that has `http` in Artifact C.
- **Hint 4:** Packet 3's Ack = server ISN + 1.
- **Hint 5:** The header starts with `X-`.
- **Hint 6:** The value looks like Base64. Try `echo '<value>' | base64 -d`.

</details>

## Solution

<details>
<summary>Show Solution</summary>

**Stage 1 — subnet.** /27 = 5 host bits, block size 32. Multiples: 96, 128. .101 lies in 96–127.
- Network: `192.168.56.96`
- Broadcast: `192.168.56.127`
- Usable: `.97`–`.126` = 30 hosts

**Stage 2 — discovery.** 4 hosts up including yours → 3 others (.97, .110, .122). .122 has a Brother MAC and port 9100 open → likely a printer. It's a guess: MAC vendors and port numbers are hints, not proof.

**Stage 3 — scan.** .110 runs Apache httpd 2.4.57 on 80/tcp (and SSH on 22). That is discovery, not a vulnerability.

**Stage 4 — handshake.** SYN seq 4000 → SYN-ACK seq 9000 ack 4001 → ACK seq 4001 ack 9001. Server ISN = 9000; Ack in packet 3 = 9001.

**Stage 5 — HTTP.** Method GET, URI /status, status 200, header `X-Debug-Token`.

**Stage 6 — decode.**
```bash
echo 'RkxBR3tuM3R3MHJrX3IzYzBuX200c3Qzcn0=' | base64 -d
```
`base64 -d` decodes Base64 back to the original text.

Flag: `FLAG{n3tw0rk_r3c0n_m4st3r}`

</details>

## Summary

You combined subnetting, discovery, service identification, TCP analysis, HTTP reading and decoding: the full recon-and-analysis loop.
