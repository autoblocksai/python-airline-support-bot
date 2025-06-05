"""
Tests for the Airline Support Bot
"""

from unittest.mock import Mock
from unittest.mock import patch

from python_airline_support_bot.bot import AirlineSupportBot
from python_airline_support_bot.bot import FlightInfo


class TestFlightInfo:
    """Test the FlightInfo model"""

    def test_flight_info_creation(self):
        """Test creating a FlightInfo instance"""
        flight = FlightInfo(
            flight_number="AA123",
            departure_city="New York (JFK)",
            arrival_city="Los Angeles (LAX)",
            departure_time="08:00 AM",
            arrival_time="11:30 AM",
            status="On Time",
            gate="A12",
            terminal="Terminal 4",
        )

        assert flight.flight_number == "AA123"
        assert flight.departure_city == "New York (JFK)"
        assert flight.arrival_city == "Los Angeles (LAX)"
        assert flight.status == "On Time"
        assert flight.gate == "A12"
        assert flight.terminal == "Terminal 4"


class TestAirlineSupportBot:
    """Test the AirlineSupportBot class"""

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_bot_initialization(self, mock_openai):
        """Test bot initialization"""
        bot = AirlineSupportBot(api_key="test-key")
        assert bot is not None
        assert len(bot.flight_database) > 0
        assert bot.conversation_history == []
        assert len(bot.tools) == 3  # Check that tools are defined
        mock_openai.assert_called_once()

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_get_flight_info(self, mock_openai):
        """Test getting flight information"""
        bot = AirlineSupportBot(api_key="test-key")

        # Test existing flight
        flight = bot._get_flight_info("AA123")
        assert flight is not None
        assert flight.flight_number == "AA123"
        assert flight.departure_city == "New York (JFK)"

        # Test non-existing flight
        flight = bot._get_flight_info("XX999")
        assert flight is None

        # Test case insensitive
        flight = bot._get_flight_info("aa123")
        assert flight is not None
        assert flight.flight_number == "AA123"

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_get_available_flights(self, mock_openai):
        """Test getting all available flights"""
        bot = AirlineSupportBot(api_key="test-key")
        flights = bot.get_available_flights()

        assert len(flights) > 0
        assert all(isinstance(flight, FlightInfo) for flight in flights)

        # Check that we have our expected sample flights
        flight_numbers = [flight.flight_number for flight in flights]
        assert "AA123" in flight_numbers
        assert "DL456" in flight_numbers
        assert "UA789" in flight_numbers
        assert "SW101" in flight_numbers

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_search_flights_by_route(self, mock_openai):
        """Test searching flights by route"""
        bot = AirlineSupportBot(api_key="test-key")

        # Search for flights from New York
        ny_flights = bot.search_flights_by_route("New York", "")
        assert len(ny_flights) > 0
        assert all("New York" in flight.departure_city for flight in ny_flights)

        # Search for flights to Los Angeles
        la_flights = bot.search_flights_by_route("", "Los Angeles")
        assert len(la_flights) > 0
        assert all("Los Angeles" in flight.arrival_city for flight in la_flights)

        # Search for specific route
        specific_flights = bot.search_flights_by_route("New York", "Los Angeles")
        assert len(specific_flights) > 0
        for flight in specific_flights:
            assert "New York" in flight.departure_city
            assert "Los Angeles" in flight.arrival_city

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_format_flight_info(self, mock_openai):
        """Test flight information formatting"""
        bot = AirlineSupportBot(api_key="test-key")
        flight = bot._get_flight_info("AA123")

        formatted = bot._format_flight_info(flight)

        assert "Flight AA123" in formatted
        assert "New York (JFK)" in formatted
        assert "Los Angeles (LAX)" in formatted
        assert "08:00 AM" in formatted
        assert "11:30 AM" in formatted
        assert "On Time" in formatted
        assert "Terminal 4" in formatted
        assert "Gate A12" in formatted

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_reset_conversation(self, mock_openai):
        """Test conversation reset"""
        bot = AirlineSupportBot(api_key="test-key")

        # Add some conversation history
        bot.conversation_history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]

        assert len(bot.conversation_history) == 2

        bot.reset_conversation()
        assert len(bot.conversation_history) == 0

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_execute_function_get_flight_info(self, mock_openai):
        """Test executing the get_flight_info function"""
        bot = AirlineSupportBot(api_key="test-key")

        # Test existing flight
        result = bot._execute_function("get_flight_info", {"flight_number": "AA123"})
        assert "Flight AA123" in result
        assert "New York (JFK)" in result
        assert "Los Angeles (LAX)" in result

        # Test non-existing flight
        result = bot._execute_function("get_flight_info", {"flight_number": "XX999"})
        assert "not found" in result
        assert "XX999" in result

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_execute_function_search_flights(self, mock_openai):
        """Test executing the search_flights_by_route function"""
        bot = AirlineSupportBot(api_key="test-key")

        # Test search with results
        result = bot._execute_function(
            "search_flights_by_route", {"departure_city": "New York", "arrival_city": "Los Angeles"}
        )
        assert "Found" in result
        assert "AA123" in result

        # Test search with no results
        result = bot._execute_function(
            "search_flights_by_route", {"departure_city": "NonExistent", "arrival_city": "City"}
        )
        assert "No flights found" in result

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_execute_function_get_all_flights(self, mock_openai):
        """Test executing the get_all_flights function"""
        bot = AirlineSupportBot(api_key="test-key")

        result = bot._execute_function("get_all_flights", {})
        assert "All available flights" in result
        assert "AA123" in result
        assert "DL456" in result
        assert "UA789" in result
        assert "SW101" in result

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_execute_function_unknown(self, mock_openai):
        """Test executing an unknown function"""
        bot = AirlineSupportBot(api_key="test-key")

        result = bot._execute_function("unknown_function", {})
        assert "Unknown function" in result

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_process_message_without_tool_calls(self, mock_openai):
        """Test processing message that doesn't require tool calls"""
        # Mock the OpenAI response without tool calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I can help you with flight information."
        mock_response.choices[0].message.tool_calls = None

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        bot = AirlineSupportBot(api_key="test-key")

        response = bot.process_message("Hello, can you help me?")

        # Check that OpenAI was called once (no function calls)
        assert mock_client.chat.completions.create.call_count == 1

        # Check that conversation history was updated
        assert len(bot.conversation_history) == 2  # user message + bot response
        assert bot.conversation_history[0]["role"] == "user"
        assert bot.conversation_history[1]["role"] == "assistant"

        # Check the response
        assert response == "I can help you with flight information."

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_process_message_with_tool_calls(self, mock_openai):
        """Test processing message that requires tool calls"""
        # Mock tool call object
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_flight_info"
        mock_tool_call.function.arguments = '{"flight_number": "AA123"}'

        # Mock first response with tool calls
        mock_first_response = Mock()
        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]

        # Mock final response after tool calls
        mock_final_response = Mock()
        mock_final_response.choices = [Mock()]
        mock_final_response.choices[0].message.content = "Flight AA123 is on time and departing from gate A12."

        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [mock_first_response, mock_final_response]
        mock_openai.return_value = mock_client

        bot = AirlineSupportBot(api_key="test-key")

        response = bot.process_message("What's the status of flight AA123?")

        # Check that OpenAI was called twice (initial + after function call)
        assert mock_client.chat.completions.create.call_count == 2

        # Check the response
        assert response == "Flight AA123 is on time and departing from gate A12."

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_process_message_api_error(self, mock_openai):
        """Test handling API errors gracefully"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        bot = AirlineSupportBot(api_key="test-key")
        response = bot.process_message("Hello")

        assert "technical difficulties" in response.lower()
        assert "API Error" in response

    @patch("python_airline_support_bot.bot.OpenAI")
    def test_tools_definition(self, mock_openai):
        """Test that tools are properly defined"""
        bot = AirlineSupportBot(api_key="test-key")

        assert len(bot.tools) == 3

        # Check tool names
        tool_names = [tool["function"]["name"] for tool in bot.tools]
        assert "get_flight_info" in tool_names
        assert "search_flights_by_route" in tool_names
        assert "get_all_flights" in tool_names

        # Check that all tools have required structure
        for tool in bot.tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
