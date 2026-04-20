#!/usr/bin/env python3
"""
Script to seed random expenses for a specific user.
Usage: python seed_expenses.py <user_id> <count> <months>
"""

import sys
import random
from datetime import datetime, timedelta
from database.db import get_db


def seed_expenses(user_id, count, months):
    """
    Seeds random expenses for a user.

    Args:
        user_id: ID of the user
        count: Number of expenses to generate
        months: Number of past months to spread expenses across
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Step 1: Verify user exists
        cursor.execute('SELECT id, name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            print(f"No user found with id {user_id}.")
            return

        print(f"Seeding {count} expenses for user: {user['name']} (id={user_id})")
        print()

        # Step 2: Generate expenses
        # Categories with realistic Indian descriptions and amounts (₹)
        categories = {
            'Food': {
                'weight': 30,
                'descriptions': [
                    'Lunch at local dhaba',
                    'Dinner at restaurant',
                    'Grocery shopping',
                    'Street food snacks',
                    'Breakfast at cafe',
                    'Food delivery order',
                    'Sweets from halwai',
                ],
                'amount_range': (50, 800)
            },
            'Transport': {
                'weight': 25,
                'descriptions': [
                    'Auto rickshaw fare',
                    'Metro card recharge',
                    'Petrol for bike',
                    'Uber ride',
                    'Bus pass',
                    'Ola cab booking',
                ],
                'amount_range': (20, 500)
            },
            'Bills': {
                'weight': 15,
                'descriptions': [
                    'Electricity bill',
                    'Mobile recharge',
                    'Broadband internet',
                    'DTH recharge',
                    'Water bill',
                    'Gas cylinder',
                ],
                'amount_range': (200, 3000)
            },
            'Shopping': {
                'weight': 15,
                'descriptions': [
                    'Clothes from market',
                    'Electronics purchase',
                    'Home supplies',
                    'Book from bookstore',
                    'Gift for friend',
                    'Online shopping order',
                ],
                'amount_range': (200, 5000)
            },
            'Entertainment': {
                'weight': 8,
                'descriptions': [
                    'Movie tickets at PVR',
                    'Cricket match tickets',
                    'Gaming subscription',
                    'Concert entry',
                    'Museum visit',
                ],
                'amount_range': (100, 1500)
            },
            'Health': {
                'weight': 5,
                'descriptions': [
                    'Doctor consultation',
                    'Medicine from pharmacy',
                    'Lab tests',
                    'Dental checkup',
                    'Gym membership',
                ],
                'amount_range': (100, 2000)
            },
            'Other': {
                'weight': 2,
                'descriptions': [
                    'Miscellaneous expense',
                    'ATM withdrawal charge',
                    'Courier service',
                    'Photocopy and printing',
                ],
                'amount_range': (50, 1000)
            }
        }

        # Build weighted category list
        category_pool = []
        for category, config in categories.items():
            category_pool.extend([category] * config['weight'])

        # Generate random expenses
        expenses = []
        today = datetime.now()
        start_date = today - timedelta(days=months * 30)

        for _ in range(count):
            # Pick random category
            category = random.choice(category_pool)
            config = categories[category]

            # Generate random amount (rounded to 2 decimals)
            amount = round(random.uniform(*config['amount_range']), 2)

            # Pick random description
            description = random.choice(config['descriptions'])

            # Generate random date within the range
            days_range = (today - start_date).days
            random_days = random.randint(0, days_range)
            expense_date = start_date + timedelta(days=random_days)
            date_str = expense_date.strftime('%Y-%m-%d')

            expenses.append((user_id, amount, category, date_str, description))

        # Sort by date for better display
        expenses.sort(key=lambda x: x[3])

        # Step 3: Insert all expenses in a single transaction
        cursor.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            expenses
        )

        conn.commit()

        # Step 4: Display confirmation
        print(f"✓ Successfully inserted {count} expenses")
        print(f"✓ Date range: {expenses[0][3]} to {expenses[-1][3]}")
        print()
        print("Sample of inserted records:")
        print("-" * 80)

        # Show sample (all of them since count is only 5)
        for i, (uid, amt, cat, date, desc) in enumerate(expenses[:5], 1):
            print(f"{i}. ₹{amt:>8.2f} | {cat:<15} | {date} | {desc}")

        if len(expenses) > 5:
            print(f"... and {len(expenses) - 5} more")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])

        seed_expenses(user_id, count, months)
    except ValueError:
        print("Error: All arguments must be valid integers")
        print("Usage: /seed-expenses <user_id> <count> <months>")
        sys.exit(1)
