import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from hashing import md5_hash, sha1_hash, sha256_hash


# ---------------------------------------------------------------------------
# Project / wordlist paths
# ---------------------------------------------------------------------------

CURRENT_DIR = Path(__file__).resolve()


def find_project_wordlist(filename: str = "rockyou.txt") -> Path:
    """
    Find the project-level wordlist by walking upward from this file.

    Example project structure:

        D:\\yaoguai\\
        ├── rockyou.txt
        ├── backend\\
        │   └── cracking.py
        └── ...

    Returns:
        Path to the wordlist.

    Raises:
        FileNotFoundError: if the wordlist cannot be found.
    """
    for directory in [CURRENT_DIR.parent, *CURRENT_DIR.parents]:
        candidate = directory / filename

        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f"Could not find {filename} in this directory or any parent directory."
    )


def get_wordlist_path(wordlist: str = None) -> Path:
    """
    Return the explicitly supplied wordlist or the project's rockyou.txt.
    """
    if wordlist:
        path = Path(wordlist).expanduser().resolve()
    else:
        path = find_project_wordlist()

    if not path.is_file():
        raise FileNotFoundError(f"Wordlist not found: {path}")

    return path


# Pure-Python dictionary attack: no external tool needed.
WORDLIST_HASHERS = {
    "md5": md5_hash,
    "sha1": sha1_hash,
    "sha256": sha256_hash,
}


# ---------------------------------------------------------------------------
# Pure-Python dictionary attack
# ---------------------------------------------------------------------------

def crack_with_wordlist(
    hash_value: str,
    hash_type: str = "md5",
    wordlist: str = None,
):
    hasher = WORDLIST_HASHERS.get(hash_type.lower())

    if hasher is None:
        return {
            "success": False,
            "error": (
                f"Unsupported hash_type: {hash_type}. "
                "Use md5, sha1 or sha256."
            ),
        }

    try:
        wordlist_path = get_wordlist_path(wordlist)
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
        }

    target = hash_value.strip().lower()
    tried = 0

    try:
        with wordlist_path.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:

            for line in f:
                word = line.rstrip("\r\n")

                if not word:
                    continue

                tried += 1

                if hasher(word) == target:
                    return {
                        "success": True,
                        "cracked": True,
                        "password": word,
                        "tried": tried,
                        "wordlist": str(wordlist_path),
                    }

    except OSError as e:
        return {
            "success": False,
            "error": f"Failed to read wordlist: {e}",
        }

    return {
        "success": True,
        "cracked": False,
        "password": None,
        "tried": tried,
        "wordlist": str(wordlist_path),
    }


# ---------------------------------------------------------------------------
# Hashcat / John mappings
# ---------------------------------------------------------------------------

HASHCAT_MODES = {
    "md5": "0",
    "sha1": "100",
    "sha256": "1400",
    "ntlm": "1000",
}


JOHN_FORMATS = {
    "md5": "raw-md5",
    "sha1": "raw-sha1",
    "sha256": "raw-sha256",
    "ntlm": "nt",
}


def _tool_path(name: str):
    return shutil.which(name)


# ---------------------------------------------------------------------------
# John the Ripper
# ---------------------------------------------------------------------------

def crack_with_john(
    hash_value: str,
    hash_type: str = "md5",
    wordlist: str = None,
):
    tool = _tool_path("john")

    if not tool:
        return {
            "success": False,
            "error": "John the Ripper is not installed or not on PATH.",
        }

    fmt = JOHN_FORMATS.get(hash_type.lower())

    if not fmt:
        return {
            "success": False,
            "error": f"Unsupported hash_type for John: {hash_type}",
        }

    try:
        wordlist_path = get_wordlist_path(wordlist)
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
        }

    hash_file = None

    try:
        # Create a temporary file containing the target hash.
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".hash",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(hash_value.strip() + "\n")
            hash_file = f.name

        cmd = [
            tool,
            f"--format={fmt}",
            f"--wordlist={str(wordlist_path)}",
            hash_file,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        show_cmd = [
            tool,
            f"--format={fmt}",
            "--show",
            hash_file,
        ]

        show_result = subprocess.run(
            show_cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cracked": show_result.stdout,
            "wordlist": str(wordlist_path),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "John the Ripper timed out.",
        }

    except OSError as e:
        return {
            "success": False,
            "error": f"Failed to run John the Ripper: {e}",
        }

    finally:
        if hash_file and os.path.exists(hash_file):
            os.unlink(hash_file)


# ---------------------------------------------------------------------------
# Hashcat
# ---------------------------------------------------------------------------

def crack_with_hashcat(
    hash_value: str,
    hash_type: str = "md5",
    wordlist: str = None,
):
    tool = _tool_path("hashcat")

    if not tool:
        return {
            "success": False,
            "error": "Hashcat is not installed or not on PATH.",
        }

    mode = HASHCAT_MODES.get(hash_type.lower())

    if mode is None:
        return {
            "success": False,
            "error": f"Unsupported hash_type for Hashcat: {hash_type}",
        }

    try:
        wordlist_path = get_wordlist_path(wordlist)
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
        }

    hash_file = None
    out_path = None

    try:
        # Create a temporary file containing the target hash.
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".hash",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(hash_value.strip() + "\n")
            hash_file = f.name

        out_path = hash_file + ".out"

        cmd = [
            tool,
            "-m",
            mode,
            "-a",
            "0",
            hash_file,
            str(wordlist_path),
            "--potfile-disable",
            "-o",
            out_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
            timeout=120,

        cracked = ""

        if os.path.isfile(out_path):
            with open(
                out_path,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                cracked = f.read()

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cracked": cracked,
            "wordlist": str(wordlist_path),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Hashcat timed out.",
        }

    except OSError as e:
        return {
            "success": False,
            "error": f"Failed to run Hashcat: {e}",
        }

    finally:
        if hash_file and os.path.exists(hash_file):
            os.unlink(hash_file)

        if out_path and os.path.exists(out_path):
            os.unlink(out_path)