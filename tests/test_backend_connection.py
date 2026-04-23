"""
Test suite for backend connection - database query functions and profile route.

Tests cover:
- get_user_by_id()
- get_summary_stats()
- get_recent_transactions()
- get_category_breakdown()
- /profile route integration
"""

import pytest
import sqlite3
from database import queries as queries_module
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_db():
    """Create fresh in-memory database for each test."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create schema (same as database/db.py)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE expenses (
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
    yield conn
    conn.close()


@pytest.fixture
def sample_user(test_db):
    """Create test user."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ('John Doe', 'john@test.com', 'hash123', '2026-01-15 10:30:00')
    )
    test_db.commit()
    return cursor.lastrowid


@pytest.fixture
def sample_expenses(test_db, sample_user):
    """Create test expenses."""
    expenses = [
        (sample_user, 100.0, 'Food', '2026-04-20', 'Grocery'),
        (sample_user, 50.0, 'Transport', '2026-04-19', 'Gas'),
        (sample_user, 75.0, 'Food', '2026-04-18', 'Restaurant'),
        (sample_user, 200.0, 'Bills', '2026-04-17', 'Electricity'),
    ]
    cursor = test_db.cursor()
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    test_db.commit()


@pytest.fixture
def mock_get_db(test_db, monkeypatch):
    """Replace get_db() with test database connection."""
    # Import the db module to patch get_db at the source
    from database import db as db_module

    class MockConnection:
        """Wrapper that prevents close() from actually closing test database."""
        def __init__(self, real_conn):
            self._conn = real_conn

        def cursor(self):
            return self._conn.cursor()

        def commit(self):
            return self._conn.commit()

        def execute(self, *args, **kwargs):
            return self._conn.execute(*args, **kwargs)

        def close(self):
            # Don't actually close the test database
            pass

        def __getattr__(self, name):
            return getattr(self._conn, name)

    def _get_test_db():
        # Return a wrapper that prevents close() from affecting test database
        return MockConnection(test_db)

    # Patch get_db in both places: queries module and db module
    monkeypatch.setattr(queries_module, 'get_db', _get_test_db)
    monkeypatch.setattr(db_module, 'get_db', _get_test_db)


@pytest.fixture
def client():
    """Create Flask test client."""
    from app import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        yield client


# ============================================================================
# Unit Tests: get_user_by_id()
# ============================================================================

def test_get_user_by_id_success(test_db, sample_user, mock_get_db):
    """Test fetching existing user returns correct data."""
    result = get_user_by_id(sample_user)

    assert result is not None
    assert result['name'] == 'John Doe'
    assert result['email'] == 'john@test.com'
    assert result['initials'] == 'JD'
    assert result['member_since'] == 'January 2026'


def test_get_user_by_id_not_found(test_db, mock_get_db):
    """Test fetching non-existent user returns None."""
    result = get_user_by_id(999)
    assert result is None


def test_get_user_by_id_single_name(test_db, mock_get_db):
    """Test single name generates single letter initials."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ('Madonna', 'madonna@test.com', 'hash', '2026-02-01 00:00:00')
    )
    test_db.commit()
    user_id = cursor.lastrowid

    result = get_user_by_id(user_id)
    assert result is not None
    assert result['initials'] == 'M'
    assert result['member_since'] == 'February 2026'


# ============================================================================
# Unit Tests: get_summary_stats()
# ============================================================================

def test_get_summary_stats_with_expenses(test_db, sample_user, sample_expenses, mock_get_db):
    """Test summary stats with expenses returns correct totals."""
    result = get_summary_stats(sample_user)

    assert result['total_spent'] == 425.0  # 100 + 50 + 75 + 200
    assert result['transaction_count'] == 4
    assert result['top_category'] == 'Bills'  # 200.0 is highest


def test_get_summary_stats_no_expenses(test_db, sample_user, mock_get_db):
    """Test summary stats with no expenses returns zeros."""
    result = get_summary_stats(sample_user)

    assert result['total_spent'] == 0.0
    assert result['transaction_count'] == 0
    assert result['top_category'] == '—'


# ============================================================================
# Unit Tests: get_recent_transactions()
# ============================================================================

def test_get_recent_transactions_success(test_db, sample_user, sample_expenses, mock_get_db):
    """Test fetching transactions returns correct data in order."""
    result = get_recent_transactions(sample_user, limit=10)

    assert len(result) == 4
    # Check ordering (newest first)
    assert result[0]['date'] == '2026-04-20'
    assert result[0]['description'] == 'Grocery'
    assert result[0]['category'] == 'Food'
    assert result[0]['amount'] == 100.0
    assert result[3]['date'] == '2026-04-17'
    assert result[3]['description'] == 'Electricity'


def test_get_recent_transactions_limit(test_db, sample_user, sample_expenses, mock_get_db):
    """Test limit parameter restricts results."""
    result = get_recent_transactions(sample_user, limit=2)

    assert len(result) == 2
    assert result[0]['date'] == '2026-04-20'
    assert result[1]['date'] == '2026-04-19'


def test_get_recent_transactions_empty(test_db, sample_user, mock_get_db):
    """Test fetching transactions with no expenses returns empty list."""
    result = get_recent_transactions(sample_user)
    assert result == []


def test_get_recent_transactions_null_description(test_db, sample_user, mock_get_db):
    """Test NULL description is replaced with 'No description'."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (sample_user, 10.0, 'Other', '2026-04-21', None)
    )
    test_db.commit()

    result = get_recent_transactions(sample_user)
    assert result[0]['description'] == 'No description'


