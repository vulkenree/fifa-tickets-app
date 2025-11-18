#!/usr/bin/env python3
"""
Password Reset Script for FIFA Tickets App
This script allows you to reset a user's password in production
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

def get_database_url():
    """Get database URL from environment variable"""
    return os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/fifa_tickets')

def reset_user_password(username, new_password):
    """Reset a user's password in the database"""
    try:
        # Connect to the database
        conn = psycopg2.connect(get_database_url())
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user exists
        cursor.execute("SELECT id, username FROM \"user\" WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: User '{username}' not found in database")
            return False
        
        # Generate new password hash
        password_hash = generate_password_hash(new_password)
        
        # Update the password
        cursor.execute(
            "UPDATE \"user\" SET password_hash = %s WHERE username = %s",
            (password_hash, username)
        )
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully reset password for user '{username}'")
        print(f"New password: {new_password}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def list_users():
    """List all users in the database"""
    try:
        conn = psycopg2.connect(get_database_url())
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, username, created_at FROM \"user\" ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database")
            return
        
        print("\nUsers in database:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user['id']}, Username: {user['username']}, Created: {user['created_at']}")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python reset_user_password.py list                    # List all users")
        print("  python reset_user_password.py reset <username> <password>  # Reset user password")
        print("\nExamples:")
        print("  python reset_user_password.py list")
        print("  python reset_user_password.py reset admin newpassword123")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_users()
    elif command == "reset":
        if len(sys.argv) != 4:
            print("Error: reset command requires username and new password")
            print("Usage: python reset_user_password.py reset <username> <password>")
            return
        
        username = sys.argv[2]
        new_password = sys.argv[3]
        
        if len(new_password) < 6:
            print("Error: Password must be at least 6 characters long")
            return
        
        print(f"Resetting password for user '{username}'...")
        success = reset_user_password(username, new_password)
        
        if success:
            print("Password reset completed successfully!")
        else:
            print("Password reset failed!")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, reset")

if __name__ == "__main__":
    main()
