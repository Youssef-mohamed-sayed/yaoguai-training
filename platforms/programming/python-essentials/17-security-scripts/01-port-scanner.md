# Building a TCP Port Scanner

## Learning Objectives

- Combine sockets, loops, and functions into a working port scanner.
- Add timeouts, concurrency limits, and clean output.
- Scope scanning to authorized targets only.

## Introduction

A port scanner asks one question per port: does a TCP connection succeed? You already own every piece - `connect_ex` (module 01), timeouts (module 15), argument parsing (module 12), aligned output (module 03). This lesson assembles them.

**Authorization first:** run this against `scanme.nmap.org` (provided by the Nmap project for testing), your own machines, or lab VMs. Nothing else, ever.

## The Core Loop

```python
import socket

def check_port(host, port, timeout=1.0):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0

def scan(host, ports):
    open_ports = []
    for port in ports:
        if check_port(host, port):
            open_ports.append(port)
    return open_ports
```

That is a complete scanner in ten lines. `connect_ex` returns 0 when the handshake completes; anything else (refused, filtered, timed out) counts as closed for this purpose.

## A Real Command-Line Tool

Wrap it with argparse and reporting:

```python
import argparse
import socket

def check_port(host, port, timeout=1.0):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0

SERVICES = {22: "ssh", 80: "http", 443: "https", 3306: "mysql", 3389: "rdp", 8080: "http-alt"}

def main():
    parser = argparse.ArgumentParser(description="Tiny authorized-use port scanner")
    parser.add_argument("host")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="port range, e.g. 1-1024 or 22,80,443")
    parser.add_argument("-t", "--timeout", type=float, default=1.0)
    args = parser.parse_args()

    if "-" in args.ports:
        lo, hi = args.ports.split("-")
        ports = range(int(lo), int(hi) + 1)
    else:
        ports = [int(p) for p in args.ports.split(",")]

    try:
        ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        parser.error(f"cannot resolve {args.host}")

    print(f"scanning {args.host} ({ip})")
    for port in ports:
        if check_port(ip, port, args.timeout):
            print(f"{port:>5}/tcp open  {SERVICES.get(port, 'unknown')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

```text
$ python3 scanner.py scanme.nmap.org -p 20-100
scanning scanme.nmap.org (45.33.32.156)
   22/tcp open  ssh
   80/tcp open  http
```

## Speed: Threads with a Bound

One port per second times 1000 ports is slow. Threads overlap the waiting; a `ThreadPoolExecutor` caps how many run at once:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=100) as pool:
    results = pool.map(lambda p: (p, check_port(ip, p)), ports)
open_ports = [p for p, ok in results if ok]
```

One hundred concurrent connection attempts is a reasonable default for a lab. Hundreds more is how you trip rate limits and IDS alerts - noisy scanning is an operational mistake, not a flex. Real tools (nmap) add timing templates, service detection, and SYN scanning; knowing the TCP-connect version's limits tells you why those exist.

## Common Mistakes

- No timeout per connection, so filtered ports stall the scan.
- Declaring a port "closed" when it is actually filtered (firewall dropped the packet) - a connect scanner cannot distinguish these well.
- Scanning without a worker cap and melting the target or your own network.
- Scanning anything you do not own or have written permission for.

## Key Takeaways

- `connect_ex` + timeout is the scanner primitive; loop it over a parsed port range.
- argparse, resolution checks, and aligned output turn the loop into a tool.
- Thread pools add speed; bounded concurrency keeps you polite and un-flagged.

## Practice Exercises

**Exercise 1.** Run the full scanner against `scanme.nmap.org` for ports 20-100 and record which are open.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 scanner.py scanme.nmap.org -p 20-100
scanning scanme.nmap.org (45.33.32.156)
   22/tcp open  ssh
   80/tcp open  http
```

(Exact results can change; 22 and 80 are the expected answers.)
</details>

**Exercise 2.** Add the threaded version and measure the speedup on the 1-500 range with `time`.

<details>
<summary>Show a worked solution</summary>

```text
$ time python3 scanner.py scanme.nmap.org -p 1-500          # sequential
real  1m12s
$ time python3 scanner_threaded.py scanme.nmap.org -p 1-500
real  0m6s
```

Numbers vary with timeout and latency; the order-of-magnitude gap is the point.
</details>

**Exercise 3.** Extend the scanner to print the total scan time and the count of open ports at the end.

<details>
<summary>Show a worked solution</summary>

```python
import time

start = time.perf_counter()
found = [p for p in ports if check_port(ip, p, args.timeout)]
elapsed = time.perf_counter() - start
for port in found:
    print(f"{port:>5}/tcp open  {SERVICES.get(port, 'unknown')}")
print(f"{len(found)} open ports in {elapsed:.1f}s")
```
</details>

## Check Yourself

**Why can a connect scanner not distinguish "closed" from "filtered"?**

<details>
<summary>Show answer</summary>

Both produce a failed connection (RST or silence/timeout). Distinguishing them needs raw-packet techniques (SYN scans) like nmap's.
</details>

**What does `ThreadPoolExecutor(max_workers=100)` bound?**

<details>
<summary>Show answer</summary>

The number of connection attempts in flight at once - concurrency is capped so neither the target nor your host is flooded.
</details>

**Which hosts may you scan with this tool?**

<details>
<summary>Show answer</summary>

Only ones you own or have explicit permission to test: scanme.nmap.org, your own machines, and lab VMs.
</details>
