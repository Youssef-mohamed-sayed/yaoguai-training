# Standard Streams, Redirection, and Pipes


## Learning objectives
- Explain stdin, stdout, stderr, and their file descriptor numbers.
- Redirect and append output, and combine or split streams deliberately.
- Build pipelines and interpret exit codes, including in chains of commands.

## Core concepts
Every process starts with three standard streams:

- **stdin** (file descriptor 0): where it reads input.
- **stdout** (file descriptor 1): where it writes normal output.
- **stderr** (file descriptor 2): where it writes diagnostics and errors.

The separation is deliberate and useful: a program's *results* flow on stdout while its *complaints* flow on stderr, so you can capture, filter, or discard each independently. A **pipe** (`|`) connects one command's stdout to the next command's stdin. **Redirection** connects a stream to a file instead.

This is the Unix philosophy in practice: small tools that each do one thing, glued together with streams into exactly the workflow you need.

## Syntax
```bash
command > output.txt       # stdout to file, overwriting
command >> output.txt      # stdout to file, appending
command < input.txt        # stdin from file
command 2> errors.txt      # stderr to file
command > all.txt 2>&1     # stdout AND stderr to the same file
command 2>&1 | less        # combine streams, then pipe the mix
command &> all.txt         # Bash shorthand for both streams
```

Order matters and it follows one rule: redirections are applied left to right. `> all.txt 2>&1` first points stdout at the file, then points stderr at wherever stdout now goes: both land in the file. Reversed, `2>&1 > all.txt` first points stderr at the *old* stdout (your terminal), then moves stdout to the file: errors still hit the screen.

> [!WARNING]
> `>` truncates the destination **before** the command runs, even if the command then fails. `cat important.txt > important.txt` destroys the file instantly. When you mean "add to the end", type `>>`.

## Pipes and exit codes
```bash
printf 'alpha\nbeta\n' | grep beta
printf 'c\nb\na\n' | sort | head -n 1
```

Each stage reads the previous stage's stdout. The pipeline's exit status in Bash is the status of its **last** command, which hides failures in the middle:

```bash
grep secret missing-file.txt | sort
echo "status: $?"           # 0: sort succeeded even though grep failed
set -o pipefail
grep secret missing-file.txt | sort
echo "status: $?"           # 2: the pipeline now reports grep's failure
```

`$?` always holds the most recent foreground command's status: `0` means success, anything else is a failure code. Scripts rely on `set -o pipefail` (module 12) so a broken stage cannot masquerade as success.

### Command chaining with statuses
- `a && b`: run `b` only if `a` **succeeded**. `mkdir out && cd out`.
- `a || b`: run `b` only if `a` **failed**. `pgrep myapp || echo "not running"`.
- `a ; b`: run both, regardless.

## Practice exercises
Do these in your own terminal. Try every task before opening its solution.

**Exercise 1.** Run `ls /does-not-exist` and send its error message to `errors.txt` while letting any normal output reach the screen. Then check the exit status.

<details>
<summary>Show a worked solution</summary>

```bash
ls /does-not-exist 2> errors.txt
echo "$?"
cat errors.txt
```

Output:

```text
2
ls: cannot access '/does-not-exist': No such file or directory
```

The error went to the file (descriptor 2), the status `2` is `ls`'s failure code.
</details>

**Exercise 2.** Build a three-stage pipeline: list the names in `/usr/bin`, keep only those containing `sh`, and count them.

<details>
<summary>Show a worked solution</summary>

```bash
ls /usr/bin | grep sh | wc -l
```

`wc -l` counts lines. Each tool does one job; the pipe composes them. (You will learn `grep` properly in the next lesson.)
</details>

**Exercise 3.** Capture both stdout and stderr of `ls /tmp /does-not-exist` into one file, in the order the messages were produced.

<details>
<summary>Show a worked solution</summary>

```bash
ls /tmp /does-not-exist > both.txt 2>&1
cat both.txt
```

The `2>&1` must come **after** the file redirection so stderr follows stdout into the file.
</details>

**Exercise 4.** Write a one-liner that creates `~/linux-lab/pipeline-out` only if `~/linux-lab` exists, and prints "missing" otherwise.

<details>
<summary>Show a worked solution</summary>

```bash
[ -d ~/linux-lab ] && mkdir -p ~/linux-lab/pipeline-out || echo missing
```

`[ -d ... ]` tests for the directory; `&&` runs the `mkdir` only when the test succeeds; `||` prints the message only when the chain so far failed.
</details>

## Check yourself
Answer each question, then open the answer to verify.

**Q1.** What is the difference between `>` and `>>`, and when does the difference become destructive?

<details>
<summary>Show answer</summary>

`>` truncates the target file before the command runs; `>>` appends. It becomes destructive the moment you redirect into a file that already holds data you wanted to keep.
</details>

**Q2.** `prog 2>&1 > out.txt` does not capture errors in `out.txt`. Why?

<details>
<summary>Show answer</summary>

Left-to-right: `2>&1` first points stderr at the current stdout (the terminal), then `> out.txt` moves only stdout into the file. The correct order is `prog > out.txt 2>&1`.
</details>

**Q3.** A pipeline's last command succeeded, so `$?` is 0. Does that prove the whole pipeline worked?

<details>
<summary>Show answer</summary>

No. Without `pipefail`, `$?` reports only the last command. A middle stage can fail silently; `set -o pipefail` makes the pipeline report the first failure.
</details>

## Common mistakes
- Using `>` when `>>` was meant.
- Reversing the order in `> file 2>&1`.
- Trusting the last command's status for the whole pipeline.
- Forgetting that the shell performs redirections before the command starts, so the file is truncated even when the command errors.

## Key takeaways
stdout carries results, stderr carries complaints, and pipes plus redirections route each where you want it. Quote the order as "file first, then stderr follows": `> file 2>&1`. Check `$?`, and use `pipefail` in anything scripted.

## Further practice
Read the redirection and pipeline sections of `man bash`, then rewrite one GUI task you did this week (find a file, filter lines, save results) as a single pipeline.

## References
- [Bash redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html)
