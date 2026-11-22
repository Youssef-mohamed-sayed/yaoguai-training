# Module 6 — Nmap

> Difficulty: Beginner → Intermediate

Nmap ("Network Mapper") discovers hosts, open ports and services. This module teaches you to **run** it, and — more importantly — to **interpret** it.

## ⚠️ Authorization

Scan **only**: your own machines, your own lab (e.g. VirtualBox host-only network `192.168.56.0/24`), CTF/training ranges, or systems where you have **explicit written permission**. (`scanme.nmap.org` may be lightly scanned per the Nmap project's published policy; read it first.) Unauthorised scanning can be illegal and can disrupt services.

## Lessons

1. [Introduction](introduction.md): what Nmap is, recon, the workflow
2. [Host Discovery](host-discovery.md): `-sn`
3. [Port Scanning](port-scanning.md): default scan, `-p`, `-p-`, `-sS`, `-sT`, `-sU`
4. [Service & Version Detection](service-detection.md): `-sV`, `-O`, `-A`
5. [Reading Results](reading-results.md): interpretation exercises

## Lab Setup

- Install Nmap: <https://nmap.org/download>
- Create a safe target: a VM (e.g. Metasploitable-style or any Linux VM you own) on a host-only network, or run a local web server: `python3 -m http.server 8000` and scan `127.0.0.1`.

## Lab 4 — Nmap

Complete the practical task at the end of every lesson against your lab target and keep notes in a file.

- [ ] Module complete
