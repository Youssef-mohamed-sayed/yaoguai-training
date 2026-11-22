"""
Yaoguai-Crypto — one-command app.

    python app.py

starts the Flask REST API (encoding, encryption, hashing, cracking) AND
serves the front-end website from the same server, then opens it in your
browser at http://127.0.0.1:5000/.  All API routes accept and return JSON.
"""
import base64
import binascii
import io
import os
import threading
import webbrowser

from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

import encoding
import encryption
import decryption
import hashing
import crack
import hashescom
import auth
import database
from rsa_core import rsa_encrypt_int, rsa_decrypt_int

HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", 5000))

# Site folder = ../public (holds index.html, lessons/, js/, assets/)
SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024  # Includes multipart overhead for 2 MB avatars


@app.before_request
def validate_auth_request():
    is_auth = request.path.startswith("/api/auth/")
    if not is_auth and request.content_length and request.content_length > 1024 * 1024:
        raise RequestEntityTooLarge()
    if is_auth and request.method == "POST" and request.is_json:
        if not isinstance(request.get_json(silent=True), dict):
            return err("Request body must be a valid JSON object.", 400)


# john/hashcat need external binaries that a hosted deployment won't have,
# so they're switched off when hosted on Vercel. /api/crack/wordlist is pure
# Python (no subprocess, no network) and stays available either way.
HOSTED = bool(os.environ.get("VERCEL"))
CRACK_PATHS = ("/api/crack/john", "/api/crack/hashcat")


@app.before_request
def block_cracking_when_hosted():
    if HOSTED and request.path.startswith(CRACK_PATHS):
        return jsonify({"success": False,
                        "error": "This cracking tool needs a local program that isn't available on the hosted version."}), 403


@app.after_request
def allow_local_cors(resp):
    if request.path.startswith(("/api/auth/", "/api/user/")):
        resp.headers["Cache-Control"] = "no-store"
    # Lets the pages call the API even if index.html is opened straight from disk.
    resp.headers.setdefault("Access-Control-Allow-Origin", "*")
    resp.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization")
    resp.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
    return resp


# ---------------------------------------------------------- FRONT-END SITE
# Only these site folders are public; scripts/ (source, wordlists) is not.
@app.route("/")
@app.route("/index.html")
def site_index():
    return send_from_directory(SITE_ROOT, "index.html")


@app.route("/tools")
@app.route("/tools.html")
def site_tools():
    return send_from_directory(SITE_ROOT, "tools.html")


@app.route("/favicon.ico")
def site_favicon():
    return send_from_directory(os.path.join(SITE_ROOT, "assets", "images"), "favicon.ico")


@app.route("/<any(lessons, js, assets):folder>/<path:filename>")
def site_files(folder, filename):
    # New uploads live in the shared database, including on serverless workers.
    if folder == "assets" and filename.startswith("avatars/"):
        avatar_name = filename[len("avatars/"):]
        avatar = auth.get_avatar(avatar_name)
        if avatar:
            return send_file(io.BytesIO(bytes(avatar["data"])), mimetype=avatar["content_type"])
        if not auth.DATABASE_URL and not auth.is_read_only:
            return send_from_directory(auth.AVATARS_DIR, avatar_name)
        return not_found(None)
    return send_from_directory(os.path.join(SITE_ROOT, folder), filename)


def ok(result):
    return jsonify({"success": True, "result": result})


def err(message, status=400):
    return jsonify({"success": False, "error": message}), status


def account_storage_unavailable(exc):
    app.logger.error("Account database is unavailable (%s)", type(exc).__name__)
    return err("Account storage is temporarily unavailable. Please try again later.", 503)


for database_error in (*database.DATABASE_ERRORS, database.ConfigurationError):
    app.register_error_handler(database_error, account_storage_unavailable)


