# Implementation Plan: User Registration

## Context

This plan implements Step 2 of the Spendly roadmap: user registration functionality. The feature allows new users to create accounts by submitting a registration form with name, email, and password. The implementation validates inputs, hashes passwords securely, stores users in the SQLite database, and automatically logs users in upon successful registration.

The database schema (users table) already exists from Step 1, so this task focuses on building the application logic, form handling, and user feedback mechanisms.

## Critical Files

- `app.py` — Main Flask application with routes
- `database/db.py` — Database functions for user management
- `templates/register.html` — Registration form template
- `static/css/style.css` — Styling for messages

## Implementation Steps

### 1. Add Database Function: `create_user()` in `database/db.py`

**Location:** After the `seed_db()` function

**Function signature:** `create_user(name, email, password)` → returns `user_id` (int) or `None`

**Implementation:**
- Hash password using `generate_password_hash(password)` (already imported from werkzeug.security)
- Connect to database via `get_db()`
- Execute parameterized INSERT: `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)`
- Catch `sqlite3.IntegrityError` for duplicate email → return `None`
- On success → return `cursor.lastrowid` (the new user's ID)
- Always close connection properly

**Error handling:**
```python
try:
    cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
                   (name, email, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id
except sqlite3.IntegrityError:
    conn.close()
    return None  # Email already exists
```

### 2. Update `app.py` — Configure Flask and Modify `/register` Route

**Add to top of file (after imports):**
- Import: `request`, `redirect`, `url_for`, `session`, `flash` from Flask
- Import: `create_user` from `database.db`
- Set secret key: `app.secret_key = 'dev-secret-key-change-in-production'` (after `app = Flask(__name__)`)

**Modify `/register` route:**

Current route only handles GET. Update to handle both GET and POST:

```python
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        # Server-side validation
        if not name:
            flash("Please enter your name", "error")
            return render_template("register.html")
        
        if not email or "@" not in email:
            flash("Please enter a valid email address", "error")
            return render_template("register.html")
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return render_template("register.html")
        
        # Attempt to create user
        user_id = create_user(name, email, password)
        
        if user_id is None:
            flash("This email is already registered", "error")
            return render_template("register.html")
        
        # Success: log user in and redirect
        session["user_id"] = user_id
        session["user_name"] = name
        flash(f"Welcome to Spendly, {name}!", "success")
        return redirect(url_for("profile"))  # profile is placeholder
    
    # GET request: show form
    return render_template("register.html")
```

### 3. Update `templates/register.html` — Add Flash Message Display

**Replace lines 16-18:**

Current code:
```jinja2
{% if error %}
<div class="auth-error">{{ error }}</div>
{% endif %}
```

New code:
```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="auth-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

This loops through all flashed messages and displays them with appropriate CSS classes (`.auth-error` or `.auth-success`).

### 4. Add Success Message Styling in `static/css/style.css`

**Location:** After `.auth-error` block (after line 472)

**Add:**
```css
.auth-success {
    background: var(--accent-light);
    color: var(--accent);
    border: 1px solid #c8ddd0;
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    margin-bottom: 1.25rem;
}
```

This mirrors the `.auth-error` styling but uses the accent color (green) for success messages.

## Validation Rules

**Server-side validation (all required):**
1. Name: must not be empty after trimming
2. Email: must contain "@" character (basic validation)
3. Password: minimum 8 characters
4. Email uniqueness: handled by database IntegrityError

**Client-side validation:**
- Already exists via HTML5 `required` attributes on form inputs
- Server-side validation is authoritative

## User Flow

**Successful registration:**
1. User submits form → POST to `/register`
2. Validation passes → `create_user()` returns user_id
3. Session established: `session["user_id"]` and `session["user_name"]`
4. Flash success message: "Welcome to Spendly, [Name]!"
5. Redirect to `/profile` (placeholder page)

**Failed registration (duplicate email):**
1. User submits form → POST to `/register`
2. Validation passes → `create_user()` returns `None`
3. Flash error: "This email is already registered"
4. Re-render registration form

**Failed registration (validation error):**
1. User submits form → POST to `/register`
2. Validation fails → Flash appropriate error
3. Re-render registration form

## Verification Steps

After implementation, verify with these tests:

1. **Happy path:**
   - Navigate to `http://localhost:5001/register`
   - Fill in name: "Test User", email: "test@example.com", password: "testpass123"
   - Submit form
   - Should redirect to `/profile` with success message
   - Verify database: `sqlite3 spendly.db "SELECT * FROM users WHERE email='test@example.com';"` → should show hashed password

2. **Duplicate email:**
   - Try registering with "test@example.com" again
   - Should show error: "This email is already registered"
   - Should stay on registration page

3. **Weak password:**
   - Try password: "short1"
   - Should show error: "Password must be at least 8 characters long"

4. **Missing fields:**
   - Submit with empty name → should show error
   - Submit with invalid email → should show error

5. **Session verification:**
   - After successful registration, check Flask session is established
   - Can verify by adding debug print: `print(session)` in profile route

6. **Security check:**
   - Open `spendly.db` and query users table
   - Verify password_hash is a hash, not plain text
   - Should start with `scrypt:` or `pbkdf2:` depending on werkzeug version

## Implementation Complete ✓

All components successfully implemented and tested:

- ✅ `create_user()` function with password hashing
- ✅ Flask session configuration and secret key
- ✅ POST handler with comprehensive validation
- ✅ Flash message system with error/success categories
- ✅ CSS styling for success messages
- ✅ All test scenarios verified (successful registration, duplicate email, weak password, empty fields)
- ✅ Password security confirmed (scrypt hashing)
