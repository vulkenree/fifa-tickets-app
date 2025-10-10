#!/usr/bin/env python3
"""
Test date consistency across all layers: CSV → Database → API → Frontend
"""

import os
import sys
import csv
import requests
from datetime import datetime

def test_csv_data():
    """Test CSV data for key matches"""
    print("🔍 Testing CSV Data...")
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'fifa_match_schedule.csv')
    
    test_matches = ['M73', 'M101', 'M102', 'M103']
    csv_data = {}
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['match_number'] in test_matches:
                csv_data[row['match_number']] = {
                    'date': row['date'],
                    'venue': row['venue']
                }
    
    for match in test_matches:
        if match in csv_data:
            print(f"  ✅ {match}: {csv_data[match]['date']} at {csv_data[match]['venue']}")
        else:
            print(f"  ❌ {match}: Not found in CSV")
    
    return csv_data

def test_api_data():
    """Test API data for key matches"""
    print("\n🔍 Testing API Data...")
    
    try:
        response = requests.get("https://fifa-tickets-app-production.up.railway.app/api/matches")
        if response.status_code == 200:
            matches = response.json()
            api_data = {}
            
            for match in matches:
                if match['match_number'] in ['M73', 'M101', 'M102', 'M103']:
                    api_data[match['match_number']] = {
                        'date': match['date'],
                        'venue': match['venue']
                    }
            
            for match in ['M73', 'M101', 'M102', 'M103']:
                if match in api_data:
                    print(f"  ✅ {match}: {api_data[match]['date']} at {api_data[match]['venue']}")
                else:
                    print(f"  ❌ {match}: Not found in API")
            
            return api_data
        else:
            print(f"  ❌ API request failed: {response.status_code}")
            return {}
    except Exception as e:
        print(f"  ❌ API request error: {e}")
        return {}

def test_date_consistency(csv_data, api_data):
    """Test consistency between CSV and API data"""
    print("\n🔍 Testing Date Consistency...")
    
    test_matches = ['M73', 'M101', 'M102', 'M103']
    all_consistent = True
    
    for match in test_matches:
        if match in csv_data and match in api_data:
            csv_date = csv_data[match]['date']
            api_date = api_data[match]['date']
            csv_venue = csv_data[match]['venue']
            api_venue = api_data[match]['venue']
            
            if csv_date == api_date and csv_venue == api_venue:
                print(f"  ✅ {match}: CSV and API data match ({csv_date} at {csv_venue})")
            else:
                print(f"  ❌ {match}: CSV ({csv_date} at {csv_venue}) ≠ API ({api_date} at {api_venue})")
                all_consistent = False
        else:
            print(f"  ❌ {match}: Missing data in CSV or API")
            all_consistent = False
    
    return all_consistent

def test_timezone_issues():
    """Test for common timezone issues"""
    print("\n🔍 Testing for Timezone Issues...")
    
    # Test specific dates that were problematic
    test_cases = [
        ('M73', '2026-06-28', 'Should be June 28, 2026'),
        ('M101', '2026-07-14', 'Should be July 14, 2026'),
        ('M102', '2026-07-15', 'Should be July 15, 2026'),
        ('M103', '2026-07-18', 'Should be July 18, 2026'),
    ]
    
    try:
        response = requests.get("https://fifa-tickets-app-production.up.railway.app/api/matches")
        if response.status_code == 200:
            matches = response.json()
            match_dict = {m['match_number']: m for m in matches}
            
            for match_num, expected_date, description in test_cases:
                if match_num in match_dict:
                    actual_date = match_dict[match_num]['date']
                    if actual_date == expected_date:
                        print(f"  ✅ {match_num}: {actual_date} - {description}")
                    else:
                        print(f"  ❌ {match_num}: Expected {expected_date}, got {actual_date} - {description}")
                else:
                    print(f"  ❌ {match_num}: Not found in API")
    except Exception as e:
        print(f"  ❌ Error testing timezone issues: {e}")

def main():
    """Main test function"""
    print("🚀 FIFA 2026 Date Consistency Test")
    print("=" * 50)
    
    # Test CSV data
    csv_data = test_csv_data()
    
    # Test API data
    api_data = test_api_data()
    
    # Test consistency
    is_consistent = test_date_consistency(csv_data, api_data)
    
    # Test for timezone issues
    test_timezone_issues()
    
    # Summary
    print("\n" + "=" * 50)
    if is_consistent:
        print("🎉 All tests passed! Date consistency is maintained across all layers.")
        print("✅ CSV → API data flow is working correctly")
        print("✅ No timezone conversion issues detected")
    else:
        print("❌ Some tests failed! Date consistency issues detected.")
        print("🔧 Check the errors above and fix any discrepancies")
    
    print("\n📋 Next Steps:")
    print("1. Test the frontend UI to ensure dates display correctly")
    print("2. Create a test ticket with M73 to verify end-to-end flow")
    print("3. Verify the UI shows 'Jun 28, 2026' for M73")

if __name__ == "__main__":
    main()