def get_auth_user():
    """Identify the account exclusively from its verified bearer session."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    if not token:
        return None
    try:
        payload = auth.decode_token(token)
        user_id = int(payload.get("user_id") or payload.get("sub"))
        return auth.get_user_by_id(user_id)
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Your session is invalid or has expired. Please log in again.")


def require_auth():
    try:
        user = get_auth_user()
    except ValueError as exc:
        return None, err(str(exc), 401)
    if not user:
        return None, err("Authentication required. Please log in.", 401)
    return user, None


def get_json():
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    return data


def require(data, *fields):
    missing = [f for f in fields if f not in data or data[f] in (None, "")]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    if request.path.startswith("/api/auth/"):
        return err("Upload too large. Avatar files must be no more than 2 MB.", 413)
    return err("File too large (max 1 MB).", 413)


@app.errorhandler(404)
def not_found(e):
    if not request.path.startswith("/api/"):
        return "404 - page not found", 404
    return err("Endpoint not found.", 404)


@app.errorhandler(500)
def server_error(e):
    # never leak stack traces
    return err("Internal server error.", 500)


# ---------------------------------------------------------------- ENCODING
@app.route("/api/encoding/hex/encode", methods=["POST"])
def hex_encode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.hex_encode(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encoding/hex/decode", methods=["POST"])
def hex_decode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.hex_decode(data["data"]))
    except (ValueError, binascii.Error):
        return err("Invalid hexadecimal input.")


@app.route("/api/encoding/base64/encode", methods=["POST"])
def base64_encode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.base64_encode(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encoding/base64/decode", methods=["POST"])
def base64_decode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.base64_decode(data["data"]))
    except (ValueError, binascii.Error):
        return err("Invalid Base64 input.")


@app.route("/api/encoding/ascii/encode", methods=["POST"])
def ascii_encode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.ascii_encode(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encoding/ascii/decode", methods=["POST"])
def ascii_decode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.ascii_decode(data["data"]))
    except ValueError:
        return err("Invalid ASCII code list.")


@app.route("/api/encoding/url/encode", methods=["POST"])
def url_encode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.url_encode(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encoding/url/decode", methods=["POST"])
def url_decode_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(encoding.url_decode(data["data"]))
    except ValueError as e:
        return err(str(e))


# -------------------------------------------------------------- ENCRYPTION
@app.route("/api/encryption/xor", methods=["POST"])
def xor_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(encryption.xor_encrypt(data["data"], data["key"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encryption/rc4", methods=["POST"])
def rc4_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(encryption.rc4_encrypt(data["data"], data["key"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encryption/des", methods=["POST"])
def des_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(encryption.des_encrypt(data["data"], data["key"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encryption/3des", methods=["POST"])
def triple_des_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "key1", "key2")
        return ok(encryption.triple_des_encrypt(
            data["data"], data["key1"], data["key2"], data.get("key3")))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encryption/aes", methods=["POST"])
def aes_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(encryption.aes_encrypt(data["data"], data["key"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/encryption/rsa/generate-keys", methods=["POST"])
def rsa_generate_keys_route():
    data = get_json()
    bits = int(data.get("bits", 512))
    if bits < 64 or bits > 2048 or bits % 2 != 0:
        return err("bits must be an even number between 64 and 2048 (demo-sized).")
    keys = encryption.rsa_generate_keys(bits)
    # strings, not numbers: JSON numbers this large lose precision in JavaScript
    return ok({"n": str(keys["n"]), "e": str(keys["e"]), "d": str(keys["d"])})


@app.route("/api/encryption/rsa", methods=["POST"])
def rsa_encrypt_route():
    data = get_json()
    try:
        require(data, "data", "e", "n")
        return ok(encryption.rsa_encrypt(data["data"], int(data["e"]), int(data["n"])))
    except ValueError as e:
        return err(str(e))


# -------------------------------------------------------------- DECRYPTION
@app.route("/api/decryption/xor", methods=["POST"])
def xor_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(decryption.xor_decrypt(data["data"], data["key"]))
    except (ValueError, binascii.Error):
        return err("Invalid key or malformed ciphertext.")


@app.route("/api/decryption/rc4", methods=["POST"])
def rc4_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(decryption.rc4_decrypt(data["data"], data["key"]))
    except (ValueError, binascii.Error):
        return err("Invalid key or malformed ciphertext.")


@app.route("/api/decryption/des", methods=["POST"])
def des_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(decryption.des_decrypt(data["data"], data["key"]))
    except (ValueError, binascii.Error):
        return err("Invalid key or malformed ciphertext.")


@app.route("/api/decryption/3des", methods=["POST"])
def triple_des_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "key1", "key2")
        return ok(decryption.triple_des_decrypt(
            data["data"], data["key1"], data["key2"], data.get("key3")))
    except (ValueError, binascii.Error):
        return err("Invalid key(s) or malformed ciphertext.")


@app.route("/api/decryption/aes", methods=["POST"])
def aes_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "key")
        return ok(decryption.aes_decrypt(data["data"], data["key"]))
    except (ValueError, binascii.Error):
        return err("Invalid key or malformed ciphertext.")


@app.route("/api/decryption/rsa", methods=["POST"])
def rsa_decrypt_route():
    data = get_json()
    try:
        require(data, "data", "d", "n")
        return ok(decryption.rsa_decrypt(data["data"], int(data["d"]), int(data["n"])))
    except ValueError as e:
        return err("Invalid RSA parameters.")


# ----------------------------------------------------------------- HASHING
@app.route("/api/hashing/md5", methods=["POST"])
def md5_hash_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(hashing.md5_hash(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashing/sha1", methods=["POST"])
def sha1_hash_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(hashing.sha1_hash(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashing/sha256", methods=["POST"])
def sha256_hash_route():
    data = get_json()
    try:
        require(data, "data")
        return ok(hashing.sha256_hash(data["data"]))
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashing/bcrypt", methods=["POST"])
def bcrypt_hash_route():
    data = get_json()
    try:
        require(data, "data")
        rounds = int(data.get("rounds", 12))
        return ok(hashing.bcrypt_hash(data["data"], rounds))
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashing/bcrypt/verify", methods=["POST"])
def bcrypt_verify_route():
    data = get_json()
    try:
        require(data, "data", "hash")
        return ok(hashing.bcrypt_verify(data["data"], data["hash"]))
    except ValueError as e:
        return err(str(e))


# ------------------------------------------------------------------- CRACK
@app.route("/api/crack/wordlist", methods=["POST"])
def crack_wordlist_route():
    data = get_json()
    try:
        require(data, "hash")
        result = crack.crack_with_wordlist(
            data["hash"], data.get("hash_type", "md5"), data.get("wordlist"))
        return jsonify(result)
    except ValueError as e:
        return err(str(e))


@app.route("/api/crack/john", methods=["POST"])
def crack_john_route():
    data = get_json()
    try:
        require(data, "hash")
        result = crack.crack_with_john(
            data["hash"], data.get("hash_type", "md5"), data.get("wordlist"))
        return jsonify(result)
    except ValueError as e:
        return err(str(e))


@app.route("/api/crack/hashcat", methods=["POST"])
def crack_hashcat_route():
    data = get_json()
    try:
        require(data, "hash")
        result = crack.crack_with_hashcat(
            data["hash"], data.get("hash_type", "md5"), data.get("wordlist"))
        return jsonify(result)
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashescom", methods=["POST"])
def hashescom_route():
    data = get_json()
    try:
        require(data, "hash")
        api_key = data.get("api_key") or hashescom.DEFAULT_API_KEY
        result = hashescom.hashescom_lookup(data["hash"], api_key)
        return jsonify(result)
    except ValueError as e:
        return err(str(e))


@app.route("/api/hashescom/balance", methods=["GET", "POST"])
def hashescom_balance_route():
    data = get_json() if request.method == "POST" else request.args
    api_key = data.get("api_key") or data.get("key") or hashescom.DEFAULT_API_KEY
    result = hashescom.hashescom_balance(api_key)
    return jsonify(result)


@app.route("/api/hashescom/identify", methods=["POST"])
def hashescom_identify_route():
    data = get_json()
    try:
        require(data, "hash")
        extended = str(data.get("extended", "false")).lower() in ("true", "1", "yes")
        result = hashescom.hashescom_identify(data["hash"], extended=extended)
        return jsonify(result)
    except ValueError as e:
        return err(str(e))


# ---------------------------------------------------- FILE ENCRYPT / DECRYPT
@app.route("/api/file/transform", methods=["POST"])
def file_transform_route():
    action = request.form.get("action", "encrypt").lower().strip()
    algo = request.form.get("algo", "des").lower().strip()

    # For hybrid decrypt called with JSON payload
    if not request.files and request.is_json:
        data = request.get_json(silent=True) or {}
        action = "decrypt"
        algo = "hybrid"
        try:
            require(data, "encrypted_key", "d", "n")
            if "encrypted_file_b64" not in data or not data["encrypted_file_b64"]:
                return err("Encrypted file payload is required.")
            d_int = int(str(data["d"]).strip())
            n_int = int(str(data["n"]).strip())
            enc_key_int = int(str(data["encrypted_key"]).strip())
            session_key_int = rsa_decrypt_int(enc_key_int, d_int, n_int)
            session_key_bytes = session_key_int.to_bytes(8, "big")
            encrypted_file = base64.b64decode(data["encrypted_file_b64"])
            plain = encryption.des_decrypt_file_bytes(encrypted_file, session_key_bytes.hex())
            orig_name = secure_filename(str(data.get("original_filename") or "decrypted.txt").strip()) or "decrypted.txt"
            return send_file(io.BytesIO(plain), as_attachment=True, download_name=orig_name, mimetype="application/octet-stream")
        except Exception as e:
            return err(f"Hybrid decryption failed: {e}")

    if "file" not in request.files or not request.files["file"].filename:
        return err("No file uploaded.")

    file = request.files["file"]
    raw_bytes = file.read()
    if not raw_bytes:
        return err("Uploaded file is empty.")
    orig_name = secure_filename(file.filename) or "file.txt"

    # 1. Hashing
    if action == "hash":
        try:
            if algo == "md5":
                h = hashing.md5_hash_bytes(raw_bytes)
            elif algo == "sha1":
                h = hashing.sha1_hash_bytes(raw_bytes)
            elif algo == "sha256":
                h = hashing.sha256_hash_bytes(raw_bytes)
            elif algo == "bcrypt":
                rounds = int(request.form.get("rounds", 10))
                h = hashing.bcrypt_hash_bytes(raw_bytes, rounds)
            else:
                return err(f"Unsupported hash algorithm: {algo}")
            return ok({"algo": algo, "hash": h, "filename": orig_name})
        except Exception as e:
            return err(f"Hashing failed: {e}")

    # 2. Hash Verification
    if action == "verify":
        expected = request.form.get("expected_hash", "").strip()
        if not expected:
            return err("Expected hash is required.")
        try:
            if algo in ("md5", "sha1", "sha256"):
                if algo == "md5":
                    actual = hashing.md5_hash_bytes(raw_bytes)
                elif algo == "sha1":
                    actual = hashing.sha1_hash_bytes(raw_bytes)
                else:
                    actual = hashing.sha256_hash_bytes(raw_bytes)
                match = (actual.lower() == expected.lower())
                return ok({"algo": algo, "match": match, "actual_hash": actual, "expected_hash": expected, "filename": orig_name})
            elif algo == "bcrypt":
                match = hashing.bcrypt_verify_bytes(raw_bytes, expected)
                return ok({"algo": algo, "match": match, "expected_hash": expected, "filename": orig_name})
            else:
                return err(f"Unsupported verify algorithm: {algo}")
        except Exception as e:
            return err(f"Verification failed: {e}")

    # 3. Encryption
    if action == "encrypt":
        try:
            if algo == "des":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.des_encrypt_file_bytes(raw_bytes, key)
                ext = ".des.enc"
            elif algo == "aes":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.aes_encrypt_file_bytes(raw_bytes, key)
                ext = ".aes.enc"
            elif algo == "3des":
                k1 = request.form.get("key1", "").strip()
                k2 = request.form.get("key2", "").strip()
                k3 = request.form.get("key3", "").strip() or None
                if not k1 or not k2:
                    return err("Key 1 and Key 2 are required for 3DES.")
                out = encryption.triple_des_encrypt_file_bytes(raw_bytes, k1, k2, k3)
                ext = ".3des.enc"
            elif algo == "rc4":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.rc4_file_bytes(raw_bytes, key)
                ext = ".rc4.enc"
            elif algo == "xor":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.xor_file_bytes(raw_bytes, key)
                ext = ".xor.enc"
            elif algo == "hybrid":
                try:
                    e = int(str(request.form.get("e", "")).strip())
                    n = int(str(request.form.get("n", "")).strip())
                except (ValueError, TypeError):
                    return err("Valid RSA public key (e and n integers) is required.")
                if n <= 2**64:
                    return err("RSA key too small to wrap an 8-byte session key. Generate at least a 128-bit key pair.")
                session_key_bytes = os.urandom(8)
                encrypted_file = encryption.des_encrypt_file_bytes(raw_bytes, session_key_bytes.hex())
                session_key_int = int.from_bytes(session_key_bytes, "big")
                encrypted_key = rsa_encrypt_int(session_key_int, e, n)
                return ok({
                    "encrypted_file_b64": base64.b64encode(encrypted_file).decode("ascii"),
                    "encrypted_key": str(encrypted_key),
                    "original_filename": orig_name
                })
            else:
                return err(f"Unsupported encrypt algorithm: {algo}")

            download_name = f"{orig_name}{ext}"
            return send_file(io.BytesIO(out), as_attachment=True, download_name=download_name, mimetype="application/octet-stream")
        except Exception as e:
            return err(f"Encryption failed: {e}")

    # 4. Encoding
    if action == "encode":
        try:
            if algo == "base64":
                out = encoding.base64_encode_bytes(raw_bytes)
                ext = ".b64"
            elif algo == "hex":
                out = encoding.hex_encode_bytes(raw_bytes)
                ext = ".hex"
            elif algo == "ascii":
                out = encoding.ascii_encode_bytes(raw_bytes)
                ext = ".ascii"
            elif algo == "url":
                out = encoding.url_encode_bytes(raw_bytes)
                ext = ".url"
            else:
                return err(f"Unsupported encode algorithm: {algo}")

            download_name = f"{orig_name}{ext}"
            return send_file(io.BytesIO(out), as_attachment=True, download_name=download_name, mimetype="application/octet-stream")
        except Exception as e:
            return err(f"Encoding failed: {e}")

    # 5. Decryption
    if action == "decrypt":
        restore_name = secure_filename(str(request.form.get("original_filename", "")).strip()) or "decrypted.txt"
        try:
            if algo == "des":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.des_decrypt_file_bytes(raw_bytes, key)
            elif algo == "aes":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.aes_decrypt_file_bytes(raw_bytes, key)
            elif algo == "3des":
                k1 = request.form.get("key1", "").strip()
                k2 = request.form.get("key2", "").strip()
                k3 = request.form.get("key3", "").strip() or None
                if not k1 or not k2:
                    return err("Key 1 and Key 2 are required for 3DES.")
                out = encryption.triple_des_decrypt_file_bytes(raw_bytes, k1, k2, k3)
            elif algo == "rc4":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.rc4_file_bytes(raw_bytes, key)
            elif algo == "xor":
                key = request.form.get("key", "").strip()
                if not key:
                    return err("Key is required.")
                out = encryption.xor_file_bytes(raw_bytes, key)
            elif algo == "hybrid":
                try:
                    d_int = int(str(request.form.get("d", "")).strip())
                    n_int = int(str(request.form.get("n", "")).strip())
                    enc_key_int = int(str(request.form.get("encrypted_key", "")).strip())
                except (ValueError, TypeError) as e:
                    return err(f"Invalid RSA parameters: {e}")
                try:
                    file_str = raw_bytes.decode("ascii").strip()
                    base64.b64decode(file_str, validate=True)
                    encrypted_file = base64.b64decode(file_str)
                except Exception:
                    encrypted_file = raw_bytes
                session_key_int = rsa_decrypt_int(enc_key_int, d_int, n_int)
                session_key_bytes = session_key_int.to_bytes(8, "big")
                out = encryption.des_decrypt_file_bytes(encrypted_file, session_key_bytes.hex())
            else:
                return err(f"Unsupported decrypt algorithm: {algo}")

            return send_file(io.BytesIO(out), as_attachment=True, download_name=restore_name, mimetype="application/octet-stream")
        except Exception as e:
            return err(f"Decryption failed: {e}")

    # 6. Decoding
    if action == "decode":
        restore_name = secure_filename(str(request.form.get("original_filename", "")).strip()) or "decoded.txt"
        try:
            if algo == "base64":
                out = encoding.base64_decode_bytes(raw_bytes)
            elif algo == "hex":
                out = encoding.hex_decode_bytes(raw_bytes)
            elif algo == "ascii":
                out = encoding.ascii_decode_bytes(raw_bytes)
            elif algo == "url":
                out = encoding.url_decode_bytes(raw_bytes)
            else:
                return err(f"Unsupported decode algorithm: {algo}")

            return send_file(io.BytesIO(out), as_attachment=True, download_name=restore_name, mimetype="application/octet-stream")
        except Exception as e:
            return err(f"Decoding failed: {e}")

    return err(f"Invalid action: {action}")


@app.route("/api/file/encrypt/des", methods=["POST"])
def file_encrypt_des_route():
    if "file" not in request.files:
        return err("No file uploaded.")
    file = request.files["file"]
    if not file or not file.filename:
        return err("No file selected.")

    orig_name = secure_filename(file.filename)
    if not orig_name.lower().endswith(".txt"):
        return err("Only .txt files are supported.")

    key = request.form.get("key", "").strip()
    if not key:
        return err("Key is required.")

    raw_bytes = file.read()
    if not raw_bytes:
        return err("Uploaded file is empty.")

    try:
        encrypted = encryption.des_encrypt_file_bytes(raw_bytes, key)
    except Exception as e:
        return err(f"Encryption failed: {e}")

    download_name = f"{orig_name}.des.enc"
    return send_file(
        io.BytesIO(encrypted),
        as_attachment=True,
        download_name=download_name,
        mimetype="application/octet-stream"
    )


@app.route("/api/file/decrypt/des", methods=["POST"])
def file_decrypt_des_route():
    if "file" not in request.files:
        return err("No file uploaded.")
    file = request.files["file"]
    if not file or not file.filename:
        return err("No file selected.")

    key = request.form.get("key", "").strip()
    if not key:
        return err("Key is required.")

    orig_name = request.form.get("original_filename", "").strip()
    if not orig_name:
        upl_name = secure_filename(file.filename)
        if upl_name.endswith(".des.enc"):
            orig_name = upl_name[:-8]
        elif upl_name.endswith(".enc"):
            orig_name = upl_name[:-4]
        else:
            orig_name = "decrypted.txt"
    else:
        orig_name = secure_filename(orig_name)

    raw_bytes = file.read()
    if not raw_bytes:
        return err("Uploaded file is empty.")

    try:
        plain = encryption.des_decrypt_file_bytes(raw_bytes, key)
    except Exception as e:
        return err(f"Decryption failed: {e}")

    return send_file(
        io.BytesIO(plain),
        as_attachment=True,
        download_name=orig_name,
        mimetype="application/octet-stream"
    )


@app.route("/api/file/encrypt/hybrid", methods=["POST"])
def file_encrypt_hybrid_route():
    if "file" not in request.files:
        return err("No file uploaded.")
    file = request.files["file"]
    if not file or not file.filename:
        return err("No file selected.")

    orig_name = secure_filename(file.filename)
    if not orig_name.lower().endswith(".txt"):
        return err("Only .txt files are supported.")

    raw_bytes = file.read()
    if not raw_bytes:
        return err("Uploaded file is empty.")

    try:
        e = int(str(request.form.get("e", "")).strip())
        n = int(str(request.form.get("n", "")).strip())
    except (ValueError, TypeError):
        return err("Valid RSA public key (e and n integers) is required.")

    if n <= 2**64:
        return err("RSA key too small to wrap an 8-byte session key. Generate at least a 128-bit key pair.")

    try:
        session_key_bytes = os.urandom(8)
        encrypted_file = encryption.des_encrypt_file_bytes(raw_bytes, session_key_bytes.hex())
        session_key_int = int.from_bytes(session_key_bytes, "big")
        encrypted_key = rsa_encrypt_int(session_key_int, e, n)
    except Exception as exc:
        return err(f"Hybrid encryption failed: {exc}")

    return ok({
        "encrypted_file_b64": base64.b64encode(encrypted_file).decode("ascii"),
        "encrypted_key": str(encrypted_key),
        "original_filename": orig_name
    })


@app.route("/api/file/decrypt/hybrid", methods=["POST"])
def file_decrypt_hybrid_route():
    data = request.get_json(silent=True) or {}
    if not data and request.form:
        data = request.form.to_dict()
        if "file" in request.files:
            file_bytes = request.files["file"].read()
            try:
                file_str = file_bytes.decode("ascii").strip()
                base64.b64decode(file_str, validate=True)
                data["encrypted_file_b64"] = file_str
            except Exception:
                data["encrypted_file_b64"] = base64.b64encode(file_bytes).decode("ascii")

    try:
        require(data, "encrypted_key", "d", "n")
        if "encrypted_file_b64" not in data or not data["encrypted_file_b64"]:
            return err("Encrypted file payload is required.")
        d_int = int(str(data["d"]).strip())
        n_int = int(str(data["n"]).strip())
        enc_key_int = int(str(data["encrypted_key"]).strip())
    except (ValueError, TypeError) as e:
        return err(f"Invalid RSA parameters: {e}")

    try:
        session_key_int = rsa_decrypt_int(enc_key_int, d_int, n_int)
        session_key_bytes = session_key_int.to_bytes(8, "big")
        encrypted_file = base64.b64decode(data["encrypted_file_b64"])
        plain = encryption.des_decrypt_file_bytes(encrypted_file, session_key_bytes.hex())
    except Exception as e:
        return err(f"Hybrid decryption failed: {e}")

    orig_name = secure_filename(str(data.get("original_filename") or "decrypted.txt").strip())
    if not orig_name:
        orig_name = "decrypted.txt"
    return send_file(
        io.BytesIO(plain),
        as_attachment=True,
        download_name=orig_name,
        mimetype="application/octet-stream"
    )


# ------------------------------------------------ AUTH & USER SESSIONS (JWT)
@app.route("/api/auth/register", methods=["POST"])
def auth_register_route():
    data = {}
    avatar_bytes = None
    avatar_filename = None

    if request.form:
        data.update(request.form.to_dict())
    if request.is_json:
        data.update(request.get_json(silent=True) or {})

    if "avatar" in request.files:
        f = request.files["avatar"]
        if f and f.filename:
            avatar_bytes = f.read()
            avatar_filename = secure_filename(f.filename)
    elif "avatar_b64" in data and data["avatar_b64"]:
        try:
            avatar_bytes = base64.b64decode(data["avatar_b64"], validate=True)
            avatar_filename = secure_filename(data.get("avatar_filename") or "avatar.png")
        except Exception:
            return err("Invalid base64 payload for avatar image.", 400)

    username = data.get("username", "")
    password = data.get("password", "")

    try:
        user_info, token = auth.register_user(
            username=username,
            password=password,
            avatar_bytes=avatar_bytes,
            avatar_filename=avatar_filename
        )
        return ok({"user": user_info, "token": token})
    except auth.ValidationError as val_err:
        return jsonify(success=False, error=str(val_err), errors=val_err.errors), 400
    except database.INTEGRITY_ERRORS:
        return err("A user with that username already exists.", 400)
    except ValueError as val_err:
        return err(str(val_err), 400)
    except (*database.DATABASE_ERRORS, database.ConfigurationError) as exc:
        return account_storage_unavailable(exc)
    except Exception as exc:
        app.logger.exception("Registration failed")
        return err("Registration is temporarily unavailable. Please try again later.", 500)


@app.route("/api/auth/login", methods=["POST"])
def auth_login_route():
    data = {}
    if request.form:
        data.update(request.form.to_dict())
    if request.is_json:
        data.update(request.get_json(silent=True) or {})

    username = data.get("username", "")
    password = data.get("password", "")

    try:
        user_info, token = auth.login_user(username, password)
        return ok({"user": user_info, "token": token})
    except auth.ValidationError as val_err:
        return jsonify(success=False, error=str(val_err), errors=val_err.errors), 400
    except ValueError as val_err:
        return err(str(val_err), 401)
    except (*database.DATABASE_ERRORS, database.ConfigurationError) as exc:
        return account_storage_unavailable(exc)
    except Exception as exc:
        app.logger.exception("Login failed")
        return err("Login is temporarily unavailable. Please try again later.", 500)


@app.route("/api/auth/me", methods=["GET"])
def auth_me_route():
    user, auth_err = require_auth()
    if auth_err:
        return auth_err
    return ok({"user": user})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout_route():
    user, auth_err = require_auth()
    if auth_err:
        return auth_err
    auth.revoke_token(request.headers["Authorization"][7:].strip())
    return ok({"logged_out": True})


@app.route("/api/auth/avatar", methods=["POST"])
def auth_avatar_route():
    user, auth_err = require_auth()
    if auth_err:
        return auth_err

    avatar_bytes = None
    avatar_filename = None

    if "avatar" in request.files:
        f = request.files["avatar"]
        if f and f.filename:
            avatar_bytes = f.read()
            avatar_filename = secure_filename(f.filename)
    else:
        data = request.get_json(silent=True) or (request.form.to_dict() if request.form else {})
        if "avatar_b64" in data and data["avatar_b64"]:
            try:
                avatar_bytes = base64.b64decode(data["avatar_b64"], validate=True)
                avatar_filename = secure_filename(data.get("avatar_filename") or "avatar.png")
            except Exception:
                return err("Invalid base64 payload for avatar image.", 400)

    if not avatar_bytes or not avatar_filename:
        return err("Please select a .png or .jpg avatar file to upload.", 400)

    try:
        avatar_url = auth.update_user_avatar(user["id"], avatar_bytes, avatar_filename)
        return ok({"avatar_url": avatar_url})
    except ValueError as val_err:
        return err(str(val_err), 400)
    except (*database.DATABASE_ERRORS, database.ConfigurationError) as exc:
        return account_storage_unavailable(exc)
    except Exception as exc:
        app.logger.exception("Avatar update failed")
        return err("Avatar upload is temporarily unavailable. Please try again later.", 500)


@app.route("/api/user/progress", methods=["GET", "POST"])
def user_progress_route():
    user, auth_err = require_auth()
    if auth_err:
        return auth_err

    if request.method == "GET":
        progress = auth.get_progress(user["id"])
        return ok({"progress": progress})

    # POST: update / save progress
    payload = request.get_json(silent=True) or (request.form.to_dict() if request.form else {})
    if not isinstance(payload, dict):
        return err("Progress must be a JSON object.", 400)
    current = auth.get_progress(user["id"])

    if "progress" in payload and isinstance(payload["progress"], dict):
        current.update(payload["progress"])
    elif "lesson_id" in payload:
        lid = payload["lesson_id"]
        if not isinstance(lid, str) or not lid or len(lid) > 100:
            return err("Lesson ID must be a non-empty string of at most 100 characters.", 400)
        if isinstance(payload.get("data"), dict):
            current[lid] = payload["data"]
        else:
            current[lid] = payload.get("data", True)

    auth.save_progress(user["id"], current)
    return ok({"progress": current})


if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}/"
    print(f"\n  YAOGUAI is running at {url}  (Ctrl+C to stop)\n")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(debug=False, host=HOST, port=PORT)
