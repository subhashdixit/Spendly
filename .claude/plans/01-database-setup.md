# Database Setup Implementation Plan

## Context

This is the first implementation step for the Spendly expense tracking application. Currently, `database/db.py` contains only stub comments, and the Flask app has no database integration. This task establishes the foundational data layer that all future features (authentication, profile, expense tracking) will depend on.

The specification document (`.claude/specs/01_database_setup.md`) provides a comprehensive blueprint for implementing SQLite-based storage with two tables (users and expenses), proper constraints, and development seed data.

## Critical Files

- `database/db.py` — implement three core functions
- `app.py` — add database initialization on startup

## Implementation Steps

### 1. Implement `get_db()` in database/db.py

**Purpose:** Returns a configured SQLite connection with dictionary-like row access and foreign key enforcement.

**Implementation details:**
```python
import sqlite3

def get_db():
    conn = sqlite3.connect('spendly.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn
```

**Key requirements:**
- Database file: `spendly.db` in project root
- Must enable `PRAGMA foreign_keys = ON` for referential integrity
- Must set `row_factory = sqlite3.Row` for dict-like column access

### 2. Implement `init_db()` in database/db.py

**Purpose:** Creates database schema safely (idempotent).

**Implementation details:**
- Use `CREATE TABLE IF NOT EXISTS` for both tables
- Ensure foreign key constraint from expenses.user_id → users.id
- Use proper column types: INTEGER for IDs, TEXT for strings, REAL for amount, TEXT for dates
- Set defaults: created_at columns default to datetime('now')
- Add constraints: PRIMARY KEY AUTOINCREMENT, NOT NULL, UNIQUE on email

**Schema:**

**users table:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
)
```

**expenses table:**
```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

**Pattern:**
```python
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Execute CREATE TABLE statements
    cursor.execute(users_table_sql)
    cursor.execute(expenses_table_sql)
    
    conn.commit()
    conn.close()
```

### 3. Implement `seed_db()` in database/db.py

**Purpose:** Insert development data (1 demo user + 8 sample expenses) without duplication.

**Implementation details:**

**Demo user:**
- name: "Demo User"
- email: "demo@spendly.com"
- password: "demo123" (must be hashed with werkzeug.security.generate_password_hash)

**Sample expenses (8 total):**
- Must cover all categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other (at least one per category, plus one additional)
- Dates should be spread across April 2026 (current month)
- Use realistic amounts as REAL values (e.g., 45.50, not 45)
- Mix of expenses with and without descriptions
- All linked to demo user via user_id

**Idempotency pattern:**
```python
from werkzeug.security import generate_password_hash

def seed_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return  # Data already seeded
    
    # Insert demo user
    password_hash = generate_password_hash('demo123')
    cursor.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', password_hash)
    )
    user_id = cursor.lastrowid
    
    # Insert 8 expenses with parameterized queries
    expenses = [
        # (user_id, amount, category, date, description)
        # Cover all 7 categories, spread across April 2026
    ]
    
    cursor.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        expenses
    )
    
    conn.commit()
    conn.close()
```

**Categories to use (fixed list):**
- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

**Sample expense distribution:**
- 2 Food expenses (e.g., grocery shopping, restaurant)
- 1 Transport (e.g., gas, uber)
- 1 Bills (e.g., electricity)
- 1 Health (e.g., pharmacy)
- 1 Entertainment (e.g., movie tickets)
- 1 Shopping (e.g., clothing)
- 1 Other (e.g., miscellaneous)

**Dates:** Use YYYY-MM-DD format, spread across April 2026 (e.g., 2026-04-01, 2026-04-05, 2026-04-10, etc.)

### 4. Update app.py

**Location:** After `app = Flask(__name__)` and before route definitions

**Changes:**
```python
from flask import Flask, render_template
from database.db import get_db, init_db, seed_db

app = Flask(__name__)

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()

# Routes follow...
```

**Why app_context():** Ensures Flask application context is available if needed for future extensions (sessions, g object, etc.)

## Critical Requirements

1. **No ORMs:** Use raw SQL with sqlite3 module only
2. **Parameterized queries:** Always use `?` placeholders, never string formatting
3. **Foreign keys:** Must be enabled on every connection
4. **Password hashing:** Use `werkzeug.security.generate_password_hash('demo123')`
5. **Idempotency:** 
   - `init_db()` safe to run multiple times (CREATE TABLE IF NOT EXISTS)
   - `seed_db()` checks for existing data before inserting
6. **Data types:**
   - amount: REAL (not INTEGER)
   - dates: TEXT in YYYY-MM-DD format
   - IDs: INTEGER with PRIMARY KEY AUTOINCREMENT

## Expected Behavior After Implementation

**On first app startup:**
1. `spendly.db` file created in project root
2. Both tables created with proper schema
3. Demo user inserted with hashed password
4. 8 sample expenses inserted
5. App starts without errors on `http://localhost:5001`

**On subsequent startups:**
6. No errors (tables already exist)
7. No duplicate data (seed_db checks for existing users)
8. App continues to run normally

**Database constraints enforced:**
- Cannot insert duplicate email (UNIQUE constraint)
- Cannot insert expense with non-existent user_id (FOREIGN KEY constraint)
- Cannot insert NULL into required fields

## Verification Steps

1. **Start the app:**
   ```bash
   python app.py
   ```
   Should start without errors.

2. **Verify database file exists:**
   ```bash
   ls -la spendly.db
   ```

3. **Check database contents:**
   ```bash
   sqlite3 spendly.db
   sqlite> .schema
   sqlite> SELECT * FROM users;
   sqlite> SELECT * FROM expenses;
   ```
   Should show:
   - Correct table schemas
   - 1 user (demo@spendly.com)
   - 8 expenses across all categories

4. **Test idempotency:**
   ```bash
   python app.py  # Run again
   ```
   Should not create duplicate data.

5. **Test foreign key constraint:**
   ```bash
   sqlite3 spendly.db
   sqlite> INSERT INTO expenses (user_id, amount, category, date) VALUES (999, 50.0, 'Food', '2026-04-21');
   ```
   Should fail with foreign key constraint error.

6. **Test unique email constraint:**
   ```bash
   sqlite3 spendly.db
   sqlite> INSERT INTO users (name, email, password_hash) VALUES ('Test', 'demo@spendly.com', 'hash');
   ```
   Should fail with unique constraint error.

## Files Modified

- `database/db.py` (complete implementation)
- `app.py` (add imports and initialization calls)

## Files Created

- `spendly.db` (auto-created on first run)

## Dependencies

- `sqlite3` (Python standard library)
- `werkzeug.security` (already in requirements.txt via Flask)

No new pip packages needed.
