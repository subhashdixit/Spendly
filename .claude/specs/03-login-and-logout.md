# Spec: Login and Logout

## Overview

Implement user authentication by converting the `/login` placeholder into a fully functional login system and implementing the `/logout` route. This feature allows registered users to authenticate with their credentials, establish secure sessions, and safely terminate those sessions. Combined with Step 2 (Registration), this completes the core authentication system for Spendly.

## Depends on

**Step 1 — Database Setup**: Requires the `users` table and `get_db()` function.

**Step 2 — Registration**: Requires the `create_user()` function and password hashing patterns established in registration.

## Routes

- `POST /login` — Process login form submission — public access
- `GET /logout` — Clear user session and redirect to landing page — logged-in users only

The existing `GET /login` route already renders the login template and requires no changes.

## Database changes

**No database schema changes** — the `users` table already contains all necessary columns.

**New function in `database/db.py`:**
- `authenticate_user(email, password)` — Validates email/password combination, returns user dict (id, name, email) on success or None on failure

## Templates

**Modify:**
- `templates/login.html` — Update to use Flask flash messages for error display (consistent with registration pattern)
- `templates/base.html` — Update navbar to show user name and "Sign out" link when logged in, or "Sign in" and "Get started" when logged out

**No new templates needed** — login template already exists.

## Files to change

1. **`app.py`**
   - Import `check_password_hash` from `werkzeug.security`
   - Update `/login` route to handle both GET and POST requests
   - Add form validation and authentication logic
   - Create user session on successful login
   - Implement `/logout` route to clear session and redirect
   - Add session checks to `/register` and `/login` (redirect logged-in users to profile)

2. **`database/db.py`**
   - Add `authenticate_user(email, password)` function
   - Import `check_password_hash` from `werkzeug.security`

3. **`templates/login.html`**
   - Add Flask flash message display (consistent with register.html pattern)
   - Maintain existing form structure

4. **`templates/base.html`**
   - Update navbar to conditionally show:
     - If logged in: "Welcome, [Name]" and "Sign out" link
     - If logged out: "Sign in" and "Get started" links
   - Use `session.get('user_name')` to check authentication state

## Files to create

**No new files** — all necessary files already exist.

## New dependencies

**No new dependencies** — use existing packages:
- `werkzeug.security.check_password_hash` (companion to `generate_password_hash`)
- Flask's built-in `session` mechanism (already in use)

## Rules for implementation

### Security
- **NEVER** return specific error messages that reveal whether an email exists — always use generic "Invalid email or password"
- Use `check_password_hash()` to verify passwords — never compare plain text
- Clear ALL session data on logout using `session.clear()`
- Validate all form inputs on server-side
- Use parameterized queries only — no string interpolation in SQL

### Code style
- Use CSS variables for colors — never hardcode hex values
- All templates must extend `base.html`
- Use `url_for()` for all internal links
- Flash messages should use categories: 'error', 'success', 'info'
- Keep authentication logic in database layer, not in routes

### Database
- `authenticate_user()` should return None for both "email not found" and "wrong password" (don't leak user existence)
- Return user data as dict: `{'id': user_id, 'name': user_name, 'email': user_email}`
- Close database connections properly

### User experience
- Generic error message on failed login: "Invalid email or password"
- On successful login, redirect to profile page with welcome message
- On logout, redirect to landing page with confirmation message: "You have been logged out"
- Logged-in users visiting `/login` or `/register` should be redirected to profile (no access)
- Empty form fields should show validation errors: "Please enter your email" / "Please enter your password"

### Session management
- Store minimal data in session: `user_id` and `user_name`
- Never store sensitive data (password hash, email) in session
- Session keys to use:
  - `session['user_id']` — integer user ID
  - `session['user_name']` — string user name for display

## Definition of done

### Functional requirements — Login
- [ ] User can submit login form with email and password
- [ ] Empty email or password shows appropriate validation error
- [ ] Invalid credentials show generic error: "Invalid email or password"
- [ ] Valid credentials:
  - Establish user session with `user_id` and `user_name`
  - Redirect to profile page
  - Show success message: "Welcome back, [Name]!"
- [ ] Logged-in users trying to access `/login` are redirected to profile
- [ ] Demo user (demo@spendly.com / demo123) can log in successfully

### Functional requirements — Logout
- [ ] Logged-in user clicking "Sign out" link triggers `/logout` route
- [ ] Logout clears session completely
- [ ] Logout redirects to landing page
- [ ] Logout shows confirmation message: "You have been logged out"
- [ ] After logout, user cannot access protected pages without logging in again

### Functional requirements — Navbar
- [ ] Navbar shows "Sign in" and "Get started" when logged out
- [ ] Navbar shows "Welcome, [Name]" and "Sign out" when logged in
- [ ] Navbar updates correctly after login/logout without manual refresh

### Technical requirements
- [ ] `authenticate_user()` function implemented in database/db.py
- [ ] Password verification uses `check_password_hash()`
- [ ] All SQL queries use parameterized format
- [ ] Session cleared properly on logout (no residual data)
- [ ] Error messages don't leak user existence
- [ ] `/register` redirects logged-in users (prevents duplicate accounts)

### Testing checklist
1. Visit `/login` when logged out — form displays correctly
2. Submit empty form — shows validation errors
3. Submit with non-existent email — shows "Invalid email or password"
4. Submit with wrong password — shows "Invalid email or password"
5. Login with demo@spendly.com / demo123 — redirects to profile with welcome message
6. Check session contains `user_id` and `user_name`
7. Visit `/login` when already logged in — redirects to profile
8. Visit `/register` when already logged in — redirects to profile
9. Click "Sign out" — redirects to landing page with confirmation
10. After logout, verify session is empty (cannot access profile without login)
11. Navbar updates correctly based on login state
