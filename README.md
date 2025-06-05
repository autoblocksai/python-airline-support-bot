# Airline Support Bot 🛫

An AI-powered airline customer support bot that can handle flight-related questions using OpenAI's GPT models with intelligent tool calling.

## Features ✨

- **🤖 AI Tool Calling**: Uses OpenAI's function calling to intelligently choose when to look up flight information
- **Flight Information**: Check real-time flight status, gates, terminals, and schedules
- **Intelligent Conversations**: Natural language processing for customer inquiries
- **Smart Function Selection**: AI automatically decides which tools to use based on customer questions
- **Multi-topic Support**: Handles questions about:
  - Flight schedules and status
  - Booking assistance  
  - Baggage policies
  - Check-in procedures
  - Cancellation and refund policies
  - Special assistance requests
  - Frequent flyer programs
  - General travel information
- **Command Line Interface**: Easy-to-use interactive CLI
- **Programmatic API**: Use the bot in your own applications

## How Tool Calling Works 🛠️

The bot uses OpenAI's function calling feature to intelligently decide when to look up flight information:

- **Automatic Detection**: The AI determines when a customer question requires flight data
- **Smart Tool Selection**: Chooses the appropriate tool (flight lookup, route search, or general info)
- **Contextual Responses**: Combines tool results with natural language responses

### Available AI Tools:

1. **`get_flight_info`**: Look up specific flight details by flight number
2. **`search_flights_by_route`**: Find flights between cities
3. **`get_all_flights`**: List all available flights

## Installation 🚀

### Requirements
- Python 3.12+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-airline-support-bot
   ```

2. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

3. **Set up your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   
   Or create a `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

## Usage 💬

### Interactive Command Line

Run the bot in interactive mode:
```bash
poetry run airline-bot
```

Or using Python directly:
```bash
poetry run python -m python_airline_support_bot.cli
```

### Example Commands in Interactive Mode

```
You: What's the status of flight AA123?
🤖 Bot: I'll look up flight AA123 for you.

Flight AA123:
• Route: New York (JFK) → Los Angeles (LAX)
• Departure: 08:00 AM
• Arrival: 11:30 AM
• Status: On Time
• Terminal: Terminal 4
• Gate: A12

Flight AA123 is currently on time and will be departing from gate A12 in Terminal 4.

You: Can you find flights from New York to Los Angeles?
🤖 Bot: Let me search for flights from New York to Los Angeles.

Found 1 flight(s) from New York to Los Angeles:

Flight AA123:
• Route: New York (JFK) → Los Angeles (LAX)
• Departure: 08:00 AM
• Arrival: 11:30 AM
• Status: On Time
• Terminal: Terminal 4
• Gate: A12

You: What's your baggage policy?
🤖 Bot: I'd be happy to help you with baggage information! For carry-on bags, most airlines allow one personal item and one carry-on bag...
```

### Tool Calling Examples

The AI automatically chooses which tools to use:

| Customer Question | Tool Called | Result |
|-------------------|-------------|---------|
| "What's the status of flight AA123?" | `get_flight_info` | Detailed flight information |
| "Find flights from NYC to LA" | `search_flights_by_route` | List of matching flights |
| "What flights are available?" | `get_all_flights` | All available flights |
| "What's your baggage policy?" | None | General airline information |

### Programmatic Usage

```python
from python_airline_support_bot import AirlineSupportBot

# Initialize the bot
bot = AirlineSupportBot()

# Ask questions - AI will automatically use tools when needed
response = bot.process_message("What's the status of flight AA123?")
print(response)

# The AI will automatically call get_flight_info tool and format the response

# Direct access to public methods is still available
flights = bot.get_available_flights()
for flight in flights:
    print(f"{flight.flight_number}: {flight.status}")
```

### Run Example Script

```bash
poetry run python example_usage.py
```

## Sample Flight Data 📊

The bot comes with sample flight data for demonstration:

| Flight | Route | Status | Gate | Terminal |
|--------|-------|--------|------|----------|
| AA123 | New York (JFK) → Los Angeles (LAX) | On Time | A12 | Terminal 4 |
| DL456 | Chicago (ORD) → Miami (MIA) | Delayed - 30 minutes | B8 | Terminal 1 |
| UA789 | San Francisco (SFO) → Seattle (SEA) | Boarding | C15 | Terminal 3 |
| SW101 | Denver (DEN) → Phoenix (PHX) | Cancelled | - | Terminal West |

## API Reference 📚

### AirlineSupportBot Class

#### Public Methods

- `__init__(api_key: Optional[str] = None)`: Initialize the bot
- `process_message(user_message: str) -> str`: Process a user message and return response (uses AI tool calling)
- `reset_conversation()`: Clear conversation history
- `get_available_flights() -> List[FlightInfo]`: Get all available flights
- `search_flights_by_route(departure_city: str, arrival_city: str) -> List[FlightInfo]`: Search flights

#### AI Tools (Called Automatically)

The AI can automatically call these functions based on user questions:

- `get_flight_info(flight_number: str)`: Look up specific flight details
- `search_flights_by_route(departure_city: str, arrival_city: str)`: Search flights by route
- `get_all_flights()`: Get all available flights

#### FlightInfo Model

```python
class FlightInfo(BaseModel):
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_time: str
    arrival_time: str
    status: str
    gate: Optional[str] = None
    terminal: Optional[str] = None
```

## Development 🛠️

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black python_airline_support_bot/
poetry run isort python_airline_support_bot/
```

### Linting

```bash
poetry run flake8 python_airline_support_bot/
```

## Configuration ⚙️

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)
- `MAX_TOKENS`: Maximum tokens for responses (default: 500)

### Customization

You can extend the bot by:

1. **Adding new tools**: Extend the `_create_tools()` method and `_execute_function()` method
2. **Adding more flight data**: Modify the `_create_sample_flight_data()` method
3. **Connecting to real APIs**: Replace the sample data with calls to airline APIs
4. **Customizing responses**: Modify the system prompt in `_create_system_prompt()`

## Tool Calling Benefits 🎯

The new tool calling approach provides several advantages:

- **🧠 Intelligent**: AI decides when to look up data vs. provide general information
- **⚡ Efficient**: Only makes function calls when necessary
- **🎯 Accurate**: Gets the most up-to-date flight information when needed
- **💬 Natural**: Seamlessly integrates tool results into conversational responses
- **🔧 Extensible**: Easy to add new tools and capabilities

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Support 💭

For questions or issues, please open an issue on GitHub or contact the maintainer.

---

Happy flying! ✈️
