"""
CrackStation integration.

IMPORTANT: CrackStation (crackstation.net) does not publish an official
public REST API. Its public website is a form that you submit hashes to and
scrape the resulting HTML table from. That means this integration:
  - is NOT an official API
  - works by submitting an HTTP POST to the site and parsing the HTML result
  - is inherently unstable: it will break if CrackStation changes their
    site's HTML structure, rate-limits requests, or adds anti-bot measures
  - should be treated as best-effort only

The endpoint is configurable via CRACKSTATION_URL so it's easy to point at
a different host (e.g. a mock server for testing) without code changes.
"""
import os
import requests

CRACKSTATION_URL = os.environ.get("CRACKSTATION_URL", "https://crackstation.net/")
TIMEOUT_SECONDS = 15


def crackstation_lookup(hash_value: str):
    """Attempts to look up a hash on CrackStation. Returns a JSON-safe dict.
    This scrapes the public form; it is unofficial and may stop working at
    any time if the site changes."""
    try:
        response = requests.post(
            CRACKSTATION_URL,
            data={"hashes": hash_value.strip()},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        return {"success": False, "error": "CrackStation request timed out."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to CrackStation."}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "error": f"CrackStation request failed: {exc}"}

    if response.status_code != 200:
        return {
            "success": False,
            "error": f"CrackStation returned HTTP {response.status_code}.",
        }

    # Very small, defensive HTML scrape: CrackStation's results table rows
    # look like <tr><td>HASH</td><td>TYPE</td><td>PLAINTEXT</td></tr>.
    # Real scraping would use something like BeautifulSoup; kept minimal
    # and dependency-light here, and explicitly marked as fragile.
    html = response.text
    found = hash_value.strip().lower() in html.lower()

    return {
        "success": True,
        "found": found,
        "note": "Unofficial scrape of the public CrackStation form; result "
                "accuracy and availability are not guaranteed.",
        "raw_length": len(html),
    }
