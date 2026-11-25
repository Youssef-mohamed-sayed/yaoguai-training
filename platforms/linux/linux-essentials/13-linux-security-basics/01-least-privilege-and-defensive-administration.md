# Least Privilege and Defensive Linux Administration


## Learning objectives
- Explain least privilege as a daily operating practice, not a slogan.
- Recognize the common privilege and configuration risks on a real host.
- Run a safe, evidence-based review workflow on systems you administer.

## Core concepts
Linux security is layered: identity, permissions, process isolation, kernel security features, network policy, package trust, service configuration, and monitoring all stack together. No single listing proves a host is secure; security is the *combined* effect, and weakness in one layer is often survivable because of the others. Your job as an administrator is to keep every layer boring and intentional.

Least privilege, as a working routine:

1. Use a regular account for routine work.
2. Elevate only the command that needs administration, only while it runs.
3. Give every service a dedicated account with only the access it needs.
4. Avoid broad sudo rules and shared credentials.
5. Remove obsolete accounts, keys, packages, and services through a controlled process.

## The defensive review toolkit
Run these on systems you administer or are explicitly authorized to audit:

```bash
id
sudo -l
getent passwd
getent group sudo
ss -tulpen
systemctl --type=service --state=running
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

What each answers:

- `sudo -l`: exactly which commands *this* user may elevate. Broad output (`(ALL) ALL`) on an account that does not need it is a finding.
- `ss -tulpen`: listening sockets: TCP (`-t`), UDP (`-u`), listening (`-l`), with owning process (`-p`) and no DNS delays (`-n`). Every line is a door into the machine; each should be a door you meant to install. Some process details require root.
- `getent group sudo` / `getent passwd`: who can administer, and which accounts can log in at all.
- The SUID `find` from module 06: privileged code on disk.

## Interpreting what you find
Evidence discipline, learned from painful experience:

- A listening port is not automatically a vulnerability: identify the service, its bind address (`127.0.0.1` versus `0.0.0.0` is the difference between local-only and world-facing), and whether it should exist.
- A SUID executable is not automatically exploitable: check package origin, updates, and expected behavior.
- A writable configuration file is a question about who needs write access, not an automatic incident.
- A log entry is evidence of an event, not proof of compromise. Corroborate before concluding.

## A safe review workflow
1. **Scope:** confirm you are authorized for this host, and write down what you are reviewing.
2. **Collect:** identity, sudo rights, listening sockets, running services, SUID files, login-capable accounts.
3. **Interpret:** for each item, answer "is this intended, documented, and current?"
4. **Record:** findings with path/port, observed state, expected state, risk, and recommendation.
5. **Change** through your normal process, one finding at a time, with rollback notes.

## Practice exercises
Do these on your own machine or lab VM. Try every task before opening its solution.

**Exercise 1.** Record your identity and your exact sudo rights.

<details>
<summary>Show a worked solution</summary>

```bash
id
sudo -l
```

If `sudo -l` shows `(ALL : ALL) ALL`, you hold full administrative rights; that is normal for a personal lab's owner account and a finding on a shared server for an account that only deploys one app.
</details>

**Exercise 2.** List every listening socket, map each to a service, and mark which are reachable from outside the machine.

<details>
<summary>Show a worked solution</summary>

```bash
ss -tulpen
```

Read the Local Address column: `127.0.0.1:...` or `[::1]:...` is local-only; `0.0.0.0:...` or `[::]:...` accepts connections from any interface. Cross-reference names with `systemctl --type=service --state=running`. Anything you cannot name is tonight's homework.
</details>

**Exercise 3.** Pick one configuration file in `/etc` and document it the audit way, without changing it.

<details>
<summary>Show a worked solution</summary>

```bash
stat /etc/ssh/sshd_config
dpkg -S /etc/ssh/sshd_config    # or rpm -qf
```

Record: path, owner/group, mode, owning package, whether local modifications exist, and what the file controls. This is the atomic unit of every audit report.
</details>

**Exercise 4.** Find every account on this machine that can log in interactively, and flag any you did not expect.

<details>
<summary>Show a worked solution</summary>

```bash
grep -Ev '/(nologin|false)$' /etc/passwd
```

Expect root plus your regular accounts. A system account with a real shell, or any account you cannot explain, is worth investigating.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why does least privilege forbid shared admin accounts even among trusted teammates?

<details>
<summary>Show answer</summary>

Accountability and revocation: shared credentials make every action unattributable in the logs, and removing one person's access means changing the password for everyone. Individual accounts plus group-based sudo give you both.
</details>

**Q2.** You find a service listening on `0.0.0.0:8080` that nobody recognizes. What are your first two steps?

<details>
<summary>Show answer</summary>

Identify it (`ss -tulpen` for the process, `systemctl status` or `dpkg -S` on the binary), and record what you found. Only then decide to stop, firewall, or remove it through a controlled change. Investigate before you switch things off; it may be load-bearing.
</details>

**Q3.** Why is "delete the account" not step one when you find a suspicious user?

<details>
<summary>Show answer</summary>

Evidence and continuity: the account's files, processes, and history tell you how it got there and what it touched. Preserve evidence, disable login (lock the password, set the shell to `nologin`), then remove through process.
</details>

## Common mistakes
- Running privilege-escalation or "audit" scripts on machines without authorization.
- Changing ownership or permissions to silence an error rather than understand it.
- Treating every open port or SUID file as an emergency.
- Leaving test accounts, keys, and packages behind after a review.

## Key takeaways
Least privilege is a routine: normal account, minimal elevation, dedicated service identities, tidy removals. Security review is evidence first, interpretation second, controlled change last.

## Further practice
Combine this lesson with the filesystem audit (module 10) and the process/service modules (07), and write a one-page review of your own VM as if it were a client's server.

## References
- [Linux kernel security documentation](https://docs.kernel.org/security/)
- [sudo documentation](https://www.sudo.ws/docs/)
