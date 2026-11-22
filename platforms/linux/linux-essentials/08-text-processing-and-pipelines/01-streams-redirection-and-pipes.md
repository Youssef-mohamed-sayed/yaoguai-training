# Standard Streams, Redirection, and Pipes


## Learning objectives
- Explain stdin, stdout, stderr, and file descriptors.
- Redirect and append output.
- Build pipelines and interpret exit codes.

## Core concepts
A process normally starts with three standard streams:
- stdin (file descriptor 0): input.
- stdout (1): normal output.
- stderr (2): diagnostic output.

A **pipe** connects one command's stdout to the next command's stdin. Redirection connects streams to files or other destinations.

## Syntax
```bash
command > output.txt       # overwrite stdout
command >> output.txt      # append stdout
command < input.txt        # read stdin from file
command 2> errors.txt      # redirect stderr
command > all.txt 2>&1     # stdout and stderr to same destination
command 2>&1 | less        # combine streams, then pipe
```
Order matters: `> all.txt 2>&1` first redirects stdout, then points stderr to the same destination. `2>&1 > all.txt` has a different effect.

```bash
printf 'alpha
beta
' | grep beta
```
The pipe passes text to `grep`. A pipeline's exit status is normally the status of its last command in Bash; `set -o pipefail` makes a pipeline fail if a command fails (with the rightmost nonzero status).

### Command chaining
- `a && b`: run `b` only if `a` succeeds.
- `a || b`: run `b` only if `a` fails.
- `a ; b`: run both sequentially regardless of the first status.
- `$?`: status of the most recently completed foreground command (or pipeline).

## Hands-on practice
- Redirect `ls /does-not-exist` stdout and stderr to separate files.
- Append a line to a file with `>>`.
- Pipe `printf` output to `sort`.
- Run `false; echo "$?"`, then `true; echo "$?"`.
- Hint: stderr uses descriptor 2.

## Common mistakes
- Using `>` when you meant to append; it truncates the destination.
- Reversing redirection order.
- Assuming a successful last pipeline command means every earlier command succeeded.
- Forgetting that shell redirection is processed before the command runs.

## Key takeaways
Streams and pipes let small tools work together. Redirect deliberately and check exit status.

## Further practice
Read `man bash` sections on redirections and pipelines.

## References
- [Bash redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
