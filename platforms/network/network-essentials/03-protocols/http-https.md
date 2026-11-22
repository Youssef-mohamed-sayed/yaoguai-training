# HTTP and HTTPS

> Difficulty: Beginner

## What You Will Learn

- How web requests/responses work
- Why HTTPS exists and what it protects
- How to read HTTP on the wire

## Why This Matters in Cybersecurity

Most attack surface today is web. HTTP is also the favourite channel for malware C2 and data exfiltration because it blends in.

## 1. Introduction

**HTTP** (HyperText Transfer Protocol) lets a client (browser) request resources from a server. **HTTPS** is HTTP wrapped in **TLS** encryption.

Problem solved: a standard way to fetch pages/APIs. HTTPS adds confidentiality, integrity and server authentication.

| | HTTP | HTTPS |
|--|------|-------|
| Layer | 7 | 7 over TLS (6/7) |
| Default port | 80 | 443 |
| Transport | TCP | TCP |
| Encrypted | No | Yes |

## 2. How It Works

```text
Client ──TCP handshake──► Server:80
Client: GET /index.html HTTP/1.1
        Host: shop.lab.local
Server: HTTP/1.1 200 OK
        Content-Type: text/html
        <html>...</html>
```

Request = method + URI + headers (+ body). Response = status code + headers (+ body).

| Method | Use |
|--------|-----|
| GET | Retrieve |
| POST | Send data (forms, login) |
| PUT/DELETE | Modify/remove (APIs) |

| Status | Meaning |
|--------|---------|
| 200 | OK |
| 301/302 | Redirect |
| 401/403 | Unauthorized/Forbidden |
| 404 | Not found |
| 500 | Server error |

### Mini Task 1

Fill in: HTTPS default port is ____. A 404 means ____. The `Host` header names the ____.

<details>
<summary>Check Your Answer</summary>

443; the resource was not found; the website/domain requested (needed for virtual hosting).

</details>

## 3. Example Packets

```text
POST /login HTTP/1.1
Host: portal.lab.local
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=alice&password=Hello1
```
With plain HTTP, anyone on the path can read this. With HTTPS, Wireshark shows only the TLS handshake (Client Hello shows the server name) and encrypted "Application Data".

### Mini Task 2

In the request above: method? URI? Which header gives the site name? Is the password protected?

<details>
<summary>Check Your Answer</summary>

POST; `/login`; `Host`; no, it's plain text.

</details>

## 4. Practical Example / Exercise

```bash
curl -v http://example.com/
```
`curl` = request tool; `-v` = verbose, shows request and response headers. Identify method, host, status code and server header.

**Nmap:** `80/tcp open http`, `443/tcp open ssl/http`. **Wireshark filters:** `http`, `tls`, `tcp.port == 80`.

## 5. Cybersecurity Perspective

- Cleartext HTTP: credentials, cookies exposed (sniffing).
- Headers leak software versions (`Server: Apache/2.4.57`).
- Web attacks (injection, XSS, broken auth) ride on HTTP(S).
- HTTPS hides content from observers, but defenders also can't inspect it without TLS inspection. Metadata (IPs, SNI, timing) remain visible.
- Misconfigurations: expired/self-signed certs, mixed content, no HSTS, directory listing.

## 6. Common Mistakes

"HTTPS means the site is safe." It means the *connection* is encrypted, not that the site is trustworthy.

## 7. CTF Challenge

**Title:** Login Trace
**Difficulty:** Easy
**Scenario:** You captured this exchange on an authorised lab.
**Objective:** Summarise the request and response.
**Provided information:**
```text
POST /login HTTP/1.1
Host: portal.lab.local
...
HTTP/1.1 302 Found
Location: /dashboard
```
**Task:** Flag = method, URI and status code, joined by underscores.
**Flag format:** `FLAG{METHOD_/uri_code}`

<details>
<summary>Show Hints</summary>

- Hint 1: First line of the request has the method and URI.
- Hint 2: First line of the response has the code.

</details>

<details>
<summary>Show Solution</summary>

Method POST, URI /login, response 302 (redirect to /dashboard, suggesting login success).

Flag: `FLAG{POST_/login_302}`

</details>

## Summary

HTTP = request/response over TCP 80; HTTPS = HTTP inside TLS on 443.

## What To Learn Next

[DNS](dns.md)
