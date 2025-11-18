#!/usr/bin/env python3
"""
Direct function testing for the enhanced FIFA 2026 chatbot functionality.
Tests the new functions directly without OpenAI API calls.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/app')

from app import app
from llm_service import LLMService
from models import db, User, Ticket, Match, ChatConversation, ChatMessage, SQLQueryLog

def setup_test_data():
    """Set up test data for the chatbot tests"""
    print("🔧 Setting up test data...")
    
    with app.app_context():
        # Create test users if they don't exist
        test_users = [
            {'username': 'john_doe', 'password': 'password123'},
            {'username': 'sarah_smith', 'password': 'password123'},
            {'username': 'mike_wilson', 'password': 'password123'},
            {'username': 'alice_brown', 'password': 'password123'},
            {'username': 'bob_jones', 'password': 'password123'}
        ]
        
        for user_data in test_users:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                user = User(username=user_data['username'])
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()
        
        # Create test tickets
        users = User.query.all()
        matches = Match.query.limit(5).all()
        
        if users and matches:
            # Clear existing tickets for clean test
            Ticket.query.delete()
            
            test_tickets = [
                {'user': users[0], 'match': matches[0], 'name': 'John Doe', 'quantity': 2, 'venue': 'New York/New Jersey'},
                {'user': users[1], 'match': matches[0], 'name': 'Sarah Smith', 'quantity': 1, 'venue': 'New York/New Jersey'},
                {'user': users[2], 'match': matches[1], 'name': 'Mike Wilson', 'quantity': 3, 'venue': 'Los Angeles'},
                {'user': users[1], 'match': matches[1], 'name': 'Sarah Smith', 'quantity': 2, 'venue': 'Los Angeles'},
                {'user': users[3], 'match': matches[2], 'name': 'Alice Brown', 'quantity': 1, 'venue': 'Miami'},
                {'user': users[4], 'match': matches[2], 'name': 'Bob Jones', 'quantity': 4, 'venue': 'Miami'},
                {'user': users[0], 'match': matches[3], 'name': 'John Doe', 'quantity': 1, 'venue': 'Boston'},
                {'user': users[2], 'match': matches[3], 'name': 'Mike Wilson', 'quantity': 2, 'venue': 'Boston'},
            ]
            
            for ticket_data in test_tickets:
                ticket = Ticket(
                    user_id=ticket_data['user'].id,
                    name=ticket_data['name'],
                    match_number=ticket_data['match'].match_number,
                    date=ticket_data['match'].date,
                    venue=ticket_data['venue'],
                    ticket_category='General',
                    quantity=ticket_data['quantity'],
                    ticket_info='Test ticket'
                )
                db.session.add(ticket)
            
            db.session.commit()
            print(f"✅ Created {len(test_tickets)} test tickets")
        else:
            print("⚠️  No users or matches found for test data")

def test_function_direct(llm_service, user_id, function_name, function_args=None):
    """Test a function directly"""
    print(f"\n{'='*60}")
    print(f"🔧 TESTING FUNCTION: {function_name}")
    print(f"📝 ARGS: {function_args}")
    print(f"{'='*60}")
    
    try:
        if function_name == "get_friends_with_tickets_count":
            result = llm_service.get_friends_with_tickets_count(user_id)
        elif function_name == "get_matches_by_attendance":
            ranking_type = function_args.get('ranking_type', 'users') if function_args else 'users'
            result = llm_service.get_matches_by_attendance(user_id, ranking_type)
        elif function_name == "recommend_matches_by_friends_and_venue":
            usernames = function_args.get('preferred_usernames') if function_args else None
            venue = function_args.get('preferred_venue') if function_args else None
            result = llm_service.recommend_matches_by_friends_and_venue(user_id, usernames, venue)
        elif function_name == "get_tickets_by_filters":
            filters = function_args.get('filters') if function_args else None
            result = llm_service.get_tickets_by_filters(user_id, filters)
        else:
            result = {"error": f"Unknown function: {function_name}"}
        
        print(f"✅ SUCCESS: {len(result)} results returned")
        for i, item in enumerate(result[:5]):  # Show first 5 results
            print(f"   {i+1}. {item}")
        if len(result) > 5:
            print(f"   ... and {len(result) - 5} more")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def run_direct_tests():
    """Run direct function tests"""
    print("🚀 Starting Direct Function Tests (Docker Environment)")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🗄️  Database: {os.environ.get('DATABASE_URL', 'SQLite (local)')}")
    
    with app.app_context():
        # Initialize LLM service
        llm_service = LLMService()
        
        # Get a test user
        test_user = User.query.first()
        if not test_user:
            print("❌ No test user found. Please create a user first.")
            return
        
        user_id = test_user.id
        print(f"👤 Using test user: {test_user.username} (ID: {user_id})")
        
        # Test functions directly
        test_functions = [
            {
                'function_name': 'get_friends_with_tickets_count',
                'function_args': None,
                'description': 'Test friends with tickets count function'
            },
            {
                'function_name': 'get_matches_by_attendance',
                'function_args': {'ranking_type': 'users'},
                'description': 'Test matches by attendance (users)'
            },
            {
                'function_name': 'get_matches_by_attendance',
                'function_args': {'ranking_type': 'tickets'},
                'description': 'Test matches by attendance (tickets)'
            },
            {
                'function_name': 'recommend_matches_by_friends_and_venue',
                'function_args': {'preferred_usernames': ['john_doe', 'sarah_smith'], 'preferred_venue': 'New York'},
                'description': 'Test recommendation function with friends and venue'
            },
            {
                'function_name': 'get_tickets_by_filters',
                'function_args': {'filters': {'match_number': 'M1'}},
                'description': 'Test ticket filtering function'
            }
        ]
        
        results = []
        for i, test in enumerate(test_functions, 1):
            print(f"\n🧪 TEST {i}: {test['description']}")
            result = test_function_direct(llm_service, user_id, test['function_name'], test['function_args'])
            results.append({
                'test': test,
                'result': result,
                'success': result is not None and not (isinstance(result, dict) and result.get('error'))
            })
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 DIRECT TEST SUMMARY")
        print(f"{'='*60}")
        
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)
        
        print(f"✅ Successful: {successful_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{status} Test {i}: {result['test']['description']}")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    setup_test_data()
    run_direct_tests()

