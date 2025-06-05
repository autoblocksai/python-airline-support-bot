"""
Python Airline Support Bot

An AI-powered airline support bot that can handle flight-related questions using OpenAI.
"""

from .bot import AirlineSupportBot
from .bot import FlightInfo
from .cli import cli
from .cli import main

__version__ = "0.1.0"
__all__ = ["AirlineSupportBot", "FlightInfo", "main", "cli"]
