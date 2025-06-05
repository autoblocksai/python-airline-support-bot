import os
from dataclasses import dataclass

from autoblocks.api.app_client import AutoblocksAppClient
from autoblocks.testing.models import BaseTestCase
from autoblocks.testing.v2.run import run_test_suite
from autoblocks.tracer import init_auto_tracer
from dotenv import load_dotenv
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

from python_airline_support_bot.bot import AirlineSupportBot

load_dotenv()
init_auto_tracer(api_key=os.getenv("AUTOBLOCKS_V2_API_KEY"), is_batch_disabled=True)
OpenAIInstrumentor().instrument()

client = AutoblocksAppClient(
    app_slug="airline-support-bot",
)


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Output:
    messages: list[Message]


@dataclass
class TestCase(BaseTestCase):
    scenario_id: str
    user_messages: list[str]

    def hash(self) -> str:
        return self.scenario_id


def run_tests():
    test_cases = [
        TestCase(scenario_id="1", user_messages=["What is the status of flight AA123?"]),
        TestCase(scenario_id="2", user_messages=["What is the status of flight DL456?"]),
        TestCase(scenario_id="3", user_messages=["What is the status of flight AA123?"]),
    ]

    async def test_fn(test_case: TestCase) -> Output:
        bot = AirlineSupportBot()
        for user_message in test_case.user_messages:
            bot.process_message(user_message)
        return Output(messages=bot.conversation_history)

    run_test_suite(
        id="airline-support-bot",
        app_slug="airline-support-bot",
        test_cases=test_cases,
        fn=test_fn,
        evaluators=[],
    )
