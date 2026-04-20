import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

# Import get_db from the database module
import sys
sys.path.insert(0, '.')
from database.db import get_db, init_db

# Pool of realistic Indian names across regions
FIRST_NAMES = [
    'Aarav', 'Aditi', 'Advait', 'Ananya', 'Arjun', 'Diya', 'Ishaan', 'Kavya',
    'Krishna', 'Lakshmi', 'Manoj', 'Neha', 'Priya', 'Rahul', 'Rohan', 'Sanjay',
    'Shreya', 'Tanvi', 'Vikram', 'Aisha', 'Deepak', 'Meera', 'Rajesh', 'Pooja',
    'Amit', 'Divya', 'Karan', 'Riya', 'Suresh', 'Anita'
]

LAST_NAMES = [
    'Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Desai', 'Nair', 'Iyer',
    'Gupta', 'Mehta', 'Shah', 'Rao', 'Joshi', 'Menon', 'Verma', 'Agarwal',
    'Chopra', 'Malhotra', 'Kapoor', 'Bhat', 'Pillai', 'Kulkarni', 'Das', 'Banerjee'
]

def generate_user():
    """Generate a random Indian user with unique email."""
    # Ensure database is initialized
    init_db()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Keep generating until we find a unique email
    max_attempts = 100
    for attempt in range(max_attempts):
        # Generate random name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        # Generate email with 2-3 digit random number
        email_first = first_name.lower()
        email_last = last_name.lower()
        random_digits = random.randint(10, 999)
        email = f"{email_first}.{email_last}{random_digits}@gmail.com"
        
        # Check if email already exists
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE email = ?', (email,))
        if cursor.fetchone()['count'] == 0:
            # Email is unique, proceed with insertion
            password_hash = generate_password_hash('password123')
            
            cursor.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (full_name, email, password_hash)
            )
            user_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Print confirmation
            print(f"✓ User created successfully:")
            print(f"  ID:    {user_id}")
            print(f"  Name:  {full_name}")
            print(f"  Email: {email}")
            return
    
    # If we exhausted all attempts
    conn.close()
    print("✗ Failed to generate unique email after 100 attempts")
    sys.exit(1)

if __name__ == '__main__':
    generate_user()
