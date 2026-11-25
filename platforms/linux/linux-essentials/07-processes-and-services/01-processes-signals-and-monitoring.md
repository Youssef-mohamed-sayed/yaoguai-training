# Processes, Signals, and Monitoring


## Learning objectives
- Explain PID, PPID, process states, and shell job control.
- Inspect and monitor processes with the right tool for each question.
- Send signals correctly: graceful termination first, forced termination last.

## Core concepts
A **process** is a running instance of a program. Each has a **PID** (process ID), a **PPID** (parent's PID), credentials (the UID/GIDs it runs with), open files, and memory. Processes form a tree: every process was started by a parent, and PID 1 (the init system, usually `systemd`) is the ancestor of everything.

Common states you will see in listings: **R** running, **S** sleeping (waiting for something, the normal idle state), **T** stopped (suspended), **Z** zombie (finished, waiting for its parent to collect its exit status).

## Commands
```bash
ps            # processes of this terminal
ps aux        # everything, BSD style
ps -ef        # everything, with PPIDs
pgrep -a ssh  # find by name, show the command line
top           # live view; q to quit
htop          # friendlier live view (may need installing)
uptime        # load averages
free -h       # memory
```

Which one answers which question:

- "What's running?" → `ps aux` (or `ps -ef` when you need parent IDs).
- "What's eating CPU right now?" → `top` / `htop`, sorted by CPU.
- "Is the service up?" → `pgrep -a name`.
- "Is the box overloaded?" → `uptime` first: the three load averages over 1, 5, and 15 minutes, compared against your CPU count.

## Job control: processes and your shell
```bash
sleep 300
# press Ctrl-Z to suspend
jobs
bg        # resume in background
fg        # bring back to foreground
```

- Append `&` to start in the background: `sleep 300 &`.
- `Ctrl-Z` suspends the foreground process; `bg` resumes it in the background; `fg` returns it to the foreground.
- `jobs` lists **this shell's** jobs (`%1`, `%2`, ...). A job number is not a PID and `jobs` is not a system-wide view; it only knows what this shell started.

## Signals and termination
A signal is a small message delivered to a process. The two you will use constantly:

- **SIGTERM (15):** "please shut down." The process may save state, close connections, and exit cleanly. It may also catch and ignore the request. Always the first choice.
- **SIGKILL (9):** the kernel destroys the process immediately. It cannot be caught, blocked, or ignored, and nothing gets cleaned up: temporary files, locks, and half-written data remain. Last resort only.

```bash
kill -TERM 1234
kill -KILL 1234     # only after TERM failed
kill -l             # list all signals
killall -TERM sleep # by name: check what matches first with pgrep -a
```

Replace `1234` with a PID you own and have verified with `ps` or `pgrep`. Signaling a guessed PID is how the wrong service dies. `killall` selects by name and may match more processes than you intended.

To survive logout, `nohup command &` keeps a command running after the terminal hangs up (output goes to `nohup.out` unless redirected). It is a convenience, not a service manager; anything that must run reliably belongs to systemd (next lesson).

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Start `sleep 300` in the background, find its PID two different ways, then terminate it gracefully and prove it is gone.

<details>
<summary>Show a worked solution</summary>

```bash
sleep 300 &
jobs -l
pgrep -a sleep
kill -TERM <PID>
pgrep -a sleep || echo "gone"
```

`jobs -l` shows the shell's jobs with PIDs; `pgrep -a sleep` finds it system-wide by name. After SIGTERM, `pgrep` finds nothing.
</details>

**Exercise 2.** Suspend a foreground process, move it to the background, then bring it back and stop it.

<details>
<summary>Show a worked solution</summary>

```bash
sleep 600
# Ctrl-Z
jobs
bg %1
jobs
fg %1
# Ctrl-C
```

`%1` is the job number, valid only in this shell. `Ctrl-C` sends SIGINT, the interactive interrupt.
</details>

**Exercise 3.** Find the five processes currently using the most memory on your system, without opening an interactive tool.

<details>
<summary>Show a worked solution</summary>

```bash
ps aux --sort=-%mem | head -n 6
```

`--sort=-%mem` sorts by memory descending (the leading `-` reverses); `head -n 6` keeps the header plus five rows.
</details>

**Exercise 4.** A runaway process ignores `kill -TERM`. Write the escalation sequence you would actually type, in order, starting from not knowing its PID.

<details>
<summary>Show a worked solution</summary>

```bash
pgrep -a runaway          # confirm PID and that it's really the right process
kill -TERM <PID>          # graceful request
sleep 3; pgrep -a runaway # still there?
kill -KILL <PID>          # last resort: kernel removes it
```

The pause and re-check between steps is what keeps this safe and deliberate.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** Why is `kill -9` a bad *first* response to a stuck process?

<details>
<summary>Show answer</summary>

SIGKILL gives the process no chance to clean up: open files, locks, database transactions, and temporary state are abandoned mid-write. Try SIGTERM, confirm, and only escalate when cleanup has demonstrably failed.
</details>

**Q2.** `jobs` shows nothing, but you can see your process in `ps aux`. Explain.

<details>
<summary>Show answer</summary>

`jobs` only tracks children of the current shell. If the process was started from another terminal, detached, or reparented, this shell has no job entry for it; the system-wide `ps` still lists it.
</details>

**Q3.** What is a zombie process, and whose job is it to clear it?

<details>
<summary>Show answer</summary>

A finished process whose parent has not yet collected its exit status; it holds a slot in the process table but no memory or CPU. The parent clears it by reading the status; if the parent is broken and dies, PID 1 adopts and reaps the zombie.
</details>

## Common mistakes
- Killing by a guessed PID.
- Reaching for `kill -9` first.
- Assuming `jobs` shows every process on the machine.
- Confusing a job number (`%1`) with a PID.
- Using `nohup &` where a real service unit belongs.

## Key takeaways
Inspect before you signal: `ps`, `pgrep`, `top`. Terminate gracefully first, forcibly last. Shell jobs and system processes are two different views of the same activity.

## Further practice
Read `man ps`, `man 7 signal`, and `man 5 proc`, then watch your own system boot's process tree with `ps -ef --forest` or `pstree`.

## References
- [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [GNU Bash job control](https://www.gnu.org/software/bash/manual/html_node/Job-Control.html)
