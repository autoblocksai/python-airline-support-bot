import os
from dataclasses import dataclass
from typing import Any
from typing import Dict

from autoblocks.api.app_client import AutoblocksAppClient
from autoblocks.scenarios.models import Message
from autoblocks.scenarios.utils import get_selected_scenario_ids
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

max_turns = 10


@dataclass
class Output:
    messages: list[Dict[str, Any]]


@dataclass
class TestCase(BaseTestCase):
    scenario_id: str

    def hash(self) -> str:
        return self.scenario_id


def run_tests():
    scenarios = client.scenarios.list_scenarios()
    selected_scenario_ids = get_selected_scenario_ids()

    # Filter scenarios if specific ones are selected
    if selected_scenario_ids:
        scenarios = [scenario for scenario in scenarios if scenario.id in selected_scenario_ids]

    test_cases = [
        TestCase(
            scenario_id=scenario.id,
        )
        for scenario in scenarios
    ]

    async def test_fn(test_case: TestCase) -> Output:
        turn = 1
        bot = AirlineSupportBot()
        while turn < max_turns:
            all_messages = [
                Message(role=message["role"], content=message["content"]) for message in bot.conversation_history
            ]
            next_message = client.scenarios.generate_message(scenario_id=test_case.scenario_id, messages=all_messages)
            bot.process_message(next_message.message)
            if next_message.is_final_message:
                break
            turn += 1
        return Output(messages=bot.conversation_history)

    run_test_suite(
        id="airline-support-bot",
        app_slug="airline-support-bot",
        test_cases=test_cases,
        fn=test_fn,
        evaluators=[],
    )
