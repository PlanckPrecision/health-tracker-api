# Weightborne

I built this web application because I track my weight daily and couldn't find a tool that was both simple and actually informative. Whether you're losing, gaining, or maintaining weight, having a clear goal and watching your progress toward it matters. Thus I built Weightborne: a minimalist Flask app with real analytics, pace-based forecasting, and a dark UI.

![Dashboard screenshot](app/static/images/landingpage.png)

---

## Features

- **Daily logging** — enter weight by date with validation (range, decimal precision, duplicate guard)
- **Dashboard analytics** — Starting weight, 7-day pace, 30-day loss, all-time loss, and dynamic forecast to goal date
- **Interactive chart** — toggle a forecast overlay projected from your current weekly pace to visualise on what date the goal weight will be achieved, based on current metrics and trends
- **Goal tracking** — set a target weight; progress bar and estimated time of arrival for goal date update automatically
- **Auth** — signup, login, change username/password, reset journey (requires password + typed "RESET")
- **Session security** — `SameSite=Strict`, `HttpOnly` cookies, Werkzeug password hashing

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask, SQLAlchemy |
| Auth | Flask-Login, Werkzeug |
| Database | SQLite (dev) via Flask-Migrate |
| Frontend | Jinja2, Tailwind CSS (CDN), Chart.js v4 |

---

## Quickstart

```bash
git clone https://github.com/your-username/health-tracker-api.git
cd health-tracker-api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # add a SECRET_KEY value
flask db upgrade
python main.py
```

Open `http://127.0.0.1:5000`.

---

## Project Structure

```
health-tracker-api/
├── app/
│   ├── __init__.py       # app factory
│   ├── models.py         # database models
│   ├── validate.py       # input validation and stat calculations
│   ├── routes/
│   │   ├── auth.py       # authentication routes
│   │   └── entries.py    # weight entry and dashboard routes
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # JS and images
├── migrations/           # Alembic migration scripts
├── tests/
├── main.py
└── pyproject.toml
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```
SECRET_KEY=your-secret-key-here
```

---

## Roadmap

- [ ] Pytest suite for auth and validation
- [ ] GitHub Actions CI (lint + test on push)
- [ ] PostgreSQL support for production deployment
- [ ] Export entries as CSV

---

## Screenshots

| Dashboard (forecast active) | History |
|---|---|
| ![Dashboard](app/static/images/landingpage.png) | ![History](app/static/images/history_page.png) |

---

## Demo


