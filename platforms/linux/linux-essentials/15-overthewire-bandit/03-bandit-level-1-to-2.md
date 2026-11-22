# Bandit Level 1 to Level 2: A Filename Beginning with a Dash


## Level objective
Use the official level instructions to read a file whose name is a single dash character.

## Concepts practiced
Option parsing, relative paths, `--`, and explicit pathnames.

## Relevant commands
```bash
ls -la
cat ./-
cat -- -
```

## Hints (in increasing order)
1. A filename beginning with `-` can be mistaken for a command option.
2. Prefix the name with a path component.
3. Many GNU utilities accept `--` to mark the end of options.

## Solution explanation
Use `cat ./-` to make the argument an explicit relative path. On implementations that support it, `cat -- -` also tells the program that subsequent arguments are operands rather than options.

## Why it works
Option parsers commonly interpret a leading dash as an option. A pathname containing `/` is not interpreted as an option, and `--` conventionally ends option processing.

## Lessons learned
Unusual filenames are valid. Quote and delimit arguments deliberately.

## Official verification
[Bandit Level 1 → Level 2](https://overthewire.org/wargames/bandit/bandit2.html)
