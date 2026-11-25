# Bandit Level 10 to Level 11: Base64 in the Wild


## Level objective
`data.txt` contains base64-encoded data. Decode it to read the password. Confirm the exact goal on the official level page.

## Concepts practiced
Recognizing and decoding base64, and understanding the difference between **encoding** and **encryption**.

## Background
Base64 is an *encoding*: a reversible byte-to-text scheme with a fixed, public alphabet and no key. It exists so binary data can travel through text-only channels (email bodies, JSON, configuration files). It is everywhere in real systems: certificates, API tokens, email attachments.

Recognize it by shape: long runs of `A-Z a-z 0-9 + /`, often ending in `=` or `==` padding. Decode with the tool of the same name:

```bash
base64 -d data.txt
```

The critical security lesson: because the algorithm is public and keyless, **base64 is obfuscation, not protection**. Treating an encoded password as "encrypted" is one of the most common real-world mistakes; anyone who sees the string can decode it in a second, exactly as you are about to.

## Relevant commands
```bash
file data.txt
head -c 80 data.txt; echo
base64 -d data.txt
```

## Hints (in increasing order)
1. The content is transformed, not hidden: a public, keyless scheme.
2. The command shares the scheme's name.
3. `-d` decodes.

## Solution explanation
`base64 -d data.txt` decodes the file and prints readable text including the next password. Use it to log in to the next level.

## Why it works
Base64 maps every three bytes to four characters from a 64-character alphabet, reversing deterministically. No secret is involved, so possession of the encoded text is possession of the content.

## Check yourself
**Q1.** A developer "secures" a token by base64-encoding it before storing it in a config file. What is wrong?

<details>
<summary>Show answer</summary>

Encoding is not encryption: no key exists, so anyone with read access decodes it instantly. The token is still plaintext for every practical purpose; protect the file's permissions or use a real secret store.
</details>

**Q2.** What visual features make you suspect a string is base64?

<details>
<summary>Show answer</summary>

The restricted alphabet (`A-Za-z0-9+/`), length in multiples of four, and `=`/`==` padding at the end.
</details>

## Official verification
[Bandit Level 10 → Level 11](https://overthewire.org/wargames/bandit/bandit11.html)
