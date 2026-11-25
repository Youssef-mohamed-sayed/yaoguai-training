# Inspecting HTTP Security Headers

## Learning Objectives

- Fetch a site's headers and evaluate security-relevant ones.
- Understand what HSTS, CSP, X-Frame-Options, and friends defend against.
- Present findings as a clear pass/warn report.

## Introduction

HTTP response headers are a server's security posture in miniature. A handful of response headers shut down whole attack classes; their absence is a finding on any review. This lesson builds a small checker - again, run it only against sites you own or have permission to assess.

## The Headers That Matter

| Header | Defends against | Good value |
| --- | --- | --- |
| `Strict-Transport-Security` | protocol downgrade, cookie theft over HTTP | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | XSS, data injection | a defined policy, not `unsafe-inline` everywhere |
| `X-Frame-Options` | clickjacking | `DENY` or `SAMEORIGIN` |
| `X-Content-Type-Options` | MIME sniffing | `nosniff` |
| `Referrer-Policy` | leaking URLs to third parties | `strict-origin-when-cross-origin` or stricter |
| `Set-Cookie` flags | session theft | `Secure; HttpOnly; SameSite` |

## The Checker

```python
import requests

EXPECTED = {
    "strict-transport-security": "forces HTTPS",
    "content-security-policy": "limits script sources (XSS defense)",
    "x-frame-options": "blocks framing (clickjacking defense)",
    "x-content-type-options": "stops MIME sniffing",
}

def inspect(url):
    response = requests.get(url, timeout=5)
    headers = {k.lower(): v for k, v in response.headers.items()}
    print(f"{url}  [{response.status_code}]")
    for name, purpose in EXPECTED.items():
        if name in headers:
            print(f"  PASS {name}: {headers[name][:60]}")
        else:
            print(f"  WARN missing {name} ({purpose})")
    server = headers.get("server")
    if server:
        print(f"  INFO server banner: {server}")

inspect("https://example.com")
```

```text
https://example.com  [200]
  PASS strict-transport-security: max-age=31536000
  WARN missing content-security-policy (limits script sources (XSS defense))
  PASS x-frame-options: DENY
  PASS x-content-type-options: nosniff
  INFO server banner: ECS (nyb/1D2A)
```

Reading the report: missing headers are not automatically exploitable holes - they are defense-in-depth gaps worth raising. The `Server` (and `X-Powered-By`) banners leak software and version information that helps an attacker pick exploits; minimal banners are better.

Cookie flags need their own pass over `Set-Cookie` values: `Secure` (HTTPS only), `HttpOnly` (invisible to JavaScript, blunting XSS session theft), and `SameSite` (CSRF resistance).

## Common Mistakes

- Flagging a missing header as a critical vulnerability rather than a hardening gap; context and the app's actual behavior matter.
- Following redirects without noticing - the final page's headers are not the initial response's (`response.history` shows the chain).
- Hammering a site with repeated checks; cache results and be polite.

## Key Takeaways

- HSTS, CSP, X-Frame-Options, and X-Content-Type-Options each close a specific attack class; absence is a reportable hardening gap.
- Lowercase header names before lookup; HTTP headers are case-insensitive.
- Check cookie flags (`Secure`, `HttpOnly`, `SameSite`) and banner leakage alongside the headline headers.

## Practice Exercises

**Exercise 1.** Run the inspector against `https://example.com` and one site you own or administer; compare the reports.

<details>
<summary>Show a worked solution</summary>

Expect `example.com` to pass HSTS/X-Frame-Options/X-Content-Type-Options and miss CSP. Your own site will differ - every WARN is a concrete, low-effort fix at the web server level (one line in nginx/Apache config for most of them).
</details>

**Exercise 2.** Extend the checker to examine `Set-Cookie` and warn when `HttpOnly` or `Secure` is missing.

<details>
<summary>Show a worked solution</summary>

```python
cookie = headers.get("set-cookie", "")
if cookie:
    for flag in ("httponly", "secure", "samesite"):
        if flag not in cookie.lower():
            print(f"  WARN cookie missing {flag}")
else:
    print("  INFO no cookies set on this response")
```
</details>

**Exercise 3.** Print the redirect chain (`response.history`) for `http://example.com` (note: http) and confirm HSTS appears only after the HTTPS hop.

<details>
<summary>Show a worked solution</summary>

```python
r = requests.get("http://example.com", timeout=5)
for hop in [*r.history, r]:
    print(hop.status_code, hop.url)
```

```text
301 http://example.com/
200 https://example.com/
```

HSTS is only meaningful over HTTPS - browsers ignore it on plaintext responses, which is exactly why the first hop must redirect.
</details>

## Check Yourself

**Which header prevents a page from being framed, and what attack does that stop?**

<details>
<summary>Show answer</summary>

`X-Frame-Options` (or CSP's frame-ancestors), stopping clickjacking.
</details>

**Why must header lookups be case-insensitive in your checker?**

<details>
<summary>Show answer</summary>

HTTP header names are case-insensitive and servers vary their casing; normalizing to lowercase avoids false "missing" results.
</details>

**What do `Secure` and `HttpOnly` on a cookie do?**

<details>
<summary>Show answer</summary>

`Secure` sends the cookie only over HTTPS; `HttpOnly` keeps it out of JavaScript's reach, so an XSS payload cannot read the session.
</details>
