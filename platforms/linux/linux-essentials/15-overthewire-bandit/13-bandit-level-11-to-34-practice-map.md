# Bandit Levels 11–34: Verified Practice Map


## Purpose
This file maps later Bandit themes to Linux concepts without inventing exact level objectives or credentials. Use the official level page for the exact current task before attempting a challenge. The official site links each level and explains how to proceed.

## Concept practice sequence
The following are study themes commonly encountered as you progress through the later Bandit range. They are not substitutes for the official challenge text.

| Theme | Practice before opening the level |
|---|---|
| Character substitution / ROT-style transformation | Practice `tr`, character sets, and recognizing that a simple substitution is not encryption with a secret key |
| Hexadecimal and binary inspection | Practice `xxd`, `od`, `file`, and reading a hex dump |
| Compression and archives | Practice `gzip`, `bzip2`, `tar`, and `file`; learn to identify nested formats |
| SSH key authentication | Generate an Ed25519 key pair and connect to a disposable SSH account |
| Network services and ports | Practice `ss`, `nc` against localhost, and understand TCP client/server roles |
| TLS-protected services | Read `openssl s_client` help and understand certificate verification |
| Process and scheduled-task inspection | Practice `ps`, `systemctl`, `journalctl`, and read-only inspection of cron configuration |
| Setuid behavior | Revisit the special-permissions lesson; inspect metadata without attempting unauthorized escalation |
| Git repositories | Practice `git clone`, `git log`, `git branch`, `git show`, and `git tag` on your own repository |
| Shell behavior and restricted environments | Study quoting, built-ins, job control, and the difference between a shell and a command |

## How to approach each later level
1. Open the official page for the current transition.
2. Rewrite the goal in your own words without copying the page.
3. Identify the likely Linux concept.
4. Read relevant manual pages.
5. Use progressive experiments in your own lab where possible.
6. Keep credentials out of notes and reports.
7. Confirm success using the official game flow.

## Safe local practice commands
```bash
printf 'Uryyb
' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
printf 'sample' | xxd
tar -czf sample.tar.gz sample-dir/
gzip -l sample.tar.gz
ss -tuln
git log --oneline --all
```
These examples demonstrate transformations, byte inspection, archives, sockets, and Git history. They are standalone practice commands, not claims about a specific Bandit level.

## Official level navigation
Use the official [Bandit game](https://overthewire.org/wargames/bandit/) and its left-side level navigation for Levels 11 onward. If a level's exact condition cannot be confirmed, do not infer it from third-party writeups.

## Key takeaways
The later game reinforces the same habits: inspect, identify, read documentation, form a hypothesis, and test it carefully.
