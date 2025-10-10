#!/usr/bin/env python3
"""
Force reload FIFA 2026 match schedule data from CSV
This script will replace all existing match data with the corrected CSV data
"""

import os
import sys
import csv
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Match

def force_reload_matches():
    """Force reload all match data from CSV"""
    with app.app_context():
        print("🔄 Force reloading FIFA 2026 match schedule...")
        
        # Delete all existing matches
        Match.query.delete()
        db.session.commit()
        print("🗑️  Deleted all existing match records")
        
        # Load corrected data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fifa_match_schedule.csv')
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                match_count = 0
                for row in reader:
                    match = Match(
                        match_number=row['match_number'],
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        venue=row['venue']
                    )
                    db.session.add(match)
                    match_count += 1
                db.session.commit()
                print(f"✅ Loaded {match_count} FIFA 2026 matches from corrected CSV")
                
        except FileNotFoundError:
            print(f"❌ Error: Match schedule CSV not found at {csv_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading match data: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    if force_reload_matches():
        print("🎉 Match data reload completed successfully!")
    else:
        print("💥 Match data reload failed!")
        sys.exit(1)
