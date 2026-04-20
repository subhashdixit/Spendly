# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly is a Flask-based expense tracking web application. This is a teaching project with progressive implementation steps — many routes and database functions are placeholders for students to complete.

## Development Setup

**Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run the application:**
```bash
python app.py
```
The app runs on http://localhost:5001 in debug mode (auto-reloads on code changes).

**Run tests:**
```bash
pytest
pytest -v  # Verbose output
pytest path/to/test_file.py  # Run specific test file
pytest -k test_name  # Run tests matching pattern
```

## Architecture

**Core Files:**
- `app.py` — Flask application entry point with route definitions
- `database/db.py` — Database connection and initialization functions (to be implemented)
- `templates/` — Jinja2 HTML templates with base template inheritance
- `static/css/style.css` — Custom CSS with DM Sans/DM Serif Display fonts
- `static/js/main.js` — Client-side JavaScript

**Database Layer:**
The `database/db.py` module should provide:
- `get_db()` — Returns SQLite connection with `row_factory=sqlite3.Row` and foreign keys enabled
- `init_db()` — Creates tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — Inserts sample development data

**Template Structure:**
- `base.html` — Base template with navbar and footer
- All pages extend base using `{% extends "base.html" %}` and `{% block content %}`
- Navbar shows "Sign in" and "Get started" links for unauthenticated users
- Footer includes Terms and Privacy Policy links

**Routes:**
Implemented routes: `/`, `/register`, `/login`, `/terms`, `/privacy`

Placeholder routes (return string messages):
- `/logout` — Session termination
- `/profile` — User profile page
- `/expenses/add` — Add new expense
- `/expenses/<id>/edit` — Edit existing expense
- `/expenses/<id>/delete` — Delete expense

## Key Patterns

**Route Definitions:**
Routes are organized with a separator comment `# ------------------------------------------------------------------ #` to distinguish between completed and placeholder implementations.

**URL Generation:**
Always use `url_for()` in templates:
```jinja2
<a href="{{ url_for('landing') }}">Home</a>
```

**Static Files:**
Reference static assets using `url_for('static', filename='...')`:
```jinja2
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

**Running on Port 5001:**
The app explicitly runs on port 5001 to avoid conflicts with other local services.

## Implementation Notes

When implementing placeholder routes:
1. Import necessary database functions from `database.db`
2. Use Flask's `session` for authentication state
3. Return redirects (`redirect(url_for(...))`) after form submissions
4. Use flash messages for user feedback
5. Implement proper error handling and validation

When working with the database:
1. Always use context managers or ensure connections are closed
2. Enable foreign key constraints in SQLite
3. Use parameterized queries to prevent SQL injection
4. Return `sqlite3.Row` objects for dict-like access to results
