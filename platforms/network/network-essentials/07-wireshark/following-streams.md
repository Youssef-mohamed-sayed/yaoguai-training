# Following Streams

> Difficulty: Intermediate

## What You Will Learn

- Follow TCP / UDP stream
- Reconstruct conversations
- Spot requests/responses and useful data

## Why This Matters in Cybersecurity

Individual packets are fragments. A stream shows the whole conversation: commands, credentials in cleartext protocols, downloaded files, malware beacons.

## 1. Core Concept

A **TCP stream** = all segments of one connection (identified by the 4-tuple: src IP, src port, dst IP, dst port). **Follow TCP Stream** reassembles the payload in order into readable text.

How: select a packet → right-click → **Follow → TCP Stream** (or Ctrl+Alt+Shift+T). Wireshark applies a filter like `tcp.stream eq 4`.

- **Red** text = client → server. **Blue** text = server → client (default colours).
- **Follow UDP Stream** works the same for UDP (e.g. DNS exchanges).
- Choose "Show as: ASCII / Hex dump" at the bottom.

### Mini Task 1

What four values define a TCP connection? What does `tcp.stream eq 4` select?

<details>
<summary>Check Your Answer</summary>

Source IP, source port, destination IP, destination port. The 5th TCP connection (stream numbering starts at 0).

</details>

## 2. Practical Example

Stream view of a cleartext HTTP exchange (lab server):
```text
GET /notes.txt HTTP/1.1
Host: files.lab.local
User-Agent: curl/8.5.0

HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 22

meeting at 10:00, room 4
```

### Exercise — The 5-Step Method

1. **Find** a packet (e.g. filter `http.request`).
2. **Identify** its TCP connection (look at src/dst IP and ports).
3. **Follow** the stream.
4. **Read** the conversation: who speaks first? What is the request? What is the response?
5. **Extract** important information (resource, status, headers, content, credentials).

Try it on your Lab 5 `curl http://example.com` capture. Answer: Which method, host, status code, and what's the first HTML tag in the body?

<details>
<summary>Check Your Answer</summary>

GET, `example.com`, `200`, `<!doctype html>` (or `<html>`), unless the site redirects.

</details>

## 3. Cybersecurity Perspective

- Cleartext protocols (HTTP, FTP, Telnet) expose everything; use SFTP/HTTPS.
- Malware C2: repeated short streams to the same host (beaconing).
- Incident response: reconstruct what a user downloaded or what a web shell returned.
- Encrypted streams (TLS/SSH) appear as unreadable data: you can analyse size/timing, not content.

## 4. Common Mistakes

- Following a stream from a packet in the wrong connection.
- Forgetting to clear the filter afterwards (`Clear` button) before looking at another stream.

## 5. CTF Challenge

**Title:** Read the Conversation
**Difficulty:** Medium
**Scenario:** A followed TCP stream from an authorised lab FTP server:
```text
220 FTP Ready
USER tech
331 Password required
PASS Lab#2026
230 Logged in
RETR flag.txt
150 Opening data connection
226 Transfer complete
```
**Objective:** Identify the account and the file that was requested.
**Task:** Flag = username, password, filename joined by underscores.
**Flag format:** `FLAG{user_password_file}`

<details>
<summary>Show Hints</summary>

- Hint 1: `USER` and `PASS` are client commands.
- Hint 2: `RETR` means retrieve (download) a file.

</details>

<details>
<summary>Show Solution</summary>

User `tech`, password `Lab#2026`, file `flag.txt`.

Flag: `FLAG{tech_Lab#2026_flag.txt}`

</details>

## Summary

Follow Stream rebuilds the conversation from many packets: find → identify → follow → read → extract.

## What To Learn Next

[Protocol Analysis](protocol-analysis.md)
