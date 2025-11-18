#!/usr/bin/env python3
"""
Docker-compatible test script for the enhanced FIFA 2026 chatbot functionality.
This script is designed to run inside the Docker container with PostgreSQL.
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

def test_query(llm_service, user_id, question, expected_function=None):
    """Test a single query and print results"""
    print(f"\n{'='*60}")
    print(f"❓ QUESTION: {question}")
    print(f"{'='*60}")
    
    try:
        response = llm_service.process_message(user_id, question)
        
        print(f"🤖 RESPONSE: {response['content']}")
        
        if response.get('function_called'):
            print(f"🔧 FUNCTION CALLED: {response['function_called']}")
            
            if response.get('function_result'):
                print(f"📊 RESULTS: {len(response['function_result'])} items")
                for i, item in enumerate(response['function_result'][:3]):  # Show first 3 results
                    print(f"   {i+1}. {item}")
                if len(response['function_result']) > 3:
                    print(f"   ... and {len(response['function_result']) - 3} more")
        
        if expected_function and response.get('function_called') != expected_function:
            print(f"⚠️  WARNING: Expected function '{expected_function}' but got '{response.get('function_called')}'")
        
        return response
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def run_tests():
    """Run all the test queries"""
    print("🚀 Starting FIFA 2026 Chatbot Tests (Docker Environment)")
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
        
        # Test queries
        test_queries = [
            {
                'question': "How many of my friends are interested in FIFA 2026 and have tickets?",
                'expected_function': 'get_friends_with_tickets_count',
                'description': 'Test friends with tickets count function'
            },
            {
                'question': "Which games have the most attendees?",
                'expected_function': 'get_matches_by_attendance',
                'description': 'Test matches by attendance (should ask for clarification)'
            },
            {
                'question': "Show me matches ranked by total ticket quantity",
                'expected_function': 'get_matches_by_attendance',
                'description': 'Test matches by attendance with specific ranking type'
            },
            {
                'question': "Recommend matches where John and Sarah are attending in New York",
                'expected_function': 'recommend_matches_by_friends_and_venue',
                'description': 'Test recommendation function with friends and venue'
            },
            {
                'question': "Show me all tickets for match M1",
                'expected_function': 'get_tickets_by_filters',
                'description': 'Test existing ticket filtering function'
            },
            {
                'question': "Which match has the highest total tickets sold?",
                'expected_function': 'execute_sql_query',
                'description': 'Test text-to-SQL functionality'
            }
        ]
        
        results = []
        for i, test in enumerate(test_queries, 1):
            print(f"\n🧪 TEST {i}: {test['description']}")
            result = test_query(llm_service, user_id, test['question'], test['expected_function'])
            results.append({
                'test': test,
                'result': result,
                'success': result is not None and not result.get('error', False)
            })
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)
        
        print(f"✅ Successful: {successful_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{status} Test {i}: {result['test']['description']}")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check SQL logs
        sql_logs = SQLQueryLog.query.filter_by(user_id=user_id).all()
        if sql_logs:
            print(f"\n📝 SQL Query Logs: {len(sql_logs)} queries logged")
            for log in sql_logs[-3:]:  # Show last 3
                print(f"   - {log.question[:50]}... -> {log.result_count} results")

if __name__ == "__main__":
    setup_test_data()
    run_tests()

