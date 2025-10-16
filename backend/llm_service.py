import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from models import db, Ticket, User, Match, ChatMessage, SQLQueryLog
from datetime import datetime, date
import re

class LLMService:
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o"
        else:
            self.client = None
            self.model = "gpt-4o"
            print("⚠️  Warning: OPENAI_API_KEY not set. LLM service will return mock responses.")
        
        # System prompt with database schema documentation
        self.system_prompt = """You are an AI assistant for the FIFA 2026 World Cup ticket management system. You help users query their ticket data and get intelligent recommendations.

DATABASE SCHEMA:
- Users: id, username, created_at (NO ACCESS to password_hash)
- Tickets: id, user_id, name, match_number, date, venue, ticket_category, quantity, ticket_info, ticket_price, created_at, updated_at
- Matches: id, match_number, date, venue
- ChatConversations: id, user_id, title, created_at, updated_at, is_saved
- ChatMessages: id, conversation_id, role, content, created_at
- SQLQueryLog: id, user_id, conversation_id, question, generated_sql, result_count, executed_at, error_message

SECURITY RULES:
1. NEVER access user.password_hash - this field is completely off-limits
2. Only use the provided functions to query data
3. Always validate user permissions before showing data
4. Be helpful but respect privacy

AVAILABLE FUNCTIONS:
- get_tickets_by_filters: Query tickets with various filters
- get_friends_attending_match: Find which friends are attending a specific match
- get_weekend_matches: Get matches for specific weekends
- get_venue_info: Get information about venues and cities
- get_user_tickets: Get tickets for a specific user
- get_match_details: Get details about a specific match
- get_friends_with_tickets_count: Get all users with tickets and their counts
- get_matches_by_attendance: Get matches ranked by attendance (users or tickets)
- recommend_matches_by_friends_and_venue: Recommend matches based on friends and venue
- execute_sql_query: Execute natural language queries using text-to-SQL

RESPONSE GUIDELINES:
- Provide clear, helpful answers in English only
- Use natural language, not technical jargon
- When recommending matches, consider friend attendance and venue proximity
- Ask clarifying questions when needed (travel preferences, budget, etc.)
- Be conversational and friendly
- If you can't find specific information, say so clearly

ONE-SHOT EXAMPLES:
Q: "How many friends have FIFA tickets?"
A: Call get_friends_with_tickets_count(), return formatted list with counts

Q: "Which match has the most attendees?"
A: Call get_matches_by_attendance() with clarifying question about users vs tickets

Q: "Recommend matches where John is going to New York venues"
A: Call recommend_matches_by_friends_and_venue(usernames=['John'], venue='New York')

Q: "Show me all tickets for match M50"
A: Call get_tickets_by_filters(filters={'match_number': 'M50'})

Q: "Which friends are going to the final match?"
A: Use execute_sql_query to find the final match, then get friends attending

EXAMPLE QUESTIONS YOU CAN HANDLE:
- "How many of my friends are interested in FIFA 2026 and have tickets?"
- "Which games have the most attendees?" (will ask for clarification)
- "Recommend matches where John and Sarah are attending in New York"
- "Show me matches with the most friends attending"
- "Which match has the highest total tickets sold?"
- "What's a good weekend where my friends have tickets and venues are close together?"
- "Show me all matches in New York that my friends are attending"
- "Which friends are going to Match M50?"
- "What matches are happening on July 4th weekend?"
- "Which cities have the most match activity?" """

    def get_tickets_by_filters(self, user_id: int, filters: Dict[str, Any] = None) -> List[Dict]:
        """Get tickets with optional filters - SECURE VERSION (no password access)"""
        try:
            query = db.session.query(Ticket, User.username).join(User, Ticket.user_id == User.id)
            
            if filters:
                if 'venue' in filters:
                    query = query.filter(Ticket.venue.ilike(f"%{filters['venue']}%"))
                if 'match_number' in filters:
                    query = query.filter(Ticket.match_number == filters['match_number'])
                if 'date_from' in filters:
                    query = query.filter(Ticket.date >= filters['date_from'])
                if 'date_to' in filters:
                    query = query.filter(Ticket.date <= filters['date_to'])
                if 'category' in filters:
                    query = query.filter(Ticket.ticket_category == filters['category'])
                if 'username' in filters:
                    query = query.filter(User.username.ilike(f"%{filters['username']}%"))
            
            results = query.all()
            
            # Convert to safe format (no password_hash)
            tickets = []
            for ticket, username in results:
                ticket_dict = ticket.to_dict()
                ticket_dict['username'] = username  # Use the joined username
                tickets.append(ticket_dict)
            
            return tickets
        except Exception as e:
            print(f"Error in get_tickets_by_filters: {e}")
            return []

    def get_friends_attending_match(self, user_id: int, match_number: str) -> List[Dict]:
        """Find which friends are attending a specific match"""
        try:
            # Get all users except the current user who have tickets for this match
            query = db.session.query(Ticket, User.username).join(User, Ticket.user_id == User.id).filter(
                Ticket.match_number == match_number,
                Ticket.user_id != user_id
            )
            
            results = query.all()
            
            friends = []
            for ticket, username in results:
                friends.append({
                    'username': username,
                    'name': ticket.name,
                    'quantity': ticket.quantity,
                    'category': ticket.ticket_category,
                    'venue': ticket.venue,
                    'date': ticket.date.strftime('%Y-%m-%d')
                })
            
            return friends
        except Exception as e:
            print(f"Error in get_friends_attending_match: {e}")
            return []

    def get_weekend_matches(self, start_date: str, end_date: str) -> List[Dict]:
        """Get matches for a specific weekend"""
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            matches = Match.query.filter(
                Match.date >= start_date_obj,
                Match.date <= end_date_obj
            ).all()
            
            return [match.to_dict() for match in matches]
        except Exception as e:
            print(f"Error in get_weekend_matches: {e}")
            return []

    def get_venue_info(self, venue: str = None) -> List[Dict]:
        """Get information about venues and cities"""
        try:
            if venue:
                # Get all matches for a specific venue
                matches = Match.query.filter(Match.venue.ilike(f"%{venue}%")).all()
            else:
                # Get all unique venues
                matches = Match.query.all()
            
            venues = {}
            for match in matches:
                if match.venue not in venues:
                    venues[match.venue] = {
                        'venue': match.venue,
                        'matches': [],
                        'total_matches': 0
                    }
                venues[match.venue]['matches'].append(match.to_dict())
                venues[match.venue]['total_matches'] += 1
            
            return list(venues.values())
        except Exception as e:
            print(f"Error in get_venue_info: {e}")
            return []

    def get_user_tickets(self, user_id: int) -> List[Dict]:
        """Get all tickets for a specific user"""
        try:
            tickets = Ticket.query.filter_by(user_id=user_id).all()
            return [ticket.to_dict() for ticket in tickets]
        except Exception as e:
            print(f"Error in get_user_tickets: {e}")
            return []

    def get_match_details(self, match_number: str) -> Optional[Dict]:
        """Get details about a specific match"""
        try:
            match = Match.query.filter_by(match_number=match_number).first()
            return match.to_dict() if match else None
        except Exception as e:
            print(f"Error in get_match_details: {e}")
            return None

    def get_conversation_context(self, conversation_id: int, limit: int = 20) -> List[Dict]:
        """Get recent conversation context for the LLM"""
        try:
            messages = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(
                ChatMessage.created_at.desc()
            ).limit(limit).all()
            
            # Reverse to get chronological order
            return [msg.to_dict() for msg in reversed(messages)]
        except Exception as e:
            print(f"Error in get_conversation_context: {e}")
            return []

    def execute_sql_query(self, user_id: int, question: str, conversation_id: int = None) -> Dict[str, Any]:
        """Execute a natural language query using GPT-4o text-to-SQL"""
        try:
            if not self.client:
                return {
                    "sql": "SELECT 'Mock SQL' as query",
                    "results": [{"message": "Mock response - OpenAI API key not set"}],
                    "explanation": "This is a mock response for testing"
                }

            # Database schema for GPT-4o
            schema_prompt = """
DATABASE SCHEMA (PostgreSQL):
- "user": id (INTEGER PRIMARY KEY), username (TEXT), created_at (TIMESTAMP)
- ticket: id (INTEGER PRIMARY KEY), user_id (INTEGER), name (TEXT), match_number (TEXT), 
  date (DATE), venue (TEXT), ticket_category (TEXT), quantity (INTEGER), 
  ticket_info (TEXT), ticket_price (REAL), created_at (TIMESTAMP), updated_at (TIMESTAMP)
- match: id (INTEGER PRIMARY KEY), match_number (TEXT), date (DATE), venue (TEXT)
- chat_conversation: id (INTEGER PRIMARY KEY), user_id (INTEGER), title (TEXT), 
  created_at (TIMESTAMP), updated_at (TIMESTAMP), is_saved (BOOLEAN)
- chat_message: id (INTEGER PRIMARY KEY), conversation_id (INTEGER), role (TEXT), 
  content (TEXT), created_at (TIMESTAMP)
- sql_query_log: id (INTEGER PRIMARY KEY), user_id (INTEGER), conversation_id (INTEGER), 
  question (TEXT), generated_sql (TEXT), result_count (INTEGER), executed_at (TIMESTAMP), 
  error_message (TEXT)

SAFETY RULES:
1. ONLY generate SELECT queries - NO INSERT, UPDATE, DELETE, DROP, ALTER
2. Use proper JOINs to connect related tables
3. Always use parameterized queries or safe string formatting
4. Return results in a readable format
5. Use double quotes around table names: "user", "match", etc.

Generate a safe SQL query for this question: {question}
Return ONLY the SQL query, no explanations.
"""

            # Get SQL from GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": schema_prompt.format(question=question)},
                    {"role": "user", "content": question}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Validate SQL safety
            sql_upper = sql_query.upper()
            dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE']
            if any(keyword in sql_upper for keyword in dangerous_keywords):
                raise ValueError(f"Unsafe SQL query detected: {sql_query}")
            
            # Execute query
            from sqlalchemy import text
            result = db.session.execute(text(sql_query))
            results = [dict(row._mapping) for row in result]
            
            # Log the query
            self.log_sql_review(user_id, conversation_id, question, sql_query, len(results))
            
            return {
                "sql": sql_query,
                "results": results,
                "explanation": f"Query returned {len(results)} results"
            }
            
        except Exception as e:
            error_msg = str(e)
            # Log the error
            if 'sql_query' in locals():
                self.log_sql_review(user_id, conversation_id, question, sql_query, 0, error_msg)
            
            return {
                "sql": sql_query if 'sql_query' in locals() else "Error generating SQL",
                "results": [],
                "explanation": f"Error: {error_msg}"
            }

    def log_sql_review(self, user_id: int, conversation_id: int, question: str, 
                      sql: str, result_count: int, error_message: str = None):
        """Log SQL query for review"""
        try:
            log_entry = SQLQueryLog(
                user_id=user_id,
                conversation_id=conversation_id,
                question=question,
                generated_sql=sql,
                result_count=result_count,
                error_message=error_message
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            print(f"Error logging SQL query: {e}")

    def get_friends_with_tickets_count(self, user_id: int) -> List[Dict]:
        """Get distinct users who have tickets with their ticket counts"""
        try:
            query = """
            SELECT DISTINCT u.username, u.id, COUNT(t.id) as ticket_count 
            FROM "user" u 
            JOIN ticket t ON u.id = t.user_id 
            GROUP BY u.id, u.username
            ORDER BY ticket_count DESC
            """
            
            from sqlalchemy import text
            result = db.session.execute(text(query))
            friends = []
            for row in result:
                friends.append({
                    'username': row.username,
                    'user_id': row.id,
                    'ticket_count': row.ticket_count
                })
            
            return friends
        except Exception as e:
            print(f"Error in get_friends_with_tickets_count: {e}")
            return []

    def get_matches_by_attendance(self, user_id: int, ranking_type: str = "users") -> List[Dict]:
        """Get matches ranked by attendance (users or tickets)"""
        try:
            if ranking_type == "users":
                # Count distinct users per match
                query = """
                SELECT t.match_number, t.venue, t.date, COUNT(DISTINCT t.user_id) as user_count
                FROM ticket t
                GROUP BY t.match_number, t.venue, t.date
                ORDER BY user_count DESC
                """
            else:
                # Sum total tickets per match
                query = """
                SELECT t.match_number, t.venue, t.date, SUM(t.quantity) as total_tickets
                FROM ticket t
                GROUP BY t.match_number, t.venue, t.date
                ORDER BY total_tickets DESC
                """
            
            from sqlalchemy import text
            result = db.session.execute(text(query))
            matches = []
            for row in result:
                matches.append({
                    'match_number': row.match_number,
                    'venue': row.venue,
                    'date': row.date.strftime('%Y-%m-%d') if row.date else None,
                    'user_count' if ranking_type == "users" else 'total_tickets': 
                        row.user_count if ranking_type == "users" else row.total_tickets
                })
            
            return matches
        except Exception as e:
            print(f"Error in get_matches_by_attendance: {e}")
            return []

    def recommend_matches_by_friends_and_venue(self, user_id: int, preferred_usernames: List[str] = None, 
                                             preferred_venue: str = None) -> List[Dict]:
        """Recommend matches based on friends attending and venue preference"""
        try:
            # Build the query based on parameters
            where_conditions = []
            params = {}
            
            if preferred_usernames:
                # Find user IDs for the usernames
                username_placeholders = ','.join([f':username_{i}' for i in range(len(preferred_usernames))])
                where_conditions.append(f"t.user_id IN (SELECT id FROM \"user\" WHERE username IN ({username_placeholders}))")
                for i, username in enumerate(preferred_usernames):
                    params[f'username_{i}'] = username
            
            if preferred_venue:
                where_conditions.append("t.venue ILIKE :venue")
                params['venue'] = f"%{preferred_venue}%"
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
            SELECT 
                t.match_number, 
                t.venue, 
                t.date,
                COUNT(DISTINCT t.user_id) as friend_count,
                SUM(t.quantity) as total_tickets,
                STRING_AGG(DISTINCT u.username, ',') as attending_friends
            FROM ticket t
            JOIN "user" u ON t.user_id = u.id
            {where_clause}
            GROUP BY t.match_number, t.venue, t.date
            ORDER BY friend_count DESC, total_tickets DESC
            """
            
            from sqlalchemy import text
            result = db.session.execute(text(query), params)
            matches = []
            for row in result:
                matches.append({
                    'match_number': row.match_number,
                    'venue': row.venue,
                    'date': row.date.strftime('%Y-%m-%d') if row.date else None,
                    'friend_count': row.friend_count,
                    'total_tickets': row.total_tickets,
                    'attending_friends': row.attending_friends.split(',') if row.attending_friends else []
                })
            
            return matches
        except Exception as e:
            print(f"Error in recommend_matches_by_friends_and_venue: {e}")
            return []

    def process_message(self, user_id: int, message: str, conversation_id: int = None) -> Dict[str, Any]:
        """Process a user message and return LLM response"""
        try:
            # If no OpenAI client, return mock response for testing
            if not self.client:
                return {
                    "content": f"Mock response: I understand you're asking about '{message}'. In a real implementation, I would query your FIFA 2026 ticket data and provide intelligent recommendations. Please set the OPENAI_API_KEY environment variable to enable the full AI assistant functionality.",
                    "function_called": None,
                    "function_result": None,
                    "error": False
                }
            # Get conversation context if conversation_id provided
            context_messages = []
            if conversation_id:
                context_messages = self.get_conversation_context(conversation_id)
            
            # Prepare function definitions for OpenAI
            functions = [
                {
                    "name": "get_tickets_by_filters",
                    "description": "Query tickets with various filters like venue, date, category, username",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filters": {
                                "type": "object",
                                "properties": {
                                    "venue": {"type": "string", "description": "Venue name to filter by"},
                                    "match_number": {"type": "string", "description": "Match number to filter by"},
                                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                                    "category": {"type": "string", "description": "Ticket category"},
                                    "username": {"type": "string", "description": "Username to filter by"}
                                }
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_friends_attending_match",
                    "description": "Find which friends are attending a specific match",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "match_number": {"type": "string", "description": "Match number (e.g., M50)"}
                        },
                        "required": ["match_number"]
                    }
                },
                {
                    "name": "get_weekend_matches",
                    "description": "Get matches for a specific weekend or date range",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                            "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                        },
                        "required": ["start_date", "end_date"]
                    }
                },
                {
                    "name": "get_venue_info",
                    "description": "Get information about venues and cities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "venue": {"type": "string", "description": "Venue name to get info for (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_user_tickets",
                    "description": "Get all tickets for the current user",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_match_details",
                    "description": "Get details about a specific match",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "match_number": {"type": "string", "description": "Match number (e.g., M50)"}
                        },
                        "required": ["match_number"]
                    }
                },
                {
                    "name": "get_friends_with_tickets_count",
                    "description": "Get all users who have tickets with their ticket counts",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_matches_by_attendance",
                    "description": "Get matches ranked by attendance - either by number of users or total tickets",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ranking_type": {"type": "string", "enum": ["users", "tickets"], "description": "Rank by number of unique users or total ticket quantity"}
                        },
                        "required": ["ranking_type"]
                    }
                },
                {
                    "name": "recommend_matches_by_friends_and_venue",
                    "description": "Recommend matches based on friends attending and venue preference",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "preferred_usernames": {"type": "array", "items": {"type": "string"}, "description": "List of usernames to find matches for"},
                            "preferred_venue": {"type": "string", "description": "Preferred venue name (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "execute_sql_query",
                    "description": "Execute a natural language query using text-to-SQL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Natural language question to convert to SQL"}
                        },
                        "required": ["question"]
                    }
                }
            ]

            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation context
            for msg in context_messages:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current user message
            messages.append({"role": "user", "content": message})

            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )

            response_message = response.choices[0].message

            # Handle function calls
            if response_message.function_call:
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # Execute the function
                if function_name == "get_tickets_by_filters":
                    result = self.get_tickets_by_filters(user_id, function_args.get('filters'))
                elif function_name == "get_friends_attending_match":
                    result = self.get_friends_attending_match(user_id, function_args['match_number'])
                elif function_name == "get_weekend_matches":
                    result = self.get_weekend_matches(function_args['start_date'], function_args['end_date'])
                elif function_name == "get_venue_info":
                    result = self.get_venue_info(function_args.get('venue'))
                elif function_name == "get_user_tickets":
                    result = self.get_user_tickets(user_id)
                elif function_name == "get_match_details":
                    result = self.get_match_details(function_args['match_number'])
                elif function_name == "get_friends_with_tickets_count":
                    result = self.get_friends_with_tickets_count(user_id)
                elif function_name == "get_matches_by_attendance":
                    result = self.get_matches_by_attendance(user_id, function_args.get('ranking_type', 'users'))
                elif function_name == "recommend_matches_by_friends_and_venue":
                    result = self.recommend_matches_by_friends_and_venue(
                        user_id, 
                        function_args.get('preferred_usernames'),
                        function_args.get('preferred_venue')
                    )
                elif function_name == "execute_sql_query":
                    result = self.execute_sql_query(user_id, function_args['question'], conversation_id)
                else:
                    result = {"error": f"Unknown function: {function_name}"}

                # Get final response from OpenAI with function result
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": response_message.function_call.arguments
                    }
                })
                
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(result)
                })

                # Get final response
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return {
                    "content": final_response.choices[0].message.content,
                    "function_called": function_name,
                    "function_result": result
                }
            else:
                return {
                    "content": response_message.content,
                    "function_called": None,
                    "function_result": None
                }

        except Exception as e:
            print(f"Error in process_message: {e}")
            return {
                "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "function_called": None,
                "function_result": None,
                "error": True
            }
