#!/usr/bin/env python3
"""
Example usage of the Airline Support Bot with Tool Calling

This script demonstrates how to use the AirlineSupportBot class programmatically
with the new OpenAI tool calling functionality.
Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import os
from python_airline_support_bot import AirlineSupportBot


def main():
    """Example usage of the airline support bot with tool calling"""
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: Please set your OPENAI_API_KEY environment variable")
        print("You can get an API key from: https://platform.openai.com/api-keys")
        return
    
    # Initialize the bot
    print("🚀 Initializing Airline Support Bot with Tool Calling...")
    bot = AirlineSupportBot()
    
    # Example conversation demonstrating tool calling
    print("\n" + "="*60)
    print("📞 Customer Service Simulation with AI Tool Calling")
    print("="*60)
    
    # Sample questions that will trigger different tool calls
    questions = [
        # This should trigger get_flight_info tool
        "What's the status of flight AA123?",
        
        # This should trigger search_flights_by_route tool
        "Can you find flights from New York to Los Angeles?",
        
        # This should trigger get_all_flights tool
        "What flights do you have available today?",
        
        # This should NOT trigger any tools (general question)
        "What's your baggage policy?",
        
        # This should trigger get_flight_info tool
        "Is flight DL456 delayed?",
        
        # This should trigger search_flights_by_route tool
        "Show me flights from San Francisco to Seattle",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n🧑 Customer {i}: {question}")
        print("🤖 Processing with AI tool calling...")
        
        response = bot.process_message(question)
        print(f"🤖 Support Bot: {response}")
        print("-" * 50)
    
    print("\n✅ Tool calling demonstration completed!")
    
    # Show available tools
    print("\n🛠️ Available AI Tools:")
    for tool in bot.tools:
        function = tool["function"]
        print(f"• {function['name']}: {function['description']}")
    
    # Show flight database
    print("\n📊 Available Flight Information:")
    flights = bot.get_available_flights()
    for flight in flights:
        print(f"• {flight.flight_number}: {flight.departure_city} → {flight.arrival_city} ({flight.status})")
    
    print("\n💡 The AI automatically chooses which tools to use based on the customer's question!")
    print("This makes the bot much more intelligent and responsive to specific requests.")


if __name__ == "__main__":
    main() 