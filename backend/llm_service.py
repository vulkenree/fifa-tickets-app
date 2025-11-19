import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from models import db, Ticket, User, Match, ChatMessage
from datetime import datetime, date
import re

class LLMService:
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4"
        else:
            self.client = None
            self.model = "gpt-4"
            print("⚠️  Warning: OPENAI_API_KEY not set. LLM service will return mock responses.")
        
        # System prompt with database schema documentation
        self.system_prompt = """You are an AI assistant for the FIFA 2026 World Cup ticket management system. You help users query their ticket data and get intelligent recommendations.

DATABASE SCHEMA:
- Users: id, username, created_at (NO ACCESS to password_hash)
- Tickets: id, user_id, name, match_number, date, venue, ticket_category, quantity, ticket_info, ticket_price, created_at, updated_at
- Matches: id, match_number, date, venue
- ChatConversations: id, user_id, title, created_at, updated_at, is_saved
- ChatMessages: id, conversation_id, role, content, created_at

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

RESPONSE GUIDELINES:
- Provide clear, helpful answers in English only
- Use natural language, not technical jargon
- When recommending matches, consider friend attendance and venue proximity
- Ask clarifying questions when needed (travel preferences, budget, etc.)
- Be conversational and friendly
- If you can't find specific information, say so clearly

EXAMPLE QUESTIONS YOU CAN HANDLE:
- "Which match do most of my friends have tickets for?"
- "What's a good weekend where my friends have tickets and venues are close together?"
- "Show me all matches in New York that my friends are attending"
- "Which friends are going to Match M50?"
- "Recommend matches where I can meet up with the most friends"
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

    def get_conversation_context(self, conversation_id: int, limit: int = 10) -> List[Dict]:
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
