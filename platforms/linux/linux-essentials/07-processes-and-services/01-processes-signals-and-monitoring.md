# Processes, Signals, and Monitoring


## Learning objectives
- Explain PID, PPID, process states, and job control.
- Inspect and monitor processes.
- Send signals and distinguish graceful termination from forced termination.

## Core concepts
A **process** is a running program instance. It has a process ID (PID), a parent process ID (PPID), credentials, open file descriptors, and memory mappings. A process can be foreground or background relative to a shell. Common states include running, sleeping, stopped, and zombie.

## Commands
```bash
ps
ps aux
ps -ef
pgrep -a ssh
pidof systemd
top
htop
uptime
free -h
```
`ps` snapshots process information; `top` refreshes interactively; `htop` is an optional enhanced monitor. `pgrep -a` finds matching process names and prints command lines. `pidof` may not be installed or useful for every program.

### Job control
```bash
sleep 300
# press Ctrl-Z to suspend
jobs
bg
fg
```
Append `&` to start a command in the background: `sleep 300 &`. `jobs` reports jobs belonging to the current shell; it is not a system-wide process listing.

### Signals and termination
```bash
kill -TERM 1234
kill -KILL 1234
kill -l
killall -TERM sleep
nohup sleep 300 >/tmp/sleep.log 2>&1 &
```
`SIGTERM` (15) requests graceful termination; the process may clean up or ignore it. `SIGKILL` (9) cannot be caught and should be a last resort. Replace `1234` with a PID you own and have verified. `killall name` targets processes by name and can affect more than intended.

`nohup command &` can keep a command running after a hangup, commonly writing output to `nohup.out` when output is not redirected. It is not a service manager. `killall name` sends a signal to processes selected by name; verify the exact target and local implementation before using it because multiple processes may match.

## Hands-on practice
- Start `sleep 120 &`, find its PID with `jobs -l` or `pgrep`.
- Stop it with `kill -TERM PID`.
- Run `top` and identify CPU and memory columns.
- Hint: verify the PID before sending a signal.

## Common mistakes
- Killing a process by a guessed PID.
- Using `kill -9` as the first response.
- Assuming `jobs` shows every process on the machine.
- Confusing a shell job number (`%1`) with a system PID.

## Key takeaways
Use process inspection before signaling. Prefer graceful termination and use a service manager for managed services.

## Further practice
Read `man ps`, `man signal`, `man kill`, and `man proc`.

## References
- [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [GNU Bash job control](https://www.gnu.org/software/bash/manual/html_node/Job-Control.html)
