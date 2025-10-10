#!/usr/bin/env python3
"""
Production FIFA 2026 Match Schedule Migration Script
This script is designed to run on Railway production environment
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get database URL from environment variable"""
    return os.environ.get('DATABASE_URL')

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
    print("🚀 FIFA 2026 Match Schedule Production Migration")
    print("=" * 50)
    
    try:
        # Check if DATABASE_URL is set
        database_url = get_database_url()
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            sys.exit(1)
        
        # Load corrected schedule
        print("📖 Loading corrected match schedule...")
        corrected_matches = load_corrected_schedule()
        print(f"✅ Loaded {len(corrected_matches)} matches from CSV")
        
        # Connect to database
        print(f"🔗 Connecting to production database...")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check current matches
            cur.execute("SELECT COUNT(*) as count FROM match")
            match_count = cur.fetchone()['count']
            print(f"📊 Found {match_count} matches in production database")
            
            # Check current tickets
            cur.execute("SELECT COUNT(*) as count FROM ticket")
            ticket_count = cur.fetchone()['count']
            print(f"🎫 Found {ticket_count} tickets in production database")
            
            # Create backup table
            print("💾 Creating backup of current data...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS match_backup AS 
                SELECT * FROM match
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ticket_backup AS 
                SELECT * FROM ticket
            """)
            
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
            
            # Verify migration
            print("🔍 Verifying migration...")
            verification_errors = []
            
            for match_number, expected_data in corrected_matches.items():
                cur.execute("SELECT date, venue FROM match WHERE match_number = %s", (match_number,))
                result = cur.fetchone()
                if result:
                    if result['date'].strftime('%Y-%m-%d') != expected_data['date'] or result['venue'] != expected_data['venue']:
                        verification_errors.append(f"Match {match_number}: Expected {expected_data['date']} at {expected_data['venue']}, got {result['date']} at {result['venue']}")
                else:
                    verification_errors.append(f"Match {match_number}: Not found in database")
            
            if verification_errors:
                print("❌ Verification failed:")
                for error in verification_errors:
                    print(f"  {error}")
                print("🔄 Rolling back changes...")
                conn.rollback()
                sys.exit(1)
            else:
                print("✅ Migration verification successful!")
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Updated {updated_matches} Match records")
            print(f"✅ Updated {updated_tickets} Ticket records")
            print("\n🎉 Production migration completed successfully!")
            print("💾 Backup tables created: match_backup, ticket_backup")
            
    except Exception as e:
        print(f"\n💥 Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
