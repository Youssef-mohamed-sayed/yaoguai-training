"""
Password/hash cracking helpers using locally installed tools (John the
Ripper, Hashcat). Never builds shell strings - always uses subprocess.run
with argument lists. Reports clearly if a tool isn't installed.
"""
import os
import shutil
import subprocess
import tempfile

from hashing import md5_hash, sha1_hash, sha256_hash

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROCKYOU_PATH = os.path.join(PROJECT_DIR, "rockyou.txt")

# pure-Python dictionary attack: no external tool needed, so it always works,
# including on a hosted deployment with no john/hashcat installed.
WORDLIST_HASHERS = {
    "md5": md5_hash,
    "sha1": sha1_hash,
    "sha256": sha256_hash,
}


def crack_with_wordlist(hash_value: str, hash_type: str = "md5", wordlist: str = None):
    hasher = WORDLIST_HASHERS.get(hash_type.lower())
    if hasher is None:
        return {"success": False, "error": f"Unsupported hash_type: {hash_type}. Use md5, sha1 or sha256."}

    wordlist_path = wordlist or ROCKYOU_PATH
    if not os.path.isfile(wordlist_path):
        return {"success": False, "error": f"Wordlist not found: {wordlist_path}"}

    target = hash_value.strip().lower()
    tried = 0
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            word = line.rstrip("\n").rstrip("\r")
            if not word:
                continue
            tried += 1
            if hasher(word) == target:
                return {"success": True, "cracked": True, "password": word, "tried": tried}
    return {"success": True, "cracked": False, "password": None, "tried": tried}

# maps a user-facing hash type name to the hashcat mode number
HASHCAT_MODES = {
    "md5": "0",
    "sha1": "100",
    "sha256": "1400",
    "ntlm": "1000",
}

# maps a user-facing hash type name to a John "--format"
JOHN_FORMATS = {
    "md5": "raw-md5",
    "sha1": "raw-sha1",
    "sha256": "raw-sha256",
    "ntlm": "nt",
}


def _tool_path(name: str):
    return shutil.which(name)


def crack_with_john(hash_value: str, hash_type: str = "md5", wordlist: str = None):
    tool = _tool_path("john")
    if not tool:
        return {"success": False, "error": "John the Ripper is not installed or not on PATH."}

    fmt = JOHN_FORMATS.get(hash_type.lower())
    if not fmt:
        return {"success": False, "error": f"Unsupported hash_type for John: {hash_type}"}

    wordlist_path = wordlist or ROCKYOU_PATH
    if not os.path.isfile(wordlist_path):
        return {"success": False, "error": f"Wordlist not found: {wordlist_path}"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".hash", delete=False) as f:
        f.write(hash_value.strip() + "\n")
        hash_file = f.name

    try:
        cmd = [tool, f"--format={fmt}", f"--wordlist={wordlist_path}", hash_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        show_cmd = [tool, f"--format={fmt}", "--show", hash_file]
        show_result = subprocess.run(show_cmd, capture_output=True, text=True, timeout=30)

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cracked": show_result.stdout,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "John the Ripper timed out."}
    finally:
        os.unlink(hash_file)


def crack_with_hashcat(hash_value: str, hash_type: str = "md5", wordlist: str = None):
    tool = _tool_path("hashcat")
    if not tool:
        return {"success": False, "error": "Hashcat is not installed or not on PATH."}

    mode = HASHCAT_MODES.get(hash_type.lower())
    if mode is None:
        return {"success": False, "error": f"Unsupported hash_type for Hashcat: {hash_type}"}

    wordlist_path = wordlist or ROCKYOU_PATH
    if not os.path.isfile(wordlist_path):
        return {"success": False, "error": f"Wordlist not found: {wordlist_path}"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".hash", delete=False) as f:
        f.write(hash_value.strip() + "\n")
        hash_file = f.name

    try:
        cmd = [tool, "-m", mode, "-a", "0", hash_file, wordlist_path, "--potfile-disable", "-o", hash_file + ".out"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        cracked = ""
        out_path = hash_file + ".out"
        if os.path.isfile(out_path):
            with open(out_path) as f:
                cracked = f.read()
            os.unlink(out_path)

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cracked": cracked,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Hashcat timed out."}
    finally:
        os.unlink(hash_file)