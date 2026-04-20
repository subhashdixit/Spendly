import sqlite3
from werkzeug.security import generate_password_hash


def get_db():
    """
    Opens and returns a SQLite connection to spendly.db.
    - Sets row_factory to sqlite3.Row for dict-like access
    - Enables foreign key constraints
    """
    conn = sqlite3.connect('spendly.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """
    Creates database tables if they don't exist.
    Safe to call multiple times (idempotent).
    """
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # Create expenses table with foreign key to users
    cursor.execute('''
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
    ''')

    conn.commit()
    conn.close()


def seed_db():
    """
    Inserts sample development data:
    - 1 demo user (demo@spendly.com / demo123)
    - 8 sample expenses across all categories

    Checks for existing data to prevent duplication.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute('SELECT COUNT(*) as count FROM users')
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return  # Data already seeded

    # Insert demo user with hashed password
    password_hash = generate_password_hash('demo123')
    cursor.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', password_hash)
    )
    user_id = cursor.lastrowid

    # Insert 8 sample expenses covering all categories
    # Dates spread across April 2026
    expenses = [
        (user_id, 65.40, 'Food', '2026-04-02', 'Grocery shopping at Whole Foods'),
        (user_id, 28.50, 'Food', '2026-04-15', 'Lunch at Italian restaurant'),
        (user_id, 45.00, 'Transport', '2026-04-05', 'Gas station fill-up'),
        (user_id, 120.00, 'Bills', '2026-04-01', 'Monthly electricity bill'),
        (user_id, 35.75, 'Health', '2026-04-10', 'Pharmacy - prescription medicine'),
        (user_id, 22.00, 'Entertainment', '2026-04-12', 'Movie tickets for two'),
        (user_id, 89.99, 'Shopping', '2026-04-18', 'New running shoes'),
        (user_id, 15.00, 'Other', '2026-04-20', None),
    ]

    cursor.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        expenses
    )

    conn.commit()
    conn.close()
