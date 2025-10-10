#!/usr/bin/env python3
"""
FIFA 2026 Match Schedule Migration Script

This script updates existing Match and Ticket records in the database
with corrected dates and venues from the official FIFA 2026 schedule.

The script is idempotent - it can be run multiple times safely.
"""

import os
import sys
import csv
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Match, Ticket, db

def get_database_url():
    """Get database URL from environment variable or use default"""
    return os.environ.get('DATABASE_URL', 'sqlite:///fifa_tickets.db')

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

def backup_database(session):
    """Create a backup of current data before migration"""
    print("📋 Creating backup of current data...")
    
    # Backup matches
    matches_backup = session.query(Match).all()
    matches_data = []
    for match in matches_backup:
        matches_data.append({
            'match_number': match.match_number,
            'date': match.date,
            'venue': match.venue
        })
    
    # Backup tickets
    tickets_backup = session.query(Ticket).all()
    tickets_data = []
    for ticket in tickets_backup:
        tickets_data.append({
            'id': ticket.id,
            'match_number': ticket.match_number,
            'date': ticket.date,
            'venue': ticket.venue
        })
    
    # Save backup to file
    backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'match_migration_backup_{backup_timestamp}.txt'
    
    with open(backup_file, 'w') as f:
        f.write(f"FIFA Match Schedule Migration Backup - {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("MATCHES BACKUP:\n")
        for match in matches_data:
            f.write(f"{match['match_number']}: {match['date']} at {match['venue']}\n")
        
        f.write(f"\nTICKETS BACKUP:\n")
        for ticket in tickets_data:
            f.write(f"Ticket {ticket['id']}: {ticket['match_number']} - {ticket['date']} at {ticket['venue']}\n")
    
    print(f"✅ Backup saved to: {backup_file}")
    return len(matches_data), len(tickets_data)

def migrate_matches(session, corrected_matches):
    """Update Match records with corrected data"""
    print("🔄 Updating Match records...")
    
    updated_matches = 0
    for match_number, corrected_data in corrected_matches.items():
        match = session.query(Match).filter_by(match_number=match_number).first()
        
        if match:
            old_date = match.date
            old_venue = match.venue
            
            # Update if different
            if match.date != corrected_data['date'] or match.venue != corrected_data['venue']:
                match.date = corrected_data['date']
                match.venue = corrected_data['venue']
                updated_matches += 1
                print(f"  📝 Updated {match_number}: {old_date} at {old_venue} → {corrected_data['date']} at {corrected_data['venue']}")
    
    session.commit()
    print(f"✅ Updated {updated_matches} Match records")
    return updated_matches

def migrate_tickets(session, corrected_matches):
    """Update Ticket records with corrected data"""
    print("🎫 Updating Ticket records...")
    
    updated_tickets = 0
    tickets = session.query(Ticket).all()
    
    for ticket in tickets:
        if ticket.match_number in corrected_matches:
            corrected_data = corrected_matches[ticket.match_number]
            old_date = ticket.date
            old_venue = ticket.venue
            
            # Update if different
            if ticket.date != corrected_data['date'] or ticket.venue != corrected_data['venue']:
                ticket.date = corrected_data['date']
                ticket.venue = corrected_data['venue']
                updated_tickets += 1
                print(f"  🎫 Updated Ticket {ticket.id} ({ticket.match_number}): {old_date} at {old_venue} → {corrected_data['date']} at {corrected_data['venue']}")
    
    session.commit()
    print(f"✅ Updated {updated_tickets} Ticket records")
    return updated_tickets

def verify_migration(session, corrected_matches):
    """Verify that the migration was successful"""
    print("🔍 Verifying migration...")
    
    verification_errors = []
    
    # Check matches
    for match_number, expected_data in corrected_matches.items():
        match = session.query(Match).filter_by(match_number=match_number).first()
        if match:
            if match.date != expected_data['date'] or match.venue != expected_data['venue']:
                verification_errors.append(f"Match {match_number}: Expected {expected_data['date']} at {expected_data['venue']}, got {match.date} at {match.venue}")
        else:
            verification_errors.append(f"Match {match_number}: Not found in database")
    
    # Check tickets
    tickets = session.query(Ticket).all()
    for ticket in tickets:
        if ticket.match_number in corrected_matches:
            expected_data = corrected_matches[ticket.match_number]
            if ticket.date != expected_data['date'] or ticket.venue != expected_data['venue']:
                verification_errors.append(f"Ticket {ticket.id} ({ticket.match_number}): Expected {expected_data['date']} at {expected_data['venue']}, got {ticket.date} at {ticket.venue}")
    
    if verification_errors:
        print("❌ Verification failed:")
        for error in verification_errors:
            print(f"  {error}")
        return False
    else:
        print("✅ Migration verification successful!")
        return True

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
        print(f"🔗 Connecting to database: {database_url}")
        
        if database_url.startswith('sqlite'):
            engine = create_engine(database_url)
        else:
            engine = create_engine(database_url)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create backup
        matches_count, tickets_count = backup_database(session)
        print(f"📊 Found {matches_count} matches and {tickets_count} tickets in database")
        
        # Perform migration
        updated_matches = migrate_matches(session, corrected_matches)
        updated_tickets = migrate_tickets(session, corrected_matches)
        
        # Verify migration
        if verify_migration(session, corrected_matches):
            print("\n🎉 Migration completed successfully!")
            print(f"📈 Summary:")
            print(f"  - Updated {updated_matches} Match records")
            print(f"  - Updated {updated_tickets} Ticket records")
            print(f"  - Total matches in schedule: {len(corrected_matches)}")
        else:
            print("\n❌ Migration verification failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
