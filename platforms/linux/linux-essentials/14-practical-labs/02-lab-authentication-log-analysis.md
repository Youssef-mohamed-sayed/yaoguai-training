# Lab: Authentication Log Analysis


## Lab objectives
Turn a raw authentication log into counts, a ranked list of sources, and a cautious incident note, using only the text-processing tools from module 08.

## Initial conditions
Create `sample-auth.log` using the six-line sample in [the text-processing lesson](../08-text-processing-and-pipelines/02-grep-sed-awk-and-log-analysis.md):

```bash
cat > sample-auth.log <<'EOF'
Nov 21 09:01:02 lab sshd[1201]: Failed password for invalid user guest from 192.0.2.10 port 50122 ssh2
Nov 21 09:02:11 lab sshd[1204]: Accepted publickey for analyst from 192.0.2.25 port 50123 ssh2
Nov 21 09:03:45 lab sshd[1210]: Failed password for root from 192.0.2.10 port 50130 ssh2
Nov 21 09:04:03 lab sshd[1212]: Failed password for analyst from 198.51.100.7 port 50131 ssh2
Nov 21 09:05:20 lab sshd[1218]: Connection closed by authenticating user analyst 192.0.2.25 port 50140 [preauth]
Nov 21 09:06:50 lab sshd[1221]: Failed password for invalid user test from 192.0.2.10 port 50155 ssh2
EOF
```

The addresses are documentation ranges, not real systems.

## Tasks
1. Count failed authentication messages.
2. Count successful public-key messages.
3. Extract IP-like strings from failed events.
4. Rank repeated IP-like strings.
5. Save failed events to `failed-events.txt`.
6. Write a three-sentence incident note that separates observed facts from assumptions.

## Suggested commands
```bash
grep -ci 'Failed password' sample-auth.log
grep -ci 'Accepted publickey' sample-auth.log
grep -i 'Failed password' sample-auth.log |
  grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
  sort | uniq -c | sort -nr
grep -i 'Failed password' sample-auth.log | tee failed-events.txt
```

Build each pipeline one stage at a time and check the output before appending the next stage. The extraction regex matches IP-shaped text; it is not IPv4 validation.

## Validation
**Check 1.** What counts should tasks 1 and 2 produce?

<details>
<summary>Show answer</summary>

Four `Failed password` lines and one `Accepted publickey` line.
</details>

**Check 2.** Which address ranks first, with how many failed events?

<details>
<summary>Show answer</summary>

`192.0.2.10` with 3 failed events; `198.51.100.7` with 1.
</details>

**Check 3.** Your incident note: write three sentences. Then compare with the model note.

<details>
<summary>Show model answer</summary>

"Between 09:01 and 09:07 the sample log records four failed password attempts and one successful public-key login. Three of the four failures originate from 192.0.2.10 and target the accounts root, guest, and test. The sample is synthetic and six lines long, so these counts describe this file only and say nothing about any real attacker, intent, or trend."
</details>

**Check 4.** Why would drawing a conclusion like "an attacker is brute-forcing root" be premature here, even though one failed line does name root?

<details>
<summary>Show answer</summary>

One event is not a pattern, and a six-line synthetic sample cannot establish frequency, intent, or identity. Evidence discipline: state what the log shows, then what would be needed (real logs over time, source reputation, successful logins) before any claim.
</details>

## Extension
Use `awk` to count events by username. Remember that the message format differs per event type, so field positions shift; decide how you will handle `invalid user guest` (two words) before trusting your counts.

<details>
<summary>Show a worked solution</summary>

```bash
grep -i 'Failed password' sample-auth.log |
  sed 's/invalid user //' |
  awk '{for(i=1;i<=NF;i++) if ($i=="from") {print $(i-1); break}}' |
  sort | uniq -c | sort -nr
```

Output:

```text
      1 test
      1 root
      1 guest
      1 analyst
```

The `sed` normalizes the two-word "invalid user" case, then `awk` prints the word before `from` on each line.
</details>

## Deliverable
Submit the commands, the counts, the extracted tokens with their ranking, `failed-events.txt`, and your three-sentence note.

## Common mistakes
- Counting with `grep -i` one way and `-c` another and reporting inconsistent totals.
- Trusting the IP-shaped regex as validation.
- Editing the sample log mid-analysis; always work on a copy.