# ============================================================================
# Unit Tests: get_category_breakdown()
# ============================================================================

def test_get_category_breakdown_success(test_db, sample_user, sample_expenses, mock_get_db):
    """Test category breakdown returns correct totals and ordering."""
    result = get_category_breakdown(sample_user)

    assert len(result) == 3  # Food, Transport, Bills

    # Check ordering (highest amount first)
    assert result[0]['name'] == 'Bills'
    assert result[0]['total'] == 200.0

    assert result[1]['name'] == 'Food'
    assert result[1]['total'] == 175.0  # 100 + 75

    assert result[2]['name'] == 'Transport'
    assert result[2]['total'] == 50.0


def test_get_category_breakdown_empty(test_db, sample_user, mock_get_db):
    """Test category breakdown with no expenses returns empty list."""
    result = get_category_breakdown(sample_user)
    assert result == []


def test_get_category_breakdown_percentage_sum(test_db, sample_user, sample_expenses, mock_get_db):
    """Test that percentages always sum to exactly 100."""
    result = get_category_breakdown(sample_user)

    # Check percentages sum to 100
    total_pct = sum(cat['percentage'] for cat in result)
    assert total_pct == 100

    # Verify individual percentages are reasonable
    # Bills: 200/425 = 47.06% -> should be ~47
    # Food: 175/425 = 41.18% -> should be ~41
    # Transport: 50/425 = 11.76% -> should be ~12
    assert 45 <= result[0]['percentage'] <= 48  # Bills
    assert 40 <= result[1]['percentage'] <= 42  # Food
    assert 11 <= result[2]['percentage'] <= 13  # Transport


def test_get_category_breakdown_percentage_rounding(test_db, sample_user, mock_get_db):
    """Test percentage rounding with tricky values that don't divide evenly."""
    cursor = test_db.cursor()
    # Create 3 equal categories (33.33% each)
    expenses = [
        (sample_user, 33.33, 'A', '2026-04-20', 'Test'),
        (sample_user, 33.33, 'B', '2026-04-20', 'Test'),
        (sample_user, 33.34, 'C', '2026-04-20', 'Test'),
    ]
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    test_db.commit()

    result = get_category_breakdown(sample_user)

    # Percentages must sum to exactly 100
    total_pct = sum(cat['percentage'] for cat in result)
    assert total_pct == 100

    # Each should be around 33%
    for cat in result:
        assert 32 <= cat['percentage'] <= 34


def test_get_category_breakdown_single_category(test_db, sample_user, mock_get_db):
    """Test single category gets 100%."""
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        (sample_user, 100.0, 'Food', '2026-04-20', 'Test')
    )
    test_db.commit()

    result = get_category_breakdown(sample_user)

    assert len(result) == 1
    assert result[0]['percentage'] == 100


# ============================================================================
# Integration Tests: /profile route
# ============================================================================

def test_profile_route_unauthenticated(client):
    """Test unauthenticated access redirects to login."""
    response = client.get('/profile', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_profile_route_authenticated(client, test_db, sample_user, sample_expenses, mock_get_db):
    """Test authenticated user sees correct data."""
    # Login as sample user
    with client.session_transaction() as sess:
        sess['user_id'] = sample_user
        sess['user_name'] = 'John Doe'

    response = client.get('/profile')

    assert response.status_code == 200
    assert b'John Doe' in response.data
    assert b'john@test.com' in response.data
    assert b'JD' in response.data  # initials
    assert b'January 2026' in response.data  # member_since
    assert b'425.00' in response.data  # total_spent
    assert b'4' in response.data  # transaction_count (will appear multiple times in HTML)
    assert b'Bills' in response.data  # top_category
    assert b'Grocery' in response.data  # transaction description
    assert b'Electricity' in response.data  # transaction description
