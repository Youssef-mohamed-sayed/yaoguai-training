# Yaoguai Network

Network Essentials cybersecurity learning platform. An independent Flask sibling
of Yaoguai Crypto with its black/white/deep-red identity, local fonts and Yaoguai artwork.

The complete original course is in [network-essentials](network-essentials/README.md).
That README is the educational index; this README documents the application.

## Features

- Eight modules, 33 lesson/final-challenge files, eight module landing pages and a course guide.
- All 42 course Markdown files integrated; README-driven order and clean URLs.
- Hierarchical sidebar, breadcrumbs, section outline and previous/next navigation.
- Sanitized Markdown, scrollable tables, checklists, ASCII diagrams, highlighted code and copy buttons.
- Source-backed automatic closed-question checks; self-assessed practice for open activities.
- 35 exact CTF flag checks, including the bonus subnet challenge.
- Progressive hints and closed solutions. Reading/disclosures work without JavaScript.
- Search across actual content, excluding hidden hints and solutions.
- Browser-local lessons, exercises, solved flags and resume. No accounts or cross-device sync.
- Responsive UI, keyboard controls, focus indicators and reduced-motion support.
- Integration tests, content integrity checks, Chromium browser tests and GitHub Actions.

## Technology Stack

Python 3.13, Flask, Jinja, vanilla JavaScript modules and CSS. Markdown uses
markdown-it-py, nh3 sanitization, Beautiful Soup presentation transforms and Pygments
highlighting. No frontend build step or remote scripts are needed.

Crypto uses static HTML and a Flask API, with account-backed progress. Network
keeps Flask and its frontend visual primitives, adding an application factory and
templates for Markdown. The per-page browser progress pattern uses an independent
Network namespace. Crypto authentication and crypto endpoints are not copied.

## Project Structure

~~~text
main.py                         Flask/WSGI entry point and local runner
network_yaoguai/
  __init__.py                   factory, configuration, errors, security headers
  routes.py                     dashboard, reader, search, checks, local assets
  course.py                     discovery, order, metadata and navigation
  markdown_view.py              sanitized Markdown and learning components
  exercises.py                  source-backed closed-question keys
  templates/                    shared layout and page templates
network-essentials/              original educational sources, unchanged
public/assets/
  theme.css                     adapted Yaoguai family primitives
  network.css                   Network components and responsive rules
  js/                           progress, activities and page wiring
  fonts/                        local fonts and OFL licenses
  images/                       reused Yaoguai branding
tests/                          integration and browser tests
.github/workflows/test.yml      syntax, integration and browser checks
requirements.txt                application dependencies
requirements-dev.txt            optional browser-test dependencies
.python-version                 Python 3.13
vercel.json                     native Flask and content inclusion
~~~

## Course Content

1. Networking Fundamentals — OSI, TCP/IP, comparison, encapsulation.
2. Addressing — IPv4, MAC, subnetting, ARP.
3. Common Protocols — HTTP/HTTPS, DNS, DHCP, FTP, SSH, ARP, ICMP.
4. Ports & TCP — ports/services, TCP/UDP, handshake.
5. Network Devices — substantive module README plus Network Topologies.
6. Nmap — introduction, discovery, scanning, service detection, results.
7. Wireshark — introduction, capture, filters, streams, analysis, captures.
8. Final Challenges — Operation Lantern, Quiet Resolver, The Man in the Middle.

README links determine lesson order; unlisted lessons follow in filename order.
Numeric module prefixes determine order, with the course README taking precedence.
Titles and difficulty come from source. Missing titles fall back to filenames;
missing optional difficulty is omitted. Content is indexed on startup; restart after edits.

~~~text
/network
/network/course
/network/networking-fundamentals/osi-model
/network/network-devices
/network/nmap/host-discovery
/network/wireshark/protocol-analysis
/network/final-challenges/challenge-01
/network/search?q=DNS
~~~

Relative Markdown links become course URLs. Heading IDs support anchors.
Code/output whitespace is preserved. Network Devices' README includes its exercises
and challenge, and is part of the 34-page progress path.

## Installation

Windows PowerShell:

~~~powershell
cd D:\Yaoguai-Network
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
~~~

Activation is optional: `.\.venv\Scripts\Activate.ps1`. If PowerShell blocks it,
use the explicit Python path above. No execution-policy changes are needed.

## Running Locally

~~~powershell
.\.venv\Scripts\python main.py
~~~

Open http://127.0.0.1:5000/network. Stop with Ctrl+C. The runner binds to loopback
with debug disabled. Flask's development server is for local use; Vercel runs WSGI.

## Environment Variables

No secrets or configuration are required. `PORT` defaults to `5000` and changes
only the local runner. Set it with `$env:PORT = "5078"` before starting.
The app does not automatically load `.env` files; `.env.example` documents the optional port.
No database, Nmap or Wireshark installation is needed for provided-data challenges.

## Adding a Lesson

1. Add UTF-8 Markdown inside an existing module, e.g. `new-topic.md`.
2. Start with `# Lesson Title` and optionally `> Difficulty: Beginner`.
3. Link it from the module README in learning order.
4. Use relative Markdown links and fenced code labelled `bash`, `cmd` or `text`.
5. Restart and run tests.

