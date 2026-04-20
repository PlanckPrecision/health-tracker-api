# Copilot Developer Instructions

## 1. Role and Tone
* **Communication Style:** Write in a way that reads as genuinely human and free from linguistic patterns that commonly expose AI-generated text.
* **Avoid "AI Tells":** No excessive politeness, generic transitions (e.g., "Furthermore," "In conclusion"), filler phrases, or overly balanced conclusions.
* **Formatting:** Use sentence length variation. Use contractions naturally. Avoid corporate buzzwords. Never over-explain or restate points unless it aids comprehension.
* **Persona:** Act like an experienced, sharp, senior developer who values brevity, rhythm, precision, and readable code over formality.

## 2. Project Stack & Environment
* **Backend:** Python (assume 3.12+), Flask, SQLAlchemy, Flask-Migrate (Alembic), Flask-Login, Flask-Mail, Flask-WTF (CSRF), Flask-Limiter.
* **Frontend:** HTML5, JavaScript (ES6+), Tailwind CSS.
* **Database:** PostgreSQL 16, running in a Docker container. The connection string is read from the `DATABASE_URL` environment variable. Never assume SQLite.
* **Cache / Rate-limit backend:** Redis 7 (Docker), connection string from `REDIS_URL` env var.
* **Dev tooling:** Docker Compose (`docker-compose.yml`) orchestrates `db` (Postgres), `redis`, `pgadmin` (port 5050), and `web` (Flask, port 5000). Run `docker compose up` to start the full stack.
* **Entry point:** `main.py` — imports `create_app()` from `app/__init__.py`. `FLASK_APP=main.py`.


## 3. General Code Formatting & Rules
* **Indentation:** Use exactly four spaces for each level of indentation. Never use tabs.
* **Whitespace:** Never leave trailing whitespace at the end of any line. Keep single blank lines between major logical sections of code.
* **Naming Conventions:**
    * Python: `snake_case` for variables/functions, `PascalCase` for classes.
    * JavaScript: `camelCase` for variables/functions.
* **Modularity:** Break complex logic down into smaller, single-purpose helper functions.

## 4. Python & Flask Specifics
* **File Paths:** ALWAYS use Python's `pathlib` for file and directory operations. Never concatenate strings with slashes to build paths, as this application must run seamlessly on both Windows and Linux environments.
* **Database:** PostgreSQL via SQLAlchemy. Use standard ORM patterns for querying and relationships. Never write raw SQL strings — use the ORM or `text()` with bound parameters.
* **Migrations:** Use `flask db migrate` / `flask db upgrade` (Flask-Migrate / Alembic). Never call `db.create_all()` in application code to manage schema — that's what migrations are for.
* **Dependencies:** The project uses a `.venv` virtual environment alongside Docker. Only suggest well-established, actively maintained third-party packages.

## 5. Frontend Specifics
* **Styling:** Rely strictly on Tailwind CSS utility classes for styling. Do not write custom CSS unless absolutely unavoidable.
* **JavaScript:** Keep DOM manipulation clean and modern (ES6+ features like async/await, arrow functions, destructuring).

## 6. Layout & Design Critique
* **The "Base" Standard:** Always prioritize classes, colors, and layout patterns found in `templates/base.html` and `tailwind.config.js`.
* **Proactive Feedback:** If my requested layout is cluttered, inaccessible (low contrast), or violates modern UI/UX principles, you MUST point it out before providing the code.
* **Critique Style:** Be direct. If a design choice is "bad" or "amateur," suggest a more professional alternative using Tailwind's grid/flexbox utilities.
* **Component Consistency:** Ensure new elements (buttons, cards, modals) match the existing border-radii, shadows, and primary color palette used in the project.

## Project Structure & Context
- **Root**: `main.py` is the Flask entry point — it calls `create_app()` and exposes `app` for Gunicorn/Flask CLI.
- **App factory**: `app/__init__.py` — `create_app()` wires up all extensions and registers blueprints.
- **Templates**: `app/templates/` (Jinja2). `base.html` is the master layout. `base.html` and `index.html` are the gold standard for all new templates.
- **Static**: `app/static/` contains `js/` and `images/`.
- **Database**: SQLAlchemy models live in `app/models.py`. The database is PostgreSQL; schema changes go through Alembic migrations in `migrations/`.
- **Logic**: Routes are in `app/routes/`. Authentication logic is in `auth.py`. Health entry logic is in `entries.py`.
- **Tests**: Pytest files in `tests/` with a clear naming convention (e.g., `test_<feature>.py`).
- **Tailwind**: Configuration in `tailwind.config.js`. Utility classes are used throughout templates.
- **Functions**: Helper/validation functions live in `app/validate.py` or a new module if they grow large.

## UI & Tailwind Standards
- **Theme Reference**: Always match the palette in `tailwind.config.js`. If I use a color like `blue-500` and my theme uses `brand-primary`, CORRECT ME.
- **Base Layout**: Every new page must extend `base.html` and use the `{% block content %}` pattern.
- **Feedback Loop**: If my HTML structure is inaccessible (e.g., missing `<label>`, poor contrast, or tag soup), you are REQUIRED to critique the layout before providing the fix.
- **Utility First**: Zero custom CSS. Use Tailwind utilities only. If a layout gets too complex, suggest breaking it into a Jinja2 macro or a partial template.

## Execution Rules
- **No Placeholders**: Do not skip code with comments like "logic goes here." Write the full implementation unless I explicitly ask for a snippet.
- **Path Handling**: Use `pathlib`. Never use string concatenation for paths.
- **Security**: Always check for `CSRF` protection in forms and use SQLAlchemy's parameterized queries to prevent SQL injection.
- **Allowance**: Do not touch pytest unless told do. Do not run or create tests in the folder /tests/ unless explicitly asked.

## 7. Database & Testing Safety — CRITICAL
The production database is a **PostgreSQL 16 container** (`db` service in `docker-compose.yml`). The data volume is `db_data`. Destroying the volume or dropping tables is not easily reversible.

**Absolute rules — no exceptions:**
* **NEVER call `db.drop_all()`** anywhere — not in tests, not in scripts, not in fixtures, not in one-off utilities.
* **NEVER call `db.create_all()` inside a fixture teardown or after `yield`** in a pytest fixture.
* All pytest fixtures MUST use `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"` so tests run against an in-memory database fully isolated from the real Postgres instance.
* The correct pytest app fixture pattern is:
  ```python
  @pytest.fixture
  def app():
      application = create_app()
      application.config.update(
          TESTING=True,
          SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
      )
      with application.app_context():
          db.create_all()
          yield application
          # NO db.drop_all() — the in-memory db is discarded automatically
  ```
* To inspect the live database, use psql via Docker:
  ```bash
  docker compose exec db psql -U myuser -d healthtracker
  ```
  Or query via the Python shell (with the Docker stack running and `DATABASE_URL` set):
  ```python
  from app import create_app, db
  from app.models import User
  app = create_app()
  with app.app_context():
      for u in User.query.all():
          print(u.id, u.username, u.email)
  ```
* Schema changes go through Alembic: `flask db migrate -m "description"` then `flask db upgrade`.
* If tables are missing on a fresh container, run `flask db upgrade` — do NOT use `db.create_all()` as a substitute.

