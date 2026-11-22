# Lab: Authentication Log Analysis


## Lab objectives
Practice filtering and summarizing authentication events using a controlled sample.

## Initial conditions
Create `sample-auth.log` using the six-line sample in [the text-processing lesson](../08-text-processing-and-pipelines/02-grep-sed-awk-and-log-analysis.md). The addresses are documentation ranges, not real source systems.

## Tasks
1. Count failed authentication messages.
2. Count successful public-key messages.
3. Extract IP-like strings from failed events.
4. Rank repeated IP-like strings.
5. Save failed events to `failed-events.txt`.
6. Write a three-sentence incident note that distinguishes observed facts from assumptions.

## Suggested commands
```bash
grep -ci 'Failed password' sample-auth.log
grep -ci 'Accepted publickey' sample-auth.log
grep -i 'Failed password' sample-auth.log |
  grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' |
  sort | uniq -c | sort -nr
grep -i 'Failed password' sample-auth.log | tee failed-events.txt
```
The extraction regex is a simple teaching example and does not validate IPv4 octets.

## Expected interpretation
The sample contains four failed-password lines and one accepted-publickey line. The repeated documentation address `192.0.2.10` appears in three failed events. This is a fact about the supplied sample only; it does not establish attacker identity, intent, or real-world attribution.

## Extension
Use `awk` to count events by username. Remember that the log's free-form message format makes field positions dependent on the event type.

## Deliverable
Submit the commands, counts, extracted tokens, and a cautious summary.
