# Yaoguai-Crypto

**YAOGUAI 妖怪 — Cryptography Training Ground.** A beginner-to-CTF cryptography course with hands-on tasks and a challenge in every lesson, plus a Flask API for encoding, encryption and hashing.

## Run it locally

```bash
cd scripts
pip install -r requirements.txt
python app.py
```

This serves the website and the API together and opens http://127.0.0.1:5000/.

## Deploy to Vercel

1. Import this GitHub repository as a Vercel project.
2. Add **Neon** from Vercel's Integrations Marketplace and connect the database to
   this project for Production. Use a separate Neon branch/database for Preview.
3. Confirm `DATABASE_URL` (or `POSTGRES_URL`) exists for the selected environment.
   Use Neon's pooled URL with its SSL parameters intact. Custom prefixes require
   mapping the prefixed value to `DATABASE_URL`.
4. Set `YAOGUAI_JWT_SECRET` to a private random secret, or let the application
   generate a signing key stored in the shared database. Never commit credentials.
5. If preserving existing accounts, run the import below **before the new app
   handles account requests**. The target must be empty.
6. Redeploy after connecting the database or changing environment variables.

`vercel.json` sends requests to `api/index.py`; Flask serves both the pages and
API. Accounts, progress, revocable sessions, signing settings, and uploaded avatars
use PostgreSQL when a connection URL is configured. Tables are initialized
transactionally on first database use. Avatars are stored in the database with
the existing 2 MB limit. No additional file-storage service is required.

Local runs without a connection URL use SQLite. Hosted authentication returns a
clear storage-unavailable error if Neon is missing or unreachable, rather than
creating accounts in temporary files. PostgreSQL connection failures never fall
back to SQLite. Keep Preview separate from Production to avoid shared test data.

### Import existing SQLite accounts

Back up the source SQLite database and its avatar directory. Preserve account IDs
and password hashes; passwords do not need resetting. Set `DATABASE_URL` securely
in the shell running these commands (the application does not automatically load
`.env` files). Start with a validation-only run:

```bash
python scripts/migrate_sqlite.py --source backup/yaoguai.db --avatars backup/avatars
```

Then import into an **empty** Neon database:

```bash
python scripts/migrate_sqlite.py --source backup/yaoguai.db --avatars backup/avatars --apply
```

The importer uses one transaction and refuses to overwrite existing account data.
It prefers `DATABASE_URL_UNPOOLED` for the import when that direct URL is available;
normal application requests continue using pooled `DATABASE_URL`.
It preserves users, progress, stored signing settings, unexpired sessions, and
avatars. It stops on missing avatars; `--skip-missing-avatars` explicitly resets
those unavailable images to the default. A different `YAOGUAI_JWT_SECRET` requires
users to sign in again. Data already lost from an old serverless instance's
SQLite files cannot be recovered by this import.

### Verify

```bash
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/auth-ui.test.cjs tests/session-isolation.test.cjs
```

To also run PostgreSQL integration tests, set `TEST_POSTGRES_URL` to a dedicated,
expendable test database. **These tests truncate the application tables in that
database. Never point this variable at Production or a database containing data.**
Tests cover migration, username uniqueness, per-account progress and avatars,
revoked tokens, and account-switch/logout isolation.

### Agent tooling

The Neon plugin supplies the Neon agent skills. The project also registers an
OAuth-only Neon MCP server in `.codex/config.toml`, scoped to Neon project
`odd-recipe-08068016`. Codex prompts for MCP sign-in on first use; CLI sign-in and
MCP OAuth are separate. No API key is stored in the project configuration.

Local Vercel linkage lives in ignored `.vercel/`, and local Neon linkage in ignored
`.neon`. Environment pulls must use git-ignored `.env.*` files. Preserve existing
environment values when linking Neon by using `--no-env-pull`.

## Project structure

```text
Yaoguai-Crypto/
├── api/index.py        Vercel entry point
├── public/             the website: index.html, assets/, js/, lessons/
├── scripts/            Flask API (app.py) and crypto implementations
├── requirements.txt
└── vercel.json
```

## Lessons

Fully written: Hexadecimal, Base64, XOR, AES, MD5, bcrypt. The remaining modules open a placeholder page and are listed in `public/js/registry.js`.
