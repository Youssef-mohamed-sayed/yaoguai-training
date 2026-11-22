"""
Hashes.com integration (replaces the old crackstation.py).

Hashes.com publishes a real, documented API (https://hashes.com/en/api) for
looking up hashes against their crowd-sourced "already cracked" database:

    POST https://hashes.com/en/api/search
    form fields: key={API_KEY}, hashes[]=<hash>, hashes[]=<hash>, ...

    GET  https://hashes.com/en/api/identifier?hash=<hash>
    (optional: &extended=true for extended algorithm list)

Unlike CrackStation (which only exposes a reCAPTCHA-gated HTML form with no
API at all — see the old crackstation.py this file replaces), this is a
genuine JSON API: it takes a POST request and returns a JSON response, no
browser/captcha involved, so it works perfectly fine called from a backend
script like this one.

It does require a free Hashes.com account and an API key (from the site's
API page) — the lookup still costs the account's credits (1 credit per hash
*found*; looking a hash up that isn't found costs nothing). The key is never
hardcoded here: the caller (the Flask route) passes it through from what the
person typed into the front-end, so nobody's key ends up committed to this
file or shared between users of a hosted deployment.
"""
import requests

DEFAULT_API_KEY           = "750f5602dc5aed7bad2d960011df4790"
HASHES_COM_SEARCH_URL     = "https://hashes.com/en/api/search"
HASHES_COM_IDENTIFY_URL   = "https://hashes.com/en/api/identifier"
HASHES_COM_BALANCE_URL    = "https://hashes.com/en/api/balance"
TIMEOUT_SECONDS = 20


def hashescom_lookup(hash_value: str, api_key: str = None) -> dict:
    """Looks up a single hash against Hashes.com's database.

    Returns a dict shaped like:
      {"success": True, "cracked": True, "password": "...", "algorithm": "MD5"}
      {"success": True, "cracked": False}
      {"success": False, "error": "..."}
    """
    key = (api_key or "").strip() or DEFAULT_API_KEY
    if not key:
        return {"success": False, "error": "A Hashes.com API key is required."}

    try:
        response = requests.post(
            HASHES_COM_SEARCH_URL,
            data={"key": key},
            files={"hashes[]": (None, hash_value.strip())},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Hashes.com request timed out."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Hashes.com."}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"Hashes.com request failed: {exc}"}

    try:
        payload = response.json()
    except ValueError:
        return {"success": False, "error": f"Hashes.com returned a non-JSON response (HTTP {response.status_code})."}

    if not payload.get("success"):
        # Hashes.com's own error shape: {"success": false, "message": "..."}
        return {"success": False, "error": payload.get("message", "Hashes.com returned an error.")}

    founds = payload.get("founds") or []
    if founds:
        match = founds[0]
        return {
            "success": True,
            "cracked": True,
            "password": match.get("plaintext"),
            "algorithm": match.get("algorithm"),
            "salt": match.get("salt") or None,
        }

    return {"success": True, "cracked": False}


def hashescom_balance(api_key: str = None) -> dict:
    """Checks the Hashes.com wallet balances and credits."""
    key = (api_key or "").strip() or DEFAULT_API_KEY
    try:
        response = requests.get(
            HASHES_COM_BALANCE_URL,
            params={"key": key},
            timeout=TIMEOUT_SECONDS,
        )
        return response.json()
    except Exception as exc:
        return {"success": False, "error": f"Hashes.com balance request failed: {exc}"}


def hashescom_identify(hash_value: str, extended: bool = True) -> dict:
    """Identifies the likely hash algorithm(s) for a given hash string.

    Calls GET https://hashes.com/en/api/identifier (no API key required).

    Returns a dict shaped like:
      {"success": True, "algorithms": ["MD5", ...]}
      {"success": False, "error": "..."}
    """
    params = {"hash": hash_value.strip()}
    if extended:
        params["extended"] = "true"

    try:
        response = requests.get(
            HASHES_COM_IDENTIFY_URL,
            params=params,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Hashes.com request timed out."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to Hashes.com."}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"Hashes.com request failed: {exc}"}

    try:
        payload = response.json()
    except ValueError:
        return {"success": False, "error": f"Hashes.com returned a non-JSON response (HTTP {response.status_code})."}

    if not payload.get("success"):
        return {"success": False, "error": payload.get("message", "Could not identify hash algorithm.")}

    return {"success": True, "algorithms": payload.get("algorithms", [])}
