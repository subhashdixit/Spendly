# Spec: Registration

## Overview

Implement user registration functionality to allow new users to create accounts. This feature converts the existing `/register` placeholder route into a fully functional registration system that validates input, hashes passwords, stores users in the database, and establishes authenticated sessions. This is the first step toward building a secure, multi-user expense tracking application.

## Depends on

**Step 1 — Database Setup**: Requires the `users` table and `get_db()` function to store and retrieve user data.

## Routes

- `POST /register` — Process registration form submission — public access

The existing `GET /register` route already renders the registration template and requires no changes.

## Database changes

**No database schema changes** — the `users` table already has all required columns:
- `id`, `name`, `email`, `password_hash`, `created_at`

**New function in `database/db.py`:**
- `create_user(name, email, password)` — Inserts new user with hashed password, returns user ID on success or None if email already exists

## Templates

**Modify:**
- `templates/register.html` — Update error display to use Flask flash messages instead of the `{% if error %}` block

**No new templates needed** — registration template already exists with proper form structure.

## Files to change

1. **`app.py`**
   - Add Flask secret key for session management
   - Import: `request`, `redirect`, `url_for`, `session`, `flash`
   - Update `/register` route to handle both GET and POST
   - Add form validation logic
   - Create user session on successful registration
   - Redirect to expenses dashboard (or profile page as placeholder)

2. **`database/db.py`**
   - Add `create_user(name, email, password)` function
   - Import `check_password_hash` (for future login functionality)

3. **`templates/register.html`**
   - Replace `{% if error %}` block with Flask's `get_flashed_messages()` pattern
   - Maintain existing form structure

## Files to create

**No new files** — all necessary files already exist.

## New dependencies

**No new dependencies** — use existing packages:
- `werkzeug.security.generate_password_hash` (already imported)
- Flask's built-in `session` and `flash` mechanisms

## Rules for implementation

### Security
- **NEVER** store plain-text passwords — always hash with `generate_password_hash()` before storing
- Use parameterized queries only — no string interpolation in SQL
- Set Flask `secret_key` using a strong random value (can be hardcoded for development)
- Validate all form inputs on server-side (never trust client validation alone)

### Code style
- Use CSS variables for colors — never hardcode hex values
- All templates must extend `base.html`
- Use `url_for()` for all internal links
- Flash messages should use Bootstrap-style categories: 'error', 'success', 'info'

### Database
- Handle `sqlite3.IntegrityError` when email already exists — catch and return friendly error
- Close database connections properly (use context managers or explicit close)
- Return meaningful values from `create_user()`: user ID on success, None on duplicate email

### User experience
- Clear, actionable error messages: "This email is already registered", not "Database error"
- On successful registration, automatically log user in (set session) — no need to redirect to login
- Preserve form values on validation errors (except password for security)

## Definition of done

### Functional requirements
- [ ] User can submit registration form with name, email, and password
- [ ] Password must be at least 8 characters (validated server-side)
- [ ] Email format must be valid (validated server-side)
- [ ] Duplicate email registration shows error: "This email is already registered"
- [ ] Empty or invalid fields show appropriate error messages
- [ ] Successful registration:
  - Creates user record in database with hashed password
  - Automatically logs user in (session established)
  - Redirects to dashboard/profile page
  - Shows success message: "Welcome to Spendly, [Name]!"

### Technical requirements
- [ ] Password is hashed before storage (verify in database)
- [ ] No plain-text passwords anywhere in code or database
- [ ] All SQL queries use parameterized format
- [ ] Session is properly established with user ID
- [ ] Flask secret key is configured
- [ ] Error handling prevents crashes on edge cases

### Testing checklist
1. Visit `/register` — form displays correctly
2. Submit empty form — shows validation errors
3. Submit with weak password (< 8 chars) — shows error
4. Submit with invalid email format — shows error
5. Register new user successfully — redirects and shows welcome message
6. Try to register same email again — shows duplicate error
7. Check database — password is hashed (not plain text)
8. After registration, verify session exists (user is logged in)
