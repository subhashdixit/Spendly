# Implementation Plan: Login and Logout

## Context

This feature completes the authentication system for Spendly by adding login and logout functionality. Currently, users can register accounts (Step 2), but cannot sign back in after leaving or explicitly log out. This implementation will:
- Enable registered users to authenticate with email/password
- Allow users to safely terminate their sessions
- Update the UI to reflect authentication state
- Prevent duplicate registrations by redirecting logged-in users

The registration pattern is already established, so we'll follow the same conventions for consistency.

## Critical Files

1. `app.py:60-62` - Login route (currently GET only)
2. `app.py:79-81` - Logout route (placeholder)
3. `app.py:22-57` - Register route (reference for pattern)
4. `database/db.py` - Add authenticate_user() function
5. `templates/login.html` - Update to use flash messages
6. `templates/base.html:15-26` - Navbar (conditional rendering)

## Implementation Steps

### 1. Add authenticate_user() to database/db.py

**Location:** After create_user() function (~line 123)

**Implementation:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

def authenticate_user(email, password):
    """
    Validates email/password combination.
    Returns {'id': int, 'name': str, 'email': str} on success, None on failure.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return {'id': user['id'], 'name': user['name'], 'email': user['email']}
    return None
```

**Key points:**
- Import `check_password_hash` from werkzeug.security
- Return None for both "email not found" and "wrong password" (security: don't leak user existence)
- Return dict with id, name, email (matches session needs)
- Use parameterized query
- Close connection properly

### 2. Update /login route in app.py

**Location:** Replace lines 60-62

**Pattern:** Follow the registration route pattern (app.py:22-57)

**Implementation:**
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    # Redirect logged-in users to profile
    if session.get("user_id"):
        return redirect(url_for("profile"))
    
    if request.method == "POST":
        # Extract form data
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        # Validate empty fields
        if not email:
            flash("Please enter your email", "error")
            return render_template("login.html")
        
        if not password:
            flash("Please enter your password", "error")
            return render_template("login.html")
        
        # Authenticate user
        user = authenticate_user(email, password)
        
        if user is None:
            flash("Invalid email or password", "error")
            return render_template("login.html")
        
        # Success: create session and redirect
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("profile"))
    
    # GET request: show form
    return render_template("login.html")
```

**Key points:**
- Add session check at the top (redirect if already logged in)
- Import authenticate_user from database.db (update imports line 2)
- Import check_password_hash from werkzeug.security (not used in route, but good practice)
- Validate empty fields first
- Use generic error message "Invalid email or password"
- Flash success message on login
- Match registration pattern exactly

### 3. Implement /logout route in app.py

**Location:** Replace lines 79-81

**Implementation:**
```python
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("landing"))
```

**Key points:**
- Use `session.clear()` not individual key deletion
- Flash confirmation message
- Redirect to landing page
- No authentication check needed (safe to call even if not logged in)

### 4. Add session check to /register route

**Location:** After line 23 in app.py (inside register function)

**Add:**
```python
@app.route("/register", methods=["GET", "POST"])
def register():
    # Redirect logged-in users to profile
    if session.get("user_id"):
        return redirect(url_for("profile"))
    
    if request.method == "POST":
        # ... existing code
```

**Key points:**
- Prevents logged-in users from creating duplicate accounts
- Same pattern as login route check

### 5. Update login.html template

**Location:** Replace lines 16-18 in templates/login.html

**Change from:**
```jinja2
{% if error %}
<div class="auth-error">{{ error }}</div>
{% endif %}
```

**Change to:**
```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="auth-{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```

**Key points:**
- Exact pattern from register.html (lines 16-22)
- Supports both error and success messages
- Uses existing CSS classes (auth-error, auth-success)

### 6. Update navbar in base.html

**Location:** Replace lines 21-24 in templates/base.html

**Change from:**
```html
<div class="nav-links">
    <a href="{{ url_for('login') }}">Sign in</a>
    <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
</div>
```

**Change to:**
```html
<div class="nav-links">
    {% if session.get('user_name') %}
        <span class="nav-welcome">Welcome, {{ session['user_name'] }}</span>
        <a href="{{ url_for('logout') }}" class="nav-cta">Sign out</a>
    {% else %}
        <a href="{{ url_for('login') }}">Sign in</a>
        <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
    {% endif %}
</div>
```

**Key points:**
- Check session.get('user_name') for login state
- Show user name and sign out link when logged in
- Keep original links when logged out
- Reuse nav-cta class for consistency
- May need CSS for nav-welcome (check if it exists, if not, use similar styling to nav-links a)

### 7. Update imports in app.py

**Location:** Line 2

**Change from:**
```python
from database.db import get_db, init_db, seed_db, create_user
```

**Change to:**
```python
from database.db import get_db, init_db, seed_db, create_user, authenticate_user
```

**Note:** check_password_hash doesn't need to be imported in app.py since it's only used in database/db.py

## Verification Steps

After implementation, verify the following:

### Test Login Flow
1. Start app: `python app.py`
2. Visit http://localhost:5001/login
3. Test empty form submission → shows validation errors
4. Test wrong email → "Invalid email or password"
5. Test correct email, wrong password → "Invalid email or password"
6. Test demo user (demo@spendly.com / demo123) → redirects to profile with "Welcome back, Demo User!"
7. Check navbar shows "Welcome, Demo User" and "Sign out"

### Test Logout Flow
1. While logged in, click "Sign out" in navbar
2. Should redirect to landing page
3. Should show "You have been logged out" message
4. Navbar should show "Sign in" and "Get started" again

### Test Session Protection
1. Register or login as a user
2. Try visiting /login → should redirect to profile
3. Try visiting /register → should redirect to profile
4. Logout
5. Visit /login and /register → should work normally

### Test Profile Access (future step)
1. Logout completely
2. Try visiting /profile → should show placeholder message (will be protected in future step)

### Database Verification
```bash
sqlite3 spendly.db "SELECT email, password_hash FROM users WHERE email = 'demo@spendly.com';"
```
- Verify password_hash starts with 'pbkdf2:sha256:' (werkzeug format)

### Session Verification
Use browser developer tools → Application → Cookies:
- After login: should see session cookie
- After logout: session cookie should be cleared or contain no user data

## Security Checklist

- [ ] Passwords never compared in plain text (check_password_hash used)
- [ ] Generic error message doesn't reveal if email exists
- [ ] session.clear() removes all session data
- [ ] SQL queries use parameterized format (?, not f-strings)
- [ ] Session contains minimal data (user_id and user_name only)
- [ ] Logged-in users cannot access registration/login forms

## Edge Cases Handled

- Empty email or password fields → validation errors
- Non-existent email → generic error
- Wrong password → generic error
- Already logged in visiting /login or /register → redirect to profile
- Logout when not logged in → safe (session.clear() is idempotent)
- Multiple login attempts → each attempt validated independently

## Notes

- The profile route is still a placeholder (Step 4 will implement it)
- CSS classes for flash messages already exist (auth-error, auth-success)
- May need to add CSS for nav-welcome if it doesn't exist in style.css
- Demo user (demo@spendly.com / demo123) created by seed_db() in Step 1
