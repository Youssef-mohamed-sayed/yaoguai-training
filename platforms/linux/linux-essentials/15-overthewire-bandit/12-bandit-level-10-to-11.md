# Bandit Level 10 to Level 11: Base64 Decoding


## Level objective
Decode the Base64-encoded content described by the official level page.

## Concepts practiced
Encoding versus encryption, Base64, and standard input/output.

## Relevant commands
```bash
base64 --decode data.txt
base64 -d data.txt
```

## Hints (in increasing order)
1. Base64 is an encoding scheme, not encryption.
2. The `base64` utility supports a decode option.
3. Decode the file and read the output; do not attempt to use the text as a key.

## Solution explanation
Run the Base64 decoder against the supplied file. The decoded output contains the next credential. Keep it private.

## Why it works
Base64 maps binary data to a printable character alphabet. Decoding reverses that representation; it does not require a secret key.

## Lessons learned
Encoding is not confidentiality. Never treat Base64 as a security boundary.

## Official verification
[Bandit Level 10 → Level 11](https://overthewire.org/wargames/bandit/bandit11.html)
