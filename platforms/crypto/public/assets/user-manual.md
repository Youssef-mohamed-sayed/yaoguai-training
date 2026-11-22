# YAOGUAI Cryptography Training Ground — User Manual

YAOGUAI (妖怪) is a hands-on cryptography curriculum and interactive workbench designed for learning encoding, symmetric and asymmetric ciphers, cryptographic hashing, hash cracking, and secure file encryption.

---

## 1. Running the Application

To run the application locally on your computer:

```bash
cd scripts
pip install -r requirements.txt
python app.py
```

This starts the unified Flask server hosting both the REST API and the frontend website, automatically opening your default web browser at `http://127.0.0.1:5000/`. To stop the server at any time, press `Ctrl+C` in your terminal.

---

## 2. Tools Workbench Overview

Navigate to **Tools** in the top navigation bar (`tools.html`) to access the interactive cryptography workbench:
- **Sidebar**: Select any cryptographic primitive organized by category: Encoding (Hex, Base64, ASCII, URL), Encryption (XOR, RC4, DES, 3DES, AES, RSA), Hashing (MD5, SHA-1, SHA-256, bcrypt), Cracking, and File Crypto.
- **Mode Switch**: Toggle between operations (e.g., Encode / Decode, Encrypt / Decrypt, Hash / Verify).
- **Output → Input**: Instantly copies the current result into the input box to chain operations together.
- **API Status**: The top bar chip monitors real-time connectivity to the local Flask backend.

---

## 3. File Cryptography: Encryption, Encoding & Hashing

The **File Crypto** section supports full-file operations across all algorithms in the curriculum with client validation, progress indicators, and automatic downloads:

### File Encrypt / Encode / Hash
1. **Encryption**:
   - Choose **File Encrypt** and select **Encryption**.
   - Pick your algorithm: **DES**, **AES-128**, **Triple DES (3DES)**, **RC4**, **XOR**, or **Hybrid RSA+DES**.
   - Upload your file, supply the required key(s), and click **Encrypt & Download**. Your browser immediately downloads `<filename>.<algo>.enc`.
   - In **Hybrid RSA+DES** mode: paste your RSA modulus `n` and exponent `e` (generated with the RSA tool). The file is downloaded as `.hybrid.enc` and the RSA-encrypted session key is displayed on screen with a one-click **Copy key** button.
2. **Encoding**:
   - Select **Encoding** to transform file bytes into text representation: **Base64** (`.b64`), **Hexadecimal** (`.hex`), **ASCII codes** (`.ascii`), or **URL encoding** (`.url`).
   - No secret key is needed. Click **Encode & Download** to save the encoded file.
3. **Hashing**:
   - Select **Hashing** to compute cryptographic digests: **MD5**, **SHA-1**, **SHA-256**, or **bcrypt** (with adjustable cost factor).
   - Click **Compute Hash** to inspect the hash on screen, copy it to clipboard, or download an industry-standard checksum file (`<filename>.<algo>`).

### File Decrypt / Decode / Verify
1. **Decryption**:
   - Choose **File Decrypt** and select **Decryption**.
   - Pick your algorithm (**DES**, **AES-128**, **3DES**, **RC4**, **XOR**, or **Hybrid RSA+DES**).
   - Upload the encrypted file, provide the matching secret key (or for Hybrid: encrypted session key, private exponent `d`, and modulus `n`), and enter the target filename (automatically suggested).
   - Click **Decrypt & Download** to recover your original file.
2. **Decoding**:
   - Select **Decoding** to reverse **Base64**, **Hexadecimal**, **ASCII codes**, or **URL encoding** back to the original file bytes.
   - Click **Decode & Download**.
3. **Hash Verify**:
   - Select **Hash Verify** to audit file integrity against an expected checksum.
   - Upload the file, select the algorithm (**MD5**, **SHA-1**, **SHA-256**, or **bcrypt**), paste the expected hash, and click **Verify Checksum** to receive an instant match/mismatch status.

---

## 4. Hash Cracking & Identification

Under **Crack a hash**, three dedicated modes assist with CTF challenges and audits:
1. **Crack (sample wordlist)**: Fast offline dictionary attack across MD5, SHA-1, and SHA-256 using the built-in wordlist.
2. **Crack (Hashes.com)**: Online crowd-sourced database lookup via the Hashes.com API. Enter your personal API key once (persisted safely in your browser's local storage).
3. **Identify algorithm**: Queries the Hashes.com Hash Identifier API to inspect hash length, format, and salt patterns, automatically identifying probable algorithm candidates without requiring hash type selection or an API key.

---

## 5. Lessons & CTF Challenges

Click **Encoding**, **Encryption**, or **Hashing** in the top navigation bar to explore interactive lessons. Read historical context and algorithm specifications, solve comprehension checkpoints, and solve end-of-module CTF challenges by recovering secret flags in the `flag{...}` format. Mark each lesson complete to track your overall curriculum progress.
