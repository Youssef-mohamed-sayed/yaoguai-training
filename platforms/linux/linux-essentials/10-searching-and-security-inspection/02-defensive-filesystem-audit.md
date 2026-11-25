# Defensive Filesystem and Permission Auditing


## Learning objectives
- Find risky file permissions worth reviewing.
- Explain why credentials and configuration files require protection.
- Document findings properly, without changing the system mid-audit.

## What an audit looks for
A defensive filesystem review searches for mismatches between how permissions *are* and how they *should be*:

- World-writable files and directories outside intended shared locations.
- Unexpected SUID/SGID executables (module 06 lesson 3).
- Sensitive files readable by unintended users: private keys, configuration with credentials.
- Unexpected ownership under application and configuration directories.
- Secrets accidentally committed to source trees or written into logs.

## Discovery commands
```bash
find /etc -type f -perm -0002 -ls 2>/dev/null          # world-writable config
find / -xdev -type f -perm -4000 -ls 2>/dev/null       # SUID executables
find /home -type f -name 'id_*' -ls 2>/dev/null        # private key files
stat ~/.ssh ~/.ssh/authorized_keys 2>/dev/null         # SSH permission check
grep -RniE 'password|secret|api[_-]?key' ~/project 2>/dev/null   # secrets in a source tree
```

Read these as **discovery**, not verdicts. Every result is a question, not an answer: some applications legitimately need special permissions, and `/tmp` is world-writable by design. The audit skill is interpreting each finding in context.

A finding is properly documented before anything is touched:

```text
Path:        /home/deploy/app/config.yml
Observed:    -rw-rw-r-- deploy deploy (world-readable, contains a DB password)
Expected:    -rw-r----- deploy deploy, or a secrets manager
Risk:        any local account can read production credentials
Recommendation: chmod 640/o-rwx, move the secret to a managed store, rotate it
```

### Protecting secrets
- Private keys: mode `600`, owned by the user. SSH clients refuse keys with sloppy permissions.
- Configuration with credentials: mode `640` or tighter, owned by the service's account and group.
- Keep secrets out of shell history, command arguments (visible in `ps`), and source code.
- Suspected exposure means **rotation**, not just re-permissioning: whoever read the secret already has it.

## The auditor's discipline
1. Record the original state (`stat`, `ls -l`, package ownership) **before** any change.
2. Never alter system-owned files without a change plan and a rollback path.
3. Never run an untrusted "hardening script" with root privileges to fix findings for you.
4. A scan result is never proof of exploitability; it is a prioritization list.

## Practice exercises
Do these in `~/linux-lab` only, not against the whole host. Try every task before opening its solution.

**Exercise 1.** Create one deliberately world-readable "secret" file and one correctly protected private key, then compare them with `stat`.

<details>
<summary>Show a worked solution</summary>

```bash
cd ~/linux-lab
printf 'DB_PASS=hunter2\n' > config.yml
chmod 644 config.yml
printf 'FAKE-PRIVATE-KEY\n' > id_test
chmod 600 id_test
stat -c '%a %U:%G %n' config.yml id_test
```

Output:

```text
644 learner:learner config.yml
600 learner:learner id_test
```

Any local account can read `config.yml`; only the owner can read `id_test`.
</details>

**Exercise 2.** Audit your lab directory for world-writable and world-readable files, and write one properly formatted finding for the worst offender.

<details>
<summary>Show a worked solution</summary>

```bash
find ~/linux-lab -type f -perm -0002 -ls 2>/dev/null
find ~/linux-lab -type f -perm -0004 -ls 2>/dev/null
```

Then write the finding in the four-field format from this lesson: path, observed state, expected state, risk, recommendation. The `-0004` test catches world-*readable* files, which matters when the content is sensitive.
</details>

**Exercise 3.** Check your own SSH setup's permissions and fix anything too broad.

<details>
<summary>Show a worked solution</summary>

```bash
stat -c '%a %n' ~/.ssh ~/.ssh/* 2>/dev/null
```

Expected: `~/.ssh` at `700`, private keys (`id_*` without `.pub`) at `600`, public keys and `authorized_keys` at `644` or tighter. Fix with `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*`.
</details>

**Exercise 4.** Hunt for an accidentally committed secret in a project directory without exposing it further.

<details>
<summary>Show a worked solution</summary>

```bash
grep -RniE 'password|secret|api[_-]?key|BEGIN .*PRIVATE KEY' ~/linux-lab 2>/dev/null
```

If anything matches a *real* credential: rotate the credential first, then remove it from the file, then scrub history if it was committed to git. Re-permissioning alone does not undo exposure.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why is "world-readable" not automatically a finding?

<details>
<summary>Show answer</summary>

Plenty of files are world-readable by design: documentation, public web content, `/etc/os-release`. A finding requires sensitive *content* plus broad *access*; the audit's job is judging both.
</details>

**Q2.** What are the first two actions after discovering a real password in a world-readable file?

<details>
<summary>Show answer</summary>

Rotate the password (assume it is compromised), then fix the file's permissions and move the secret to proper storage. Order matters: fixing permissions first leaves the exposed credential valid.
</details>

**Q3.** Why record the original state before changing anything?

<details>
<summary>Show answer</summary>

Evidence and rollback: you need to prove what you found, and you need a way back if the "fix" breaks the application.
</details>

## Common mistakes
- Calling every world-readable file sensitive.
- Treating scan output as proof of exploitability.
- Changing permissions before recording the original state.
- Running untrusted fix-it scripts as root.
- Re-permissioning exposed secrets without rotating them.

## Key takeaways
Auditing is evidence gathering: discover, document, interpret in context, then recommend least-privilege changes. Rotation beats re-permissioning when a secret has already leaked.

## Further practice
Repeat the audit on a disposable VM and compare against a clean installation; then skim a CIS Benchmark for your distribution to see how far the rabbit hole goes.

## References
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OpenSSH manual pages](https://www.openssh.com/manual.html)
