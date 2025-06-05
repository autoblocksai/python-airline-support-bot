"""
Airline Support Bot - Main bot implementation using OpenAI
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel


class FlightInfo(BaseModel):
    """Model for flight information"""
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_time: str
    arrival_time: str
    status: str
    gate: Optional[str] = None
    terminal: Optional[str] = None


class AirlineSupportBot:
    """
    AI-powered airline support bot that can handle flight-related questions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the airline support bot
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.system_prompt = self._create_system_prompt()
        self.conversation_history = []
        
        # Sample flight data - in a real implementation, this would connect to airline APIs
        self.flight_database = self._create_sample_flight_data()
        
        # Define available tools for the AI
        self.tools = self._create_tools()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the airline support bot"""
        return """You are a helpful airline customer support assistant. You can help customers with:

1. Flight information (schedules, status, gates, terminals)
2. Booking assistance
3. Baggage policies and issues
4. Check-in procedures
5. Cancellation and refund policies
6. Special assistance requests
7. Frequent flyer program questions
8. General travel information

When customers ask about specific flights, use the get_flight_info function to look up current flight details.
When customers want to search for flights between cities, use the search_flights_by_route function.

Be professional, empathetic, and helpful. If you don't have specific information about a flight or policy, let the customer know and suggest they contact the airline directly or check the official website.

When discussing flight information, always provide clear details including flight numbers, times, gates, and status when available.

If a customer seems frustrated, acknowledge their concerns and offer specific solutions or next steps."""

    def _create_tools(self) -> List[Dict[str, Any]]:
        """Create the tool definitions for OpenAI function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_flight_info",
                    "description": "Get detailed information about a specific flight by flight number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "flight_number": {
                                "type": "string",
                                "description": "The flight number to look up (e.g., 'AA123', 'DL456')"
                            }
                        },
                        "required": ["flight_number"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "search_flights_by_route",
                    "description": "Search for flights between specific cities or airports",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "departure_city": {
                                "type": "string",
                                "description": "The departure city or airport code"
                            },
                            "arrival_city": {
                                "type": "string", 
                                "description": "The arrival city or airport code"
                            }
                        },
                        "required": ["departure_city", "arrival_city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_flights",
                    "description": "Get a list of all available flights in the system",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]

    def _create_sample_flight_data(self) -> Dict[str, FlightInfo]:
        """Create sample flight data for demonstration"""
        return {
            "AA123": FlightInfo(
                flight_number="AA123",
                departure_city="New York (JFK)",
                arrival_city="Los Angeles (LAX)",
                departure_time="08:00 AM",
                arrival_time="11:30 AM",
                status="On Time",
                gate="A12",
                terminal="Terminal 4"
            ),
            "DL456": FlightInfo(
                flight_number="DL456", 
                departure_city="Chicago (ORD)",
                arrival_city="Miami (MIA)",
                departure_time="02:15 PM",
                arrival_time="06:45 PM",
                status="Delayed - 30 minutes",
                gate="B8",
                terminal="Terminal 1"
            ),
            "UA789": FlightInfo(
                flight_number="UA789",
                departure_city="San Francisco (SFO)", 
                arrival_city="Seattle (SEA)",
                departure_time="05:20 PM",
                arrival_time="07:40 PM",
                status="Boarding",
                gate="C15",
                terminal="Terminal 3"
            ),
            "SW101": FlightInfo(
                flight_number="SW101",
                departure_city="Denver (DEN)",
                arrival_city="Phoenix (PHX)", 
                departure_time="09:45 AM",
                arrival_time="11:10 AM",
                status="Cancelled",
                gate=None,
                terminal="Terminal West"
            )
        }
    
    def _get_flight_info(self, flight_number: str) -> Optional[FlightInfo]:
        """
        Retrieve flight information by flight number
        
        Args:
            flight_number: The flight number to look up
            
        Returns:
            FlightInfo object if found, None otherwise
        """
        return self.flight_database.get(flight_number.upper())
    
    def _format_flight_info(self, flight: FlightInfo) -> str:
        """Format flight information for display"""
        info = f"""Flight {flight.flight_number}:
• Route: {flight.departure_city} → {flight.arrival_city}
• Departure: {flight.departure_time}
• Arrival: {flight.arrival_time}
• Status: {flight.status}"""
        
        if flight.terminal:
            info += f"\n• Terminal: {flight.terminal}"
        if flight.gate:
            info += f"\n• Gate: {flight.gate}"
            
        return info

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a function call and return the result as a string"""
        try:
            if function_name == "get_flight_info":
                flight_number = arguments.get("flight_number", "")
                flight = self._get_flight_info(flight_number)
                if flight:
                    return self._format_flight_info(flight)
                else:
                    return f"Flight {flight_number} not found in our system. Please verify the flight number or contact customer service."
            
            elif function_name == "search_flights_by_route":
                departure_city = arguments.get("departure_city", "")
                arrival_city = arguments.get("arrival_city", "")
                flights = self.search_flights_by_route(departure_city, arrival_city)
                
                if flights:
                    result = f"Found {len(flights)} flight(s) from {departure_city} to {arrival_city}:\n\n"
                    for flight in flights:
                        result += self._format_flight_info(flight) + "\n\n"
                    return result.strip()
                else:
                    return f"No flights found from {departure_city} to {arrival_city}."
            
            elif function_name == "get_all_flights":
                flights = self.get_available_flights()
                result = f"All available flights ({len(flights)} total):\n\n"
                for flight in flights:
                    result += self._format_flight_info(flight) + "\n\n"
                return result.strip()
            
            else:
                return f"Unknown function: {function_name}"
                
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return a response
        
        Args:
            user_message: The user's message/question
            
        Returns:
            Bot's response
        """
        # Add the user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-10:])  # Keep last 10 exchanges for context
        
        try:
            # First API call with tools
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call any tools
            if response_message.tool_calls:
                # Add the assistant's response to the messages
                messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls
                })
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the function
                    function_result = self._execute_function(function_name, function_args)
                    
                    # Add the function result to the messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result
                    })
                
                # Get the final response after function calls
                final_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                bot_response = final_response.choices[0].message.content
            else:
                # No function calls needed
                bot_response = response_message.content
            
            # Add bot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later or contact customer service directly. Error: {str(e)}"
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
    
    def get_available_flights(self) -> List[FlightInfo]:
        """Get all available flights in the database"""
        return list(self.flight_database.values())
    
    def search_flights_by_route(self, departure_city: str, arrival_city: str) -> List[FlightInfo]:
        """
        Search for flights by departure and arrival cities
        
        Args:
            departure_city: Departure city name
            arrival_city: Arrival city name
            
        Returns:
            List of matching flights
        """
        matching_flights = []
        for flight in self.flight_database.values():
            if (departure_city.lower() in flight.departure_city.lower() and 
                arrival_city.lower() in flight.arrival_city.lower()):
                matching_flights.append(flight)
        return matching_flights 