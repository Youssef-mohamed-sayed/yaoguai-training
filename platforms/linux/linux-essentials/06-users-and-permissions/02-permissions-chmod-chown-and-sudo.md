# Permissions, chmod, chown, and sudo


## Learning objectives
- Interpret read, write, and execute permissions.
- Use symbolic and octal modes.
- Change ownership and use sudo responsibly.

## Permission model
For ordinary files:
- `r` (4): read contents.
- `w` (2): modify contents.
- `x` (1): execute the file, subject to other requirements.

For directories:
- `r`: list names.
- `w`: create, remove, or rename entries (normally combined with execute).
- `x`: traverse/search the directory.

The three classes are user/owner (`u`), group (`g`), and other (`o`). Example `-rwxr-xr--` means owner has `rwx`, group `r-x`, others `r--`.

### Octal modes
| Mode | Owner | Group | Other | Typical use |
|---|---|---|---|---|
| 755 | rwx | r-x | r-x | Publicly traversable executable directory |
| 644 | rw- | r-- | r-- | Ordinary readable file |
| 700 | rwx | --- | --- | Private directory |
| 600 | rw- | --- | --- | Private file |

Octal digits add values: read 4, write 2, execute 1.

## Commands
```bash
chmod 640 report.txt
chmod u+x script.sh
chmod go-rwx private.txt
sudo chown alice:analysts report.txt
sudo chgrp analysts report.txt
```
`chmod` changes mode bits. `chown` changes owner and optionally group; `chgrp` changes group. Ownership changes usually require root or suitable capabilities.

`sudo command` runs a command under an authorized policy, commonly as root. `su - username` starts a login shell as another user and normally requires that account's password; `sudo -iu username` may be used where policy permits.

## Hands-on practice
- Create a file and directory in `~/linux-lab`.
- Set the file to `600`, directory to `700`, and inspect with `ls -l` and `stat`.
- In a disposable VM, change ownership to a test user and verify with `stat`.
- Hint: use `chmod 755` only when group and other users genuinely need directory traversal or execution.

## Common mistakes
- Thinking execute on a directory means running it; it means traversal/search.
- Setting `777` to “fix” access errors. This usually grants far more access than needed.
- Forgetting directory execute permission when troubleshooting file access.
- Using `sudo` for every command, which can create root-owned files in a user's home directory.

## Key takeaways
Permissions are an access-control boundary. Apply the narrowest mode that supports the task.

## Further practice
Read `man chmod`, `man chown`, `man sudo`, and `man su`.

## References
- [Linux man-pages: chmod(1)](https://man7.org/linux/man-pages/man1/chmod.1.html)
- [GNU Coreutils: chown](https://www.gnu.org/software/coreutils/manual/html_node/chown-invocation.html)
