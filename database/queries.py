"""
Query functions for fetching user and expense data.

This module provides database query functions for the profile page.
All functions follow the pattern of calling get_db() internally and
closing the connection before returning.
"""

import sqlite3
from datetime import datetime
from database.db import get_db


def get_user_by_id(user_id):
    """
    Fetch user details by ID.

    Args:
        user_id: Integer user ID

    Returns:
        Dict with name, email, initials, member_since or None if not found.
        Example: {
            'name': 'John Doe',
            'email': 'john@example.com',
            'initials': 'JD',
            'member_since': 'April 2026'
        }
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    # Generate initials: "Demo User" -> "DU", "Madonna" -> "M"
    name_parts = user['name'].strip().split()
    initials = ''.join(word[0].upper() for word in name_parts if word)

    # Format member_since: "2026-04-20 18:46:19" -> "April 2026"
    dt = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
    member_since = dt.strftime('%B %Y')

    return {
        'name': user['name'],
        'email': user['email'],
        'initials': initials,
        'member_since': member_since
    }


def get_summary_stats(user_id):
    """
    Get expense summary statistics for a user.

    Args:
        user_id: Integer user ID

    Returns:
        Dict with total_spent, transaction_count, top_category.
        Example: {
            'total_spent': 421.64,
            'transaction_count': 8,
            'top_category': 'Bills'
        }

        If user has no expenses, returns zeros and '—' for top_category.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get total spent and transaction count
    cursor.execute('''
        SELECT
            COALESCE(SUM(amount), 0) as total_spent,
            COUNT(*) as transaction_count
        FROM expenses
        WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()

    # Get top category (highest total spend)
    cursor.execute('''
        SELECT category
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY SUM(amount) DESC
        LIMIT 1
    ''', (user_id,))
    top_cat = cursor.fetchone()

    conn.close()

    return {
        'total_spent': float(stats['total_spent']),
        'transaction_count': int(stats['transaction_count']),
        'top_category': top_cat['category'] if top_cat else '—'
    }


def get_recent_transactions(user_id, limit=10):
    """
    Get recent transactions for a user.

    Args:
        user_id: Integer user ID
        limit: Maximum number of transactions to return (default 10)

    Returns:
        List of dicts, ordered by date descending (newest first).
        Example: [
            {
                'date': '2026-04-20',
                'description': 'Grocery Store',
                'category': 'Food',
                'amount': 100.50
            },
            ...
        ]

        Returns empty list if user has no expenses.
        NULL descriptions are replaced with 'No description'.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, description, category, amount
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
    ''', (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dicts
    transactions = []
    for row in rows:
        transactions.append({
            'date': row['date'],
            'description': row['description'] if row['description'] else 'No description',
            'category': row['category'],
            'amount': float(row['amount'])
        })

    return transactions


def get_category_breakdown(user_id):
    """
    Get spending breakdown by category with percentages.

    Args:
        user_id: Integer user ID

    Returns:
        List of dicts ordered by total descending.
        Example: [
            {
                'name': 'Bills',
                'total': 200.00,
                'percentage': 47  # Integer percentage
            },
            ...
        ]

        Percentages always sum to exactly 100 using fractional remainder algorithm.
        Returns empty list if user has no expenses.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            category as name,
            SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # Calculate percentages that sum to exactly 100
    categories = []
    grand_total = sum(row['total'] for row in rows)

    # Step 1: Calculate raw percentages and round
    for row in rows:
        raw_pct = (row['total'] / grand_total) * 100 if grand_total > 0 else 0
        categories.append({
            'name': row['name'],
            'total': float(row['total']),
            'raw_pct': raw_pct,
            'pct': round(raw_pct)
        })

    # Step 2: Adjust to sum to exactly 100
    total_pct = sum(cat['pct'] for cat in categories)
    diff = 100 - total_pct

    if diff != 0:
        # Sort by fractional remainder (raw - rounded)
        # Higher remainder = more likely to be rounded down, so adjust those first
        categories.sort(key=lambda x: x['raw_pct'] - x['pct'], reverse=(diff > 0))

        # Distribute difference one at a time
        for i in range(abs(diff)):
            if diff > 0:
                categories[i]['pct'] += 1
            else:
                categories[i]['pct'] -= 1

        # Restore original order (by total descending)
        categories.sort(key=lambda x: x['total'], reverse=True)

    # Step 3: Return clean result
    result = []
    for cat in categories:
        result.append({
            'name': cat['name'],
            'total': cat['total'],
            'percentage': cat['pct']
        })

    return result
