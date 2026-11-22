# Network Topologies

> Difficulty: Beginner

## What You Will Learn

- How devices can be arranged: star, bus, ring, mesh, hybrid
- Pros, cons and failure behaviour of each

## Why This Matters in Cybersecurity

Topology decides what an attacker (or you, when sniffing) can see, how failures spread, and which links are chokepoints worth monitoring.

## 1. Introduction

**Topology** = the layout of how devices connect. *Physical* = cables/devices; *logical* = how data flows.

## 2. The Topologies

### Star (most common today)

```text
        PC
         |
PC ---- Switch ---- PC
         |
       Server
```
- ✔ Easy to add devices, one cable failure affects one device
- ✘ Switch is a single point of failure
- Seen: almost every office/home LAN

### Bus

```text
PC ──┬──────┬──────┬── PC
     │      │      │
    PC     PC   Server   (single shared cable)
```
- ✔ Cheap, little cable
- ✘ Cable break splits the network; collisions; poor security (everyone hears everything)
- Seen: legacy Ethernet, some industrial buses (e.g. CAN in vehicles)

### Ring

```text
 PC ── PC
 |      |
 PC ── PC   (each device connects to two neighbours)
```
- ✔ Predictable performance
- ✘ One break can disrupt the ring unless dual-ring
- Seen: older token ring, metro fibre rings (SONET/FDDI-style)

### Mesh

```text
A ───── B
│ \   / │
│   X   │
│ /   \ │
C ───── D     (full mesh: every node linked to every other)
```
- ✔ Very resilient, multiple paths
- ✘ Expensive and complex (full mesh links = n(n−1)/2)
- Seen: Internet core, WAN links, Wi-Fi mesh systems, data centres

### Hybrid

```text
        [Core Switch]
        /    |     \
   [SW1]   [SW2]   [Router]──(mesh to other sites)
   / | \   / | \
  PCs      Servers
```
- Combination of the above; typical in real enterprises.

### Mini Task 1

Which topology has a central switch? Which is the most resilient? How many links does a full mesh of 5 nodes need?

<details>
<summary>Check Your Answer</summary>

Star; mesh; 5 × 4 / 2 = 10 links.

</details>

## 3. Failure Scenarios

| Topology | What breaks | Impact |
|----------|-------------|--------|
| Star | Central switch dies | Everyone offline |
| Star | One cable dies | One device offline |
| Bus | Main cable break | Network split/offline |
| Ring | One node/link fails | Possible ring outage |
| Mesh | One link fails | Traffic reroutes |

### Mini Task 2

In a star network the switch fails. How could a design remove that single point of failure?

<details>
<summary>Check Your Answer</summary>

Redundant switches/links (e.g. two switches, link aggregation, spanning tree).

</details>

## 4. Practical Exercise

Draw your home or lab network (modem, router, switch, AP, devices). Label the topology and mark the single points of failure. Optional: use `traceroute` to see hops to a public host.

## 5. Cybersecurity Perspective

- Star with a switch: sniffing others' traffic needs a mirror port, ARP spoofing, or other access.
- Bus/hub networks: every host sees all frames.
- Mesh and hybrid: more routes → more places to monitor and more places an attacker can pivot.
- Chokepoints (core switch, gateway) are ideal for IDS/firewall placement.

## 6. Common Mistakes

Confusing physical layout with logical flow (Wi-Fi star physically, logically shared medium).

## 7. CTF Challenge

**Title:** Draw the Network
**Difficulty:** Easy
**Scenario:** Diagram:
```text
PC1 ──┐
PC2 ──┼── SW1 ── Firewall ── Router ── Internet
PC3 ──┘
```
**Objective:** Identify topology and single point of failure.
**Task:** Flag = topology name (lowercase), underscore, number of PCs that lose access if SW1 fails.
**Flag format:** `FLAG{topology_n}`

<details>
<summary>Show Hints</summary>

- Hint 1: Devices connect to a central switch.
- Hint 2: All PCs reach the network through SW1.

</details>

<details>
<summary>Show Solution</summary>

Star topology; SW1 failure disconnects all 3 PCs.

Flag: `FLAG{star_3}`

</details>

## Summary

Star, bus, ring, mesh and hybrid trade cost, resilience and security visibility.

## What To Learn Next

[Module 6 — Nmap](../06-nmap/README.md)
