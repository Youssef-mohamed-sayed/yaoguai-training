# Yaoguai Training

Yaoguai Training brings the Network, Linux, Python Programming, and Cryptography learning platforms together at one domain. Course content remains open to guests. A shared Flask account stores signed-in progress, assignments, and administration data in PostgreSQL.

## Features

- Four preserved learning applications mounted at `/network`, `/linux`, `/programming`, and `/crypto`.
- Central registration, sign-in, password change/reset, and administrator roles.
- Markdown course discovery from each imported course tree; the Python course is built from `platforms/programming/python-essentials/`.
- Course catalog and progress APIs with stable activity IDs, lesson visits, reading-time heartbeats, validated Network exercises, and server-calculated module completion.
- Session-only guest progress in the imported course interfaces. Account progress is stored by the Flask API; it is not stored permanently in the browser.
- Admin member, level, group, assignment, deadline, and submission-review tools.
- Dark Yaoguai visual system with restrained red accents and responsive layouts.

## Technology

- Vite and vanilla JavaScript for the portal.
- Existing application stacks retained for the four learning products: Flask/Jinja for Network and Crypto; Vite/JavaScript for Linux; JavaScript/MarkdownIt for Programming.
- Flask, Flask-Login, Flask-SQLAlchemy, Flask-Migrate, Flask-WTF, Argon2id, and PostgreSQL via psycopg for shared accounts and APIs.
- Neon PostgreSQL in hosted environments; SQLite is the local default.
- Vercel static output and Python Functions for the single-domain deployment.

## Repository structure

```text
api/                         Vercel Python function entry points
backend/app/                 Central Flask app, models, APIs, and services
backend/migrations/          Alembic migrations
backend/scripts/             Catalog and initial-admin setup commands
platforms/network/           Imported Network app and network-essentials content
platforms/linux/             Imported Linux app and linux-essentials content
platforms/programming/       Imported Programming app and Python source content
platforms/crypto/            Imported Crypto app and assets
public/training-bridge.js    Shared account and progress integration
src/                         Root portal and administration UI
tests/                        Content import and Flask API tests
backend/tests/                Flask API tests and fixtures
```

The original sibling repositories and their Git histories are not modified by this monorepo. `platforms/` contains their imported application copies. Python course files under `platforms/programming/python-essentials/` were copied from the Python course in the Yaoguai Programming repository and remain the build-time source for production. The build scripts read those Markdown files directly; lessons are not duplicated in frontend components.

## Windows setup

From the repository root in PowerShell:

```powershell
py -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r backend\requirements-dev.txt
npm install
npm --prefix platforms/linux install
npm --prefix platforms/programming install
```

Copy `.env.example` to `.env.local` (or use the locally ignored `.env.local` created by Neon) and fill placeholders. Generate a local secret and set the database URL before starting Flask:

```powershell
$env:SECRET_KEY = "replace-with-a-random-secret-of-at-least-32-characters"
$env:DATABASE_URL = "sqlite:///yaoguai-training.db"
$env:COOKIE_SECURE = "false"
```

Apply migrations and register the imported courses:

```powershell
python -m flask --app backend.run db upgrade
python backend\scripts\seed_catalog.py
```

Build all applications and run the unified backend in one terminal:

```powershell
npm run build
python backend\run.py
```

In a second terminal, run the portal dev server (its proxy sends API and platform paths to Flask):

```powershell
npm run dev
```

Open `http://localhost:5173`. The production bundle is in `dist/`; `python backend\run.py` serves the portal and all four course apps at port 5000.

## Course discovery and authoring

The central catalog loader reads from these imported source trees:

- `platforms/network/network-essentials/`
- `platforms/linux/linux-essentials/`
- `platforms/programming/python-essentials/`
- Crypto module order and lesson IDs come from `platforms/crypto/public/js/registry.js`.

Python is dynamically discovered at build time. The builder reads `README.md`, then discovers numbered module directories, module READMEs, nested Markdown lessons, relative assets, headings, and supporting Markdown documents. It emits `course-manifest.json` and copies referenced assets without changing the source Markdown. New Python modules or lessons become available after `npm run build:programming` (or the full `npm run build`).

