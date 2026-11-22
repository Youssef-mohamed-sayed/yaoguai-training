# Bandit Introduction and SSH Setup


## Learning objectives
- Explain the purpose and rules of Bandit.
- Connect to the game using SSH.
- Use hints and notes without relying on published credentials.

## What is OverTheWire?
OverTheWire hosts wargames that teach security concepts through hands-on tasks. Bandit is aimed at beginners and focuses on Linux command-line skills required for later wargames.

Official game: [https://overthewire.org/wargames/bandit/](https://overthewire.org/wargames/bandit/)

## Connection
The official Bandit page currently lists:
- Host: `bandit.labs.overthewire.org`
- Port: `2220`
- Starting account: `bandit0`

The initial password and current connection instructions are provided by the official game. Verify them on the official site rather than relying on copied notes. Connect with:
```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
```
When prompted about a host key, verify the fingerprint using the official information or a trusted channel before accepting. Do not disable host-key verification.

## How levels work
You begin at level 0. A level page describes how to obtain access to the next level. The password discovered during a level is used as the next account's password. Credentials can change; this course intentionally does not store passwords.

## A disciplined approach
1. Read the official level goal carefully.
2. List files, including hidden files.
3. Identify file types before assuming they are text.
4. Read relevant manual pages.
5. Try the smallest command that tests your current hypothesis.
6. Record the command, observation, explanation, and any useful general lesson.
7. Use hints in increasing order; open a solution only after a genuine attempt.

## Notes template
```text
Level:
Goal in my own words:
What I inspected:
Commands tried:
Important output (redact credentials):
Hint used:
Why the successful method works:
Linux concept learned:
Next question:
```

## Troubleshooting
- `Could not resolve hostname`: DNS or network issue.
- `Connection timed out`: outbound firewall, routing, or service availability.
- `Connection refused`: verify host and port.
- `Permission denied`: username/password or authentication issue.
- Broken pipe in some VM NAT setups: consult the official Bandit notes and your VM networking documentation; do not weaken SSH verification.

## Practice
Connect to the official game, complete the first login, then continue to the first level-to-level exercise. Keep passwords out of screenshots, public writeups, and shared course indexes.

## References
- [Official Bandit page](https://overthewire.org/wargames/bandit/)
- [OpenSSH manual](https://www.openssh.com/manual.html)
