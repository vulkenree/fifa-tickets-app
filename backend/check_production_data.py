#!/usr/bin/env python3
"""
Check production database data for specific matches
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get database URL from environment variable"""
    return os.environ.get('DATABASE_URL')

def check_match_data():
    """Check specific match data in production"""
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check M73 specifically
            cur.execute("SELECT match_number, date, venue FROM match WHERE match_number = 'M73'")
            m73 = cur.fetchone()
            if m73:
                print(f"M73: {m73['date']} at {m73['venue']}")
            else:
                print("M73 not found")
            
            # Check a few more matches around that area
            cur.execute("SELECT match_number, date, venue FROM match WHERE match_number IN ('M70', 'M71', 'M72', 'M73', 'M74', 'M75') ORDER BY match_number")
            matches = cur.fetchall()
            print("\nMatches M70-M75:")
            for match in matches:
                print(f"{match['match_number']}: {match['date']} at {match['venue']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_match_data()
