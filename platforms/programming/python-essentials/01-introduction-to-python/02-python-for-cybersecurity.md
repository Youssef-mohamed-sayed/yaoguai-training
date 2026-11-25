# Python for Cybersecurity

## Learning Objectives

- Explain why Python became the default scripting language in security work.
- Name the categories of security tasks Python handles well, with one concrete example each.
- State the rules that keep practice legal and safe.

## Introduction

Ask a working penetration tester what they write quick tools in and the answer is almost always Python. The reasons are practical:

- **Speed of writing.** In a security engagement, the tool you need often has to exist *now*. A port scanner, a log parser, or a payload encoder is an afternoon of Python, not a week of C.
- **Batteries included.** The standard library already speaks HTTP, TCP, UDP, JSON, CSV, regular expressions, file compression, and process control. Many useful tools need no installation at all.
- **The ecosystem.** Scapy crafts packets, pwntools drives exploit development, impacket speaks Windows network protocols, and Volatility (memory forensics) and sqlmap are Python too. Standing on this ecosystem means most "new" tools are 50 lines, not 5,000.
- **Readable under pressure.** Incident response at 3 AM needs code you can still read. Python's plain syntax helps.

## What Security Work Looks Like in Python

**Reconnaissance and networking.** Sockets, DNS, and HTTP are a few lines each:

```python
import socket

host = "scanme.nmap.org"
for port in (22, 80, 443):
    s = socket.socket()
    s.settimeout(1.5)
    result = s.connect_ex((host, port))
    print(port, "open" if result == 0 else "closed")
    s.close()
```

```text
22 open
80 open
443 closed
```

`connect_ex` returns 0 when the connection succeeds, so this prints which ports answer. Module 15 covers sockets in depth.

**Log analysis and forensics.** Reading millions of lines, extracting the ones that matter, and counting them:

```python
failed = 0
with open("/var/log/auth.log") as log:
    for line in log:
        if "Failed password" in line:
            failed += 1
print("Failed logins:", failed)
```

**Exploitation and CTF work.** Sending exact bytes, encoding payloads, and scripting interactions with a target service. CTF platforms and tools like pwntools assume Python fluency.

**Automation.** The unglamorous majority of security work: checking 200 hosts for a stale certificate, verifying backup permissions, diffing firewall exports. Scripts do it consistently and leave a record.

## Rules of Engagement

The techniques in this course are the same ones used in authorized assessments, and the same ones prosecuted when used without permission. The rules are not optional:

1. **Only test systems you own or have written permission to test.** "Written" means a contract, scope document, or the published terms of a bug bounty or practice platform.
2. **Practice targets exist so you never need to touch anything real.** OverTheWire (Bandit), TryHackMe, HackTheBox, PicoCTF, and `scanme.nmap.org` all explicitly invite practice.
3. **Handle data you encounter responsibly.** A script that reads credentials, tokens, or personal data has the same obligations as a person reading them.

## Common Mistakes

- Copying an exploit script and running it against a random IP "to see if it works." That is unauthorized access in most jurisdictions, regardless of intent.
- Assuming a tool is safe because it is popular; read any script before running it with your credentials or against your network.
- Writing attack tooling with no logging, so you cannot reconstruct what it did afterward.

## Key Takeaways

- Python dominates security scripting because it is fast to write, has a huge ecosystem, and stays readable.
- Networking, log analysis, exploitation, and automation are the four big use categories; this course builds toward all of them.
- Authorization is the line between practice and a crime. Use the practice platforms, never arbitrary targets.

## Practice Exercises

**Exercise 1.** Run the port-check script above against `scanme.nmap.org` (a host Nmap provides for exactly this purpose). Add port 8080 to the list.

<details>
<summary>Show a worked solution</summary>

```python
import socket

host = "scanme.nmap.org"
for port in (22, 80, 443, 8080):
    s = socket.socket()
    s.settimeout(1.5)
    result = s.connect_ex((host, port))
    print(port, "open" if result == 0 else "closed")
    s.close()
```

```text
22 open
80 open
443 closed
8080 closed
```

Results can vary over time; the mechanism is what matters.
</details>

**Exercise 2.** Write a script that counts how many lines of a text file contain the word "error" (case-insensitive). Test it on any log or text file you have.

<details>
<summary>Show a worked solution</summary>

```python
count = 0
with open("app.log") as f:
    for line in f:
        if "error" in line.lower():
            count += 1
print("Lines containing 'error':", count)
```

Create a small `app.log` with a few mixed-case "Error"/"error" lines first so you can verify the count by hand.
</details>

**Exercise 3.** Look up the terms of service or rules page of one practice platform (OverTheWire, TryHackMe, or PicoCTF). Write down in one sentence what you are allowed to attack there.

<details>
<summary>Show a worked solution</summary>

For OverTheWire: you may attack only the game servers on the ports they publish, using the accounts the game gives you; attacking their other infrastructure or other players is forbidden. The exact wording matters more than this paraphrase; read it yourself.
</details>

## Check Yourself

**Why is `connect_ex` convenient for scanning compared to `connect`?**

<details>
<summary>Show answer</summary>

It returns an error code instead of raising an exception, so a closed port does not crash the loop; you just check for 0.
</details>

**Name the four broad categories of security work this lesson lists for Python.**

<details>
<summary>Show answer</summary>

Networking/reconnaissance, log analysis and forensics, exploitation and CTF work, and automation.
</details>

**A friend says "scanning is fine as long as you do not break anything." What is wrong with that?**

<details>
<summary>Show answer</summary>

Legality depends on authorization, not on whether damage occurs. Scanning or probing systems without permission can be an offense by itself.
</details>
