#!/usr/bin/env python3
"""
Simple FIFA 2026 Match Schedule Migration Script
This script can run independently to update the database
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get database URL from environment variable"""
    return os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/fifa_tickets')

def load_corrected_schedule():
    """Load the corrected match schedule from CSV"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fifa_match_schedule.csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    corrected_matches = {}
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            match_number = row['match_number']
            corrected_matches[match_number] = {
                'date': row['date'],
                'venue': row['venue']
            }
    
    return corrected_matches

def main():
    """Main migration function"""
    print("🚀 FIFA 2026 Match Schedule Migration")
    print("=" * 40)
    
    try:
        # Load corrected schedule
        print("📖 Loading corrected match schedule...")
        corrected_matches = load_corrected_schedule()
        print(f"✅ Loaded {len(corrected_matches)} matches from CSV")
        
        # Connect to database
        database_url = get_database_url()
        print(f"🔗 Connecting to database...")
        
        # Parse the database URL
        if database_url.startswith('postgresql://'):
            # Extract connection details
            url_parts = database_url.replace('postgresql://', '').split('@')
            if len(url_parts) == 2:
                user_pass, host_db = url_parts
                user, password = user_pass.split(':')
                host_port, database = host_db.split('/')
                if ':' in host_port:
                    host, port = host_port.split(':')
                else:
                    host, port = host_port, '5432'
            else:
                raise ValueError("Invalid database URL format")
        else:
            raise ValueError("Only PostgreSQL URLs are supported")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check current matches
            cur.execute("SELECT COUNT(*) as count FROM match")
            match_count = cur.fetchone()['count']
            print(f"📊 Found {match_count} matches in database")
            
            # Check current tickets
            cur.execute("SELECT COUNT(*) as count FROM ticket")
            ticket_count = cur.fetchone()['count']
            print(f"🎫 Found {ticket_count} tickets in database")
            
            # Update matches
            print("🔄 Updating Match records...")
            updated_matches = 0
            for match_number, corrected_data in corrected_matches.items():
                cur.execute("""
                    UPDATE match 
                    SET date = %s, venue = %s 
                    WHERE match_number = %s
                """, (corrected_data['date'], corrected_data['venue'], match_number))
                
                if cur.rowcount > 0:
                    updated_matches += 1
                    print(f"  📝 Updated {match_number}: {corrected_data['date']} at {corrected_data['venue']}")
            
            # Update tickets
            print("🎫 Updating Ticket records...")
            updated_tickets = 0
            for match_number, corrected_data in corrected_matches.items():
                cur.execute("""
                    UPDATE ticket 
                    SET date = %s, venue = %s 
                    WHERE match_number = %s
                """, (corrected_data['date'], corrected_data['venue'], match_number))
                
                if cur.rowcount > 0:
                    updated_tickets += cur.rowcount
                    print(f"  🎫 Updated {cur.rowcount} tickets for {match_number}")
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Updated {updated_matches} Match records")
            print(f"✅ Updated {updated_tickets} Ticket records")
            print("\n🎉 Migration completed successfully!")
            
    except Exception as e:
        print(f"\n💥 Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
