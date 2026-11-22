# Reading Nmap Results

> Difficulty: Intermediate

## What You Will Learn

- Interpreting output instead of just running commands
- Prioritising services for further enumeration
- What conclusions are valid, and which aren't

## Why This Matters in Cybersecurity

Tools produce data; analysts produce **judgement**. This lesson trains the judgement.

## 1. Reading Checklist

For every scan, ask:

1. Which hosts are up?
2. Which ports are **open**? Closed? Filtered?
3. Which **services**, and are they on expected ports?
4. Which **versions** (if any)?
5. What's *unusual* for this host's role?
6. What is **missing** (UDP not scanned, ports above 1000, no scripts, host blocking probes)?
7. What can I conclude, and what can I **not** conclude?

## 2. Worked Example

```text
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2
80/tcp   open  http    Apache httpd 2.4.57
3306/tcp open  mysql   MySQL 8.0
```

| Question | Answer |
|----------|--------|
| Open ports | 22, 80, 3306 |
| Services | SSH, HTTP (Apache), MySQL |
| Interesting | 3306: databases rarely need to be reachable from everywhere; 80: web apps have large attack surface |
| Missing | Web content, auth settings, UDP ports, other ports (only scanned a subset?), patch level |
| Does it prove Apache is vulnerable? | **No.** It identifies the version; vulnerability needs matching advisory + exposure + verification |

### Mini Task 1

Which conclusion is valid? (a) "The server is vulnerable to SQL injection." (b) "A MySQL service is reachable on this host." (c) "The SSH password is weak."

<details>
<summary>Check Your Answer</summary>

(b). The others require testing beyond a scan.

</details>

## 3. Exercise — Interpret

```text
Nmap scan report for 192.168.56.50
Host is up (0.0008s latency).
Not shown: 996 closed tcp ports (reset)
PORT     STATE    SERVICE    VERSION
21/tcp   open     ftp        vsftpd 3.0.5
22/tcp   open     ssh        OpenSSH 9.2p1 Debian 2+deb12u3
80/tcp   open     http       nginx 1.22.1
8080/tcp filtered http-proxy
```
Answer:

1. Open ports?
2. Which port is filtered, and what does that suggest?
3. Which cleartext service deserves a note?
4. Name two things you still don't know.

<details>
<summary>Check Your Answer</summary>

1. 21, 22, 80. 2. 8080: probes get no clear answer, likely a firewall rule. 3. FTP (cleartext, check anonymous access, in authorised lab). 4. Examples: web content/application behaviour, accounts/auth policy, UDP services, whether versions are patched, what's behind the filtered port.

</details>

## 4. Cybersecurity Perspective

Prioritisation (rough):

- Exposed admin/data services (RDP, SMB, databases)
- Cleartext protocols (FTP, Telnet, HTTP login)
- Web apps (enumerate content)
- Outdated versions (verify before claiming)

Then move to **further enumeration**: directory discovery, banner/header inspection, authenticated checks (with permission).

## 5. Common Mistakes

- Skipping the "what's missing" step.
- Reporting scan output as a finding.
- Assuming `filtered` = nothing there.

## 6. CTF Challenge

**Title:** First Move
**Difficulty:** Medium
**Scenario:** A lab server (authorised):
```text
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2
80/tcp   open  http    Apache httpd 2.4.57
3306/tcp open  mysql   MySQL 8.0
```
The web server is the intended public service; SSH is the admin channel. The database should be local-only per policy.
**Objective:** Identify the port that violates the exposure policy.
**Task:** Flag = that port and the word `exposed`, underscore-joined.
**Flag format:** `FLAG{port_exposed}`

<details>
<summary>Show Hints</summary>

- Hint 1: Compare each service to its stated role.
- Hint 2: Which service shouldn't be reachable from the network?

</details>

<details>
<summary>Show Solution</summary>

MySQL (3306) is reachable though it should be local-only. This is an **exposure/configuration issue**, not a proven exploit.

Flag: `FLAG{3306_exposed}`

</details>

## Summary

Read every scan with: what's open, what service, what's unusual, what's missing, what can't I claim.

## What To Learn Next

[Module 7 — Wireshark](../07-wireshark/README.md)
