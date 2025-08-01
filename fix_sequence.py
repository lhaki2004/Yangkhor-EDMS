#!/usr/bin/env python3
"""
Script to fix PostgreSQL sequence for auth_user table after manual database manipulation.
This script resets the sequence to start from the maximum ID + 1.
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'mayan',
    'user': 'mayan',
    'password': 'mayanuserpass'
}

def fix_auth_user_sequence():
    """Fix the auth_user sequence to start from max ID + 1"""
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database successfully.")
        
        # Get the maximum ID from auth_user table
        cursor.execute("SELECT MAX(id) FROM auth_user;")
        max_id = cursor.fetchone()[0]
        
        if max_id is None:
            print("No users found in auth_user table. Setting sequence to start from 1.")
            max_id = 0
        else:
            print(f"Maximum user ID found: {max_id}")
        
        # Reset the sequence to start from max_id + 1
        next_id = max_id + 1
        reset_query = sql.SQL("ALTER SEQUENCE auth_user_id_seq RESTART WITH {};").format(
            sql.Literal(next_id)
        )
        
        cursor.execute(reset_query)
        conn.commit()
        
        print(f"Successfully reset auth_user_id_seq to start from {next_id}")
        
        # Verify the sequence value
        cursor.execute("SELECT last_value FROM auth_user_id_seq;")
        current_value = cursor.fetchone()[0]
        print(f"Current sequence value: {current_value}")
        
        cursor.close()
        conn.close()
        
        print("Sequence fix completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_auth_user_table():
    """Check the current state of auth_user table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, username, email FROM auth_user ORDER BY id;")
        users = cursor.fetchall()
        
        print(f"\nCurrent users in auth_user table:")
        print("ID | Username | Email")
        print("-" * 50)
        for user in users:
            print(f"{user[0]} | {user[1]} | {user[2]}")
        
        # Get sequence info
        cursor.execute("SELECT last_value, is_called FROM auth_user_id_seq;")
        seq_info = cursor.fetchone()
        print(f"\nSequence info: last_value={seq_info[0]}, is_called={seq_info[1]}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Mayan EDMS - PostgreSQL Sequence Fix Tool")
    print("=" * 50)
    
    # Check current state
    print("Checking current database state...")
    check_auth_user_table()
    
    print("\n" + "=" * 50)
    
    # Fix the sequence
    print("Fixing auth_user sequence...")
    if fix_auth_user_sequence():
        print("\n" + "=" * 50)
        print("Verifying fix...")
        check_auth_user_table()
        print("\n✅ Sequence fix completed! You should now be able to create new users.")
    else:
        print("\n❌ Failed to fix sequence. Please check the error messages above.")
        sys.exit(1) 