Add a Python module by adding a directory under `platforms/programming/python-essentials/`, with a `README.md` and lesson Markdown files. Add a lesson in that module directory; numeric prefixes determine order, and the lesson title comes from its first Markdown heading. Relative links and assets are resolved against the original file path. Code fences are syntax-highlighted by the Programming app and include copy controls. Exercises and expected output should be authored in the lesson Markdown; the application does not invent solutions or execute learner code.

Linux and Network discovery likewise runs from their imported course directories. Network exercises are registered from the course parser and answer checks are performed server-side before their progress is recorded.

## Accounts and progress

All account APIs live under `/api`. Authentication uses a signed, HTTP-only, same-site cookie and a shared secret across the Flask app and the Network sub-app. Passwords use Argon2id. State-changing central account API calls require a CSRF token. Password reset delivery requires SMTP settings; without mail configuration, requests return the same non-disclosing response but cannot deliver a reset link.

The catalog and activity identifiers are derived from source paths (or Crypto's existing registry), not array indexes. Activity completion is tied to a server-recorded visit; lesson completions also require the configured reading time. Network exercise completion is stored only after the existing server-side answer checker accepts the submission. Module progress is calculated as completed required activities divided by required activities. There is no manual module-completion API or control.

Guest activity in the preserved frontends is kept in `sessionStorage` for the current browser session. A signed-in learner's durable progress is kept in PostgreSQL. The current bridge records authenticated visits and lesson completion; it does not transfer temporary guest activity into an account.

## Administrator setup

Bootstrap the first admin from secure process environment variables. The script creates `YaoAdmin` idempotently and requires a password change at first sign-in; it never prints the password or stores it in source:

```powershell
$env:INITIAL_ADMIN_USERNAME = "YaoAdmin"
$env:INITIAL_ADMIN_PASSWORD = "<secure initial password>"
python backend\scripts\bootstrap_admin.py
Remove-Item Env:INITIAL_ADMIN_PASSWORD
```

Open `/admin` after signing in. The API enforces administrator roles server-side. SMTP configuration is needed for account recovery.

## Database migrations and catalog seed

Create a migration after changing SQLAlchemy models:

```powershell
python -m flask --app backend.run db migrate -m "describe the schema change"
python -m flask --app backend.run db upgrade
```

Apply migrations before deployment, then run `python backend\scripts\seed_catalog.py` once to register source-derived platform, module, lesson, and exercise IDs. The seed is idempotent and does not rewrite Markdown.

Use a pooled Neon connection string for application requests and a direct connection for schema migrations. Keep `DATABASE_URL` and `SECRET_KEY` in the deployment environment only.

## Development commands

```powershell
npm run dev
npm run build
npm run check:programming
npm run test:linux
python -m pytest backend\tests -q
$env:PYTHONPATH = "backend"; python -m pytest platforms\network\tests -q
python -m pytest platforms\crypto\tests -q
```

`npm run build` builds Linux and Programming course indexes, builds the portal, and packages each imported app under the matching `dist/` subdirectory. No learner Python code is executed by the server.

## Vercel deployment

The repository is configured for the Yaoguai Training Vercel project. Its build runs `npm run build`; Python Functions route `/api/*` and rewritten platform paths through `api/[...path].py`. Static assets are emitted under `dist/`. Configure these Vercel environment variables before deploying:

- `SECRET_KEY`: a long random value shared by the central Flask and mounted Network app.
- `DATABASE_URL`: pooled Neon PostgreSQL URL.
- Optional `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_FROM` for password reset email.
- `PUBLIC_ORIGIN=https://yaoguai-training.vercel.app`.
- `COOKIE_SECURE=true`.

Run migrations with a direct Neon URL and seed the catalog before enabling account activity. The original four Vercel projects are separate deployments and are not deleted by this repository.

## Design credit

The portal's visual refinement followed the Unslop skill's guidance on hierarchy, neutral surfaces, spacing, and purposeful accents. [Unslop by Damir Sokolovsky](https://github.com/heydamir/unslop), CC BY 4.0.
