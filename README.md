# Weightborne

[![CI](https://github.com/PlanckPrecision/health-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/PlanckPrecision/health-tracker-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-3.1-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

I've been logging my weight daily for years and couldn't find a tool that balanced simplicity with meaningful analytics, so I built one myself. Weightborne is a full-stack Flask web app with a pace-based forecasting engine, a multi-user auth system, and a Chart.js dashboard that projects your goal date in real time from a rolling weekly average. Fully containerised with Docker and backed by PostgreSQL.

![Dashboard screenshot](app/static/images/landingpage.png)

---

## Features

- **Daily weight logging** — date picker, input validation (range, decimal precision, duplicate guard)
- **Dashboard analytics** — starting weight, 7-day rolling average, weekly pace, 30-day loss, all-time loss
- **Pace-based forecasting** — computes weeks and exact goal date from both your current pace and your committed target pace, shown side by side so you can see if you're ahead or behind
- **Interactive chart** — toggle a forecast or target-pace overlay to visualise your projected goal date on the chart
- **Goal tracking** — set a target weight and weekly loss rate; progress bar and ETA update automatically on every log
- **Auth system** — signup, login, forgot/reset password via email token (30 min expiry), change username/password, reset journey (requires password confirmation + typing "RESET")
- **Rate limiting** — Flask-Limiter backed by Redis, applied to auth endpoints to prevent brute force
- **CSRF protection** — Flask-WTF CSRF tokens on all forms
- **Session security** — `SameSite=Strict`, `HttpOnly` cookies, Werkzeug password hashing

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.1, SQLAlchemy |
| Auth | Flask-Login, Werkzeug, itsdangerous (signed tokens) |
| Database | PostgreSQL 16 (Docker) via Flask-Migrate / Alembic |
| Rate limiting | Flask-Limiter + Redis |
| Frontend | Jinja2, Tailwind CSS (CDN), Chart.js v4 |
| Infrastructure | Docker, Docker Compose, pgAdmin 4 |
| Testing | Pytest, GitHub Actions CI |

---

## Quickstart (Docker)

Requirements: [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker + Docker Compose.

```bash
git clone https://github.com/PlanckPrecision/health-tracker-api.git
cd health-tracker-api
cp .env.example .env        # fill in SECRET_KEY and mail settings
docker compose up -d
docker compose exec web flask db upgrade
```

| Service | URL |
|---|---|
| App | http://localhost:5000 |
| pgAdmin | http://localhost:5050 |

pgAdmin credentials: `admin@admin.com` / `admin`
Database connection: host `db`, user `myuser`, password `mypassword`, db `healthtracker`

---

## Project Structure

```
health-tracker-api/
├── app/
│   ├── __init__.py         # app factory, extensions (db, limiter, mail, csrf)
│   ├── models.py           # User, Entry, Goal — SQLAlchemy ORM models
│   ├── validate.py         # input validation + all stat/forecast calculations
│   ├── routes/
│   │   ├── auth.py         # signup, login, logout, password reset flow
│   │   └── entries.py      # dashboard, weight logging, goal management
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # Chart.js logic, datepicker, images
├── migrations/             # Alembic migration scripts
├── tests/
├── docker-compose.yml
├── Dockerfile
├── main.py
└── pyproject.toml
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```
SECRET_KEY=your-secret-key-here

# Optional: email for password reset flow
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=you@example.com
MAIL_PASSWORD=yourpassword
MAIL_DEFAULT_SENDER=you@example.com
```

---

## Screenshots

| Dashboard (forecast active) | History |
|---|---|
| ![Dashboard](app/static/images/landingpage.png) | ![History](app/static/images/history_page.png) |

---

## Roadmap

- [x] Pytest suite for auth and validation
- [x] GitHub Actions CI (lint + test on push)
- [x] PostgreSQL + Docker containerisation
- [x] Rate limiting with Redis
- [x] Password reset via email token
- [ ] Export entries as CSV


