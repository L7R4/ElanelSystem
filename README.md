# ElanelSystem

An internal business management platform built for **Elanel Servicios SRL** to support day-to-day operations such as sales tracking, commissions, staff management, payroll/liquidations, and financial workflows.

## Key Features

- Sales tracking and operational workflows used in daily routines
- Commission calculation and control tools
- Staff / user management for internal operations
- Payroll & liquidation workflows
- Financial management utilities and reporting support
- Admin-focused UI with practical forms and validations
- Dockerized setup for reproducible local and production-like environments

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Infrastructure:** Docker, Docker Compose, Caddy (reverse proxy)
- **Database:** PostgreSQL (via Docker Compose)

---

## Run locally with Docker (copy/paste)

> This project is designed to boot the full local environment with a single command.
> The startup flow applies migrations and runs the initial seed automatically.

```bash
# 1) Create your local environment file (only if it doesn't exist yet)
cp .env.example .env

# 2) Build and start the stack (web + db)
docker compose up --build
```

### Open the app

- App: http://localhost:8000/
- Admin: http://localhost:8000/admin/

### Initial login user (created by seed)

Credentials are controlled via your `.env` file (see `.env.example`).
If you didn't change them, use the default values defined there.

---

## Optional: useful Makefile commands

If you have `make` installed:

```bash
make up       # build + up
```

---
