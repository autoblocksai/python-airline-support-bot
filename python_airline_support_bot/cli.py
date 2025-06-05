"""
Command-line interface for the Airline Support Bot
"""

import os
import click
from dotenv import load_dotenv
from .bot import AirlineSupportBot


def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()


@click.command()
@click.option('--api-key', help='OpenAI API key (or set OPENAI_API_KEY environment variable)')
@click.option('--interactive/--no-interactive', default=True, help='Run in interactive mode')
def main(api_key, interactive):
    """
    Airline Support Bot - AI-powered customer service assistant for flight-related questions
    """
    load_environment()
    
    # Check for API key
    if not api_key and not os.getenv('OPENAI_API_KEY'):
        click.echo("❌ Error: OpenAI API key is required!")
        click.echo("Set it using --api-key option or OPENAI_API_KEY environment variable")
        return
    
    # Initialize the bot
    try:
        bot = AirlineSupportBot(api_key=api_key)
        click.echo("✈️  Airline Support Bot initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Error initializing bot: {e}")
        return
    
    if interactive:
        run_interactive_mode(bot)
    else:
        click.echo("Non-interactive mode not yet implemented. Use --interactive flag.")


def run_interactive_mode(bot: AirlineSupportBot):
    """Run the bot in interactive mode"""
    click.echo("\n" + "="*60)
    click.echo("🤖 Welcome to the Airline Support Bot!")
    click.echo("I can help you with flight information, bookings, and general travel questions.")
    click.echo("Type 'quit', 'exit', or 'bye' to end the conversation.")
    click.echo("Type 'help' to see available sample flight numbers.")
    click.echo("="*60 + "\n")
    
    while True:
        try:
            user_input = click.prompt("You", type=str)
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                click.echo("\n🛫 Thank you for using Airline Support Bot! Have a great flight!")
                break
            elif user_input.lower() == 'help':
                show_help(bot)
                continue
            elif user_input.lower() == 'clear':
                bot.reset_conversation()
                click.echo("💭 Conversation history cleared!")
                continue
            
            # Process the message
            response = bot.process_message(user_input)
            click.echo(f"\n🤖 Bot: {response}\n")
            
        except KeyboardInterrupt:
            click.echo("\n\n🛫 Thank you for using Airline Support Bot! Have a great flight!")
            break
        except Exception as e:
            click.echo(f"\n❌ Error: {e}\n")


def show_help(bot: AirlineSupportBot):
    """Show help information and sample flight numbers"""
    click.echo("\n📋 Help Information:")
    click.echo("• Ask about specific flights using flight numbers")
    click.echo("• Inquire about baggage policies, check-in procedures, etc.")
    click.echo("• Request general travel information")
    click.echo("• Type 'clear' to reset conversation history")
    
    click.echo("\n✈️  Sample Flight Numbers to try:")
    flights = bot.get_available_flights()
    for flight in flights:
        status_emoji = "🟢" if "On Time" in flight.status else "🟡" if "Delayed" in flight.status else "🔴" if "Cancelled" in flight.status else "🔵"
        click.echo(f"• {flight.flight_number} - {flight.departure_city} → {flight.arrival_city} {status_emoji}")
    
    click.echo("\n💡 Example questions:")
    click.echo("• 'What's the status of flight AA123?'")
    click.echo("• 'Can you help me with baggage allowance?'")
    click.echo("• 'How do I check in online?'")
    click.echo("• 'What are your cancellation policies?'")
    click.echo()


@click.group()
def cli():
    """Airline Support Bot CLI"""
    pass


@cli.command()
def demo():
    """Run a quick demo of the bot"""
    load_environment()
    
    if not os.getenv('OPENAI_API_KEY'):
        click.echo("❌ Error: OPENAI_API_KEY environment variable is required for demo!")
        return
    
    try:
        bot = AirlineSupportBot()
        click.echo("🚀 Running Airline Support Bot Demo...\n")
        
        # Demo questions
        demo_questions = [
            "What's the status of flight AA123?",
            "Can you tell me about baggage policies?",
            "How do I check in online?",
        ]
        
        for question in demo_questions:
            click.echo(f"👤 Customer: {question}")
            response = bot.process_message(question)
            click.echo(f"🤖 Bot: {response}\n")
            click.echo("-" * 50 + "\n")
            
    except Exception as e:
        click.echo(f"❌ Demo failed: {e}")


if __name__ == '__main__':
    main() 