For a new module, add a directory such as `09-new-topic`, its README and lessons.
Link it from the course README. No route/sidebar/card/search registration is required.

`tests/content-sha256.json` records original source hashes. For intentional educational
changes, review the diff and update affected entries. Coverage tests also require
every course Markdown file to be indexed.

## Adding a Challenge

Follow the source pattern: scenario, objective, provided data, task, flag format,
progressive hints and a worked solution.

~~~html
<details>
<summary>Show Hints</summary>

- Hint 1: A first hint.
- Hint 2: A more specific hint.

</details>

<details>
<summary>Show Solution</summary>

The worked explanation and its actual flag go here.

</details>
~~~

An inline code span such as `FLAG{the_actual_answer}`, explicitly introduced by
`Flag:` inside a solution, creates a submission form. Template flags outside
solutions are not answer keys. Never invent answers for missing data.

Closed-exercise keys in `network_yaoguai/exercises.py` use page URL and the ordinal
of `Check Your Answer`. Preserve explanations in Markdown. Flags and command options
are case-sensitive; ordinary answers tolerate case and whitespace. Finite source
choices can use `CHOICES` radio inputs. Open reasoning and learner-specific captures
use self-assessed practice.

## Progress and Privacy

`localStorage` key `yaoguai:network:progress:v1` holds completion, practiced/solved IDs
and last page, without submitted answers. Its independent module can be replaced
by a persistence adapter. Clearing site data resets progress. Blocked storage keeps
the current page usable but may lose progress on navigation. Completion is self-reported,
not a verified credential. The checking API does not retain submissions. Hosting
infrastructure may retain normal access logs.

## Testing

~~~powershell
.\.venv\Scripts\python -m compileall -q main.py network_yaoguai tests
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py"
~~~

Real Chromium flow and every page at 375, 768 and 1280 px:

~~~powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PLAYWRIGHT_BROWSERS_PATH = ".test-runtime/browsers"
.\.venv\Scripts\python -m playwright install chromium
.\.venv\Scripts\python -m unittest discover -s tests -p "browser_smoke.py"
~~~

The suite manages its server and checks exercises, flags, hints, hidden solutions,
progress after reload, resume, search, navigation, radio choices, clipboard, blocked
storage, console errors and overflow. Screenshots go to ignored `.test-runtime/screenshots`.
Set `BASE_URL` for an accessible deployment; protected previews require authenticated
access or a deliberately configured bypass. CI runs both suites without deployment credentials.

## GitHub Workflow

Intended origin: https://github.com/Youssef-mohamed-sayed/yaoguai-network.git

Inspect `git status`, `git remote -v`, `git branch` and `git fetch origin` before integration.
Review, stage and commit intended changes, then push to the correct branch.
Never force-push or modify Crypto. Secrets, environments, caches, test browsers,
screenshots and IDE files are ignored.

## Vercel Deployment

Official references:

- https://vercel.com/docs/frameworks/backend/flask
- https://vercel.com/docs/project-configuration/vercel-json

Native Flask detection is configured, without legacy builds or catch-all rewrites.
Root `main.py` exports `app = create_app()`. Python 3.13 is selected; requirements
declare dependencies. Templates and Markdown are explicitly included in the function.

Assets live under `public/assets` at `/assets/...`. Vercel serves them via its CDN;
local Flask provides matching read-only routes. No frontend output directory,
custom build command or `app.static_folder` is required.

### GitHub integration

1. Import the GitHub repository into the intended Vercel team.
2. Use project name `yaoguai-network`, repository root as Root Directory and Flask framework.
3. Keep Build Command and Output Directory at defaults. No secrets are required.
4. Deploy; inspect logs and verify dashboard, nested lesson, search, flag submission and assets.
5. Use `main` for production and previews for branches; require CI checks before merging.

### CLI

With CLI 48.2.10 or newer, deliberately link the correct project/team first:

~~~powershell
cd D:\Yaoguai-Network
vercel login
vercel link
vercel project inspect --non-interactive
vercel build
vercel deploy
~~~

Verify the reported target before deployment commands. Review previews before
production release. Local tests/schema validation do not constitute a cloud build
or successful deployment; those require a linked Vercel project.

## Development

Submissions never execute code or commands. Bounded JSON is compared with registered
answer keys. HTML is sanitized before presentation transforms; scripts, event handlers
and dangerous URL schemes are rejected. Template autoescaping, same-origin CSP,
constrained routes, bounded search, read-only course loading and generic errors protect
the interface. No authentication/database setup is required.

## Future Improvements

- Optional authenticated progress through a persistence adapter.
- Additional source-authored closed-question keys and validated variants.
- Packet capture downloads if authors provide source assets.
- Search highlighting and optional offline reading.

## Licensing and Attribution

Yaoguai visual primitives, fonts and artwork were reused from Crypto as requested.
Font OFL licenses are in `public/assets/fonts`. No application/content license has
been selected; no third-party ownership or open-source license is implied.
Choose a project license deliberately before authorizing reuse.
