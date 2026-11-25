# TCP and UDP: The socket Module

## Learning Objectives

- Explain what a socket is and how TCP differs from UDP.
- Create both socket types and resolve hostnames.
- Send and receive raw bytes with correct encoding and timeouts.

## Introduction

A **socket** is the operating system's endpoint for network communication - the thing a program sends bytes into and reads bytes out of. Everything higher-level (HTTP, SSH, DNS) is a convention about what those bytes mean. Working at the socket level teaches you what `requests` and browsers do underneath, and it is how banners are grabbed, services are fingerprinted, and custom protocols are spoken.

**TCP** (`SOCK_STREAM`) is a connection: reliable, ordered, with a handshake. Like a phone call - web, SSH, and email run on it. **UDP** (`SOCK_DGRAM`) is fire-and-forget datagrams: no connection, no guarantee, minimal overhead - DNS, VoIP, and games prefer speed over certainty.

## TCP: Connect, Send, Receive

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)                          # never block forever
s.connect(("example.com", 80))           # TCP handshake happens here
s.sendall(b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n")

data = b""
while True:
    chunk = s.recv(4096)
    if not chunk:                        # b"" means the peer closed
        break
    data += chunk
s.close()
print(data.decode(errors="replace")[:200])
```

```text
HTTP/1.0 200 OK
Content-Type: text/html
...
```

Points that bite beginners:

- Sockets move **bytes**, so encode on send (`"text".encode()`) and decode on receive.
- HTTP needs `\r\n\r\n` to end the headers and a `Host` header (HTTP/1.1 requires it).
- `recv(n)` returns **up to** n bytes; you loop until it returns empty. There is no "read the whole response" call - TCP is a stream with no built-in message boundaries.

## UDP and Name Resolution

UDP has no connect handshake; you address every datagram:

```python
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(3)
s.sendto(b"\x00", ("8.8.8.8", 53))       # (not a valid DNS query, just the shape)
```

Resolution turns names into addresses - the first step of any scanner:

```python
print(socket.gethostbyname("example.com"))        # 93.184.216.34
print(socket.gethostbyname_ex("example.com"))     # (name, aliases, [all IPs])
```

And `connect_ex`, seen in module 01, is the port-scanner primitive: it returns 0 on success instead of raising.

## The with Statement and Cleanup

Sockets hold OS resources. `with socket.socket(...) as s:` closes reliably, and for servers (next lesson) `s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` avoids "address already in use" after restarts.

## Common Mistakes

- No `settimeout`: one silent host freezes the script forever.
- Assuming one `recv` gets the whole reply; streams need a read loop.
- Sending str instead of bytes (`TypeError: a bytes-like object is required`).
- Scanning hosts without authorization - the lesson-01 rules apply to every socket you open.

## Key Takeaways

- TCP (`SOCK_STREAM`) is a reliable connected stream; UDP (`SOCK_DGRAM`) is connectionless datagrams.
- Encode/decode at the boundary, always set timeouts, and loop `recv` until it returns empty bytes.
- `gethostbyname` resolves names; `connect_ex` returns a status code and is the scanner's building block.

## Practice Exercises

**Exercise 1.** Grab the HTTP response headers from `example.com` port 80 with a raw TCP socket and print only the status line.

<details>
<summary>Show a worked solution</summary>

```python
import socket

with socket.create_connection(("example.com", 80), timeout=5) as s:
    s.sendall(b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n")
    data = s.recv(4096)
print(data.decode(errors="replace").splitlines()[0])
```

```text
HTTP/1.0 200 OK
```

`create_connection` combines socket creation, timeout, and connect in one call.
</details>

**Exercise 2.** Resolve three hostnames of your choice with `gethostbyname`, handling `socket.gaierror` for a name that does not exist.

<details>
<summary>Show a worked solution</summary>

```python
import socket

for name in ("example.com", "scanme.nmap.org", "no-such-host.invalid"):
    try:
        print(name, "->", socket.gethostbyname(name))
    except socket.gaierror:
        print(name, "-> does not resolve")
```
</details>

**Exercise 3.** Check whether ports 22, 80, 443, and 8080 are open on `scanme.nmap.org` using `connect_ex`, with a 1.5s timeout each.

<details>
<summary>Show a worked solution</summary>

```python
import socket

for port in (22, 80, 443, 8080):
    s = socket.socket()
    s.settimeout(1.5)
    print(port, "open" if s.connect_ex(("scanme.nmap.org", port)) == 0 else "closed")
    s.close()
```

```text
22 open
80 open
443 closed
8080 closed
```
</details>

## Check Yourself

**What does an empty bytes return from `recv` mean?**

<details>
<summary>Show answer</summary>

The peer closed the connection - end of stream. Your read loop should stop.
</details>

**Why does UDP not need `connect` before `sendto`?**

<details>
<summary>Show answer</summary>

UDP is connectionless: each datagram carries its destination address independently, with no handshake or session.
</details>

**Why is `connect_ex` nicer than `connect` for port scanning?**

<details>
<summary>Show answer</summary>

It returns an error code instead of raising, so closed ports are data (nonzero result) rather than exceptions to catch in a tight loop.
</details>
