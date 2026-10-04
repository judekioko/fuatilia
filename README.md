# Fuatilia

**Your case. Your evidence. Your next move.**

Fuatilia ("follow up" in Swahili) turns a problem with a company, landlord or public office into an organised case,
and keeps the person moving until there is an outcome. Most complaint systems in Kenya technically exist; what is
missing is persistence. The individual has to become the case manager. Fuatilia is that case manager.

It sits *above* existing channels (provider customer care, the Communications Authority, CBK, the Small Claims
Court, the Ombudsman). It does not replace them, and it never acts for the user.

## What it does

- **Cases:** by category (telecom, mobile money, rent deposit, bank, insurance, employer, education, government,
  merchant, travel, other), with a sequential reference such as `FT-2026-00042`.
- **Playbooks:** the escalation route for each category, step by step, with the waiting time before each next step,
  the channels to use and the letter to send (`cases/playbooks/`). Written as plain data so a lawyer can review them
  without reading app code.
  - **Mobile money:** reversal, then a written complaint within 15 days, then 30 days for the provider, then an appeal
    to CBK. Shows a time-limit warning.
  - **Telecom:** provider complaint, then 21 days to resolve, then the Communications Authority.
  - **Rent deposit:** written request, then a final demand, then the Small Claims Court (up to KES 1M).
  - **General:** for everything else.
- **Evidence vault:** uploads (checked by file signature, never by extension alone) and pasted messages. Pasted
  M-Pesa messages are read for the transaction code, amount, date and counterparty. Files are encrypted at rest.
- **Timeline:** every call, reply, letter and silence, dated.
- **Letters:** drafted from the case facts for the user to review, edit and send themselves (copy, open in email,
  print/PDF), then recorded on the timeline.
- **Evidence bundle:** a printable summary, chronology and numbered exhibits, plus a ZIP with the original files, ready
  for a regulator, ombudsman or court.
- **Reminders:** a dashboard of what is due, plus a daily email digest (`send_reminders`).
- **Privacy controls:** consent recorded at sign-up, download-my-data ZIP, full account deletion, and automatic
  deletion of cases closed more than 24 months ago (`purge_closed_cases`).

## Legal framing (important)

This follows the research in `docs/research/`:

- **The user is the author and sender of every letter.** Letters say they are prepared by the user, and Fuatilia
  never sends anything on anyone's behalf.
- **No fees for letters.** Advocates Act s.34 bars unqualified people from drawing documents relating to legal
  proceedings for a fee. Fuatilia doesn't draft court forms (the user files the Judiciary's own SCC 1 form) and doesn't
  use "lawyer", "wakili" or "legal aid" in branding.
- **Health data is excluded for now.** Health cover / SHA claims are left out of version 1 because health data falls
  under the strictest rules (Data Protection Act s.46).

## Before public launch

1. **Advocate review** of every playbook and letter template (each playbook shows a `reviewed_on` note).
2. **Register with the ODPC** as a data controller/processor (KES 4,000) and complete a data protection impact
   assessment (mandatory for sensitive data).
3. **Production secrets:** set `SECRET_KEY` and `FILE_ENCRYPTION_KEY`, and back up `FILE_ENCRYPTION_KEY` separately.
   Losing it makes every uploaded file unreadable.
4. **Hosting:** Postgres plus persistent private storage for `MEDIA_ROOT`. Hosting outside Kenya needs explicit
   consent wording and a notice to the ODPC.
5. **Email:** configure SMTP (password resets, reminders) and schedule the two daily jobs:

   ```bash
   python manage.py send_reminders --base-url https://your-domain
   python manage.py purge_closed_cases
   ```

## Running locally

Requires Python 3.12+.

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Windows; use .venv/bin/pip on macOS/Linux
cp .env.example .env                                # then set SECRET_KEY and FILE_ENCRYPTION_KEY
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py createcachetable
.venv/Scripts/python manage.py runserver
```

Generate a file encryption key:

```bash
.venv/Scripts/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Tests:

```bash
.venv/Scripts/python manage.py test
```

Local test account used during development: `tester@example.com` / `Fuatilia-Test-2026` (local database only).

## Deploying

- **Docker:** `Dockerfile` (gunicorn; runs migrations on start; uploads in `/data/media`, which must be a
  persistent volume).
- **Heroku-style platforms:** `Procfile`.
- **Required environment variables:**
  - `SECRET_KEY`, `FILE_ENCRYPTION_KEY`
  - `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
  - `DATABASE_URL`, `MEDIA_ROOT`
  - `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`

## Stack

Python and Django 6.1: server-rendered templates, no JavaScript build step, and a strict Content Security Policy
(no inline scripts or styles). Postgres in production (SQLite locally). Files are encrypted with `cryptography`
(Fernet), static files are served by WhiteNoise, and the app runs on gunicorn.

## Project layout

- `accounts/`: email sign-in, sign-in lockout, consent, data export and deletion
- `cases/models.py`: Case, Evidence, TimelineEvent, CaseStep, Letter
- `cases/playbooks/`: escalation routes per category
- `cases/services.py`: workflow (open case, complete steps, deadlines, close)
- `cases/parsers.py`: M-Pesa message reader
- `cases/uploads.py`, `cases/storage.py`: upload validation and encryption at rest
- `cases/letters.py`, `templates/letters/`: letter templates
- `cases/exports.py`: evidence bundle ZIP and data-access export
- `docs/research/`: the market, legal and procedural research behind the playbooks
