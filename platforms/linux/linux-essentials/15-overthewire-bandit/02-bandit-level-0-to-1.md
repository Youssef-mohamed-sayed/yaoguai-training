# Bandit Level 0 to Level 1: Read a File


## Level objective
Use the official Level 0 → Level 1 page to locate the next account's credential in the designated home-directory file.

## Concepts practiced
SSH login, home directories, `pwd`, `ls`, and reading a text file.

## Relevant commands
```bash
pwd
ls -la
file readme
cat readme
```

## Hints (in increasing order)
1. Confirm that you are logged in as the expected account.
2. List the home directory.
3. Identify the file type before reading it.

## Solution explanation
After connecting to the starting account using the official instructions, inspect the home directory and read the named text file. Use the resulting credential only to authenticate to the next level. Do not paste the credential into notes or this course.

## Why it works
The challenge is about locating and reading an ordinary file in the current user's home directory. `cat` sends the file's contents to standard output.

## Lessons learned
- SSH places you in a remote shell.
- `pwd` and `ls` establish context before acting.
- Credentials should be handled as secrets.

## Practice independently
Close the solution section above until you have tried the commands. Then repeat the process from memory on a local text file.

## Official verification
Use the official [Bandit Level 0 → Level 1 page](https://overthewire.org/wargames/bandit/bandit1.html). The official page is authoritative if details change.
