import json
import os

from autoblocks.testing.models import BaseTestEvaluator
from autoblocks.testing.models import Evaluation
from autoblocks.testing.models import Threshold
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Initialize async OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Base evaluator with shared logic
class BaseConversationEvaluator(BaseTestEvaluator):
    def __init__(self, criterion_key: str, criterion_description: str):
        self.criterion_key = criterion_key
        self.criterion_description = criterion_description

    async def evaluate_test_case(self, test_case, output) -> Evaluation:
        # Format the conversation for evaluation
        conversation_text = ""
        for msg in output.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{role.upper()}: {content}\n"

        # Define the evaluation function schema for this specific criterion
        evaluation_function = {
            "name": f"evaluate_{self.criterion_key}",
            "description": f"Evaluate {self.criterion_key} in an airline customer support conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    self.criterion_key: {
                        "type": "string",
                        "enum": ["poor", "fair", "good", "excellent"],
                        "description": self.criterion_description,
                    },
                    "reason": {
                        "type": "string",
                        "description": f"Provide a brief explanation for why you rated {self.criterion_key} as you did, including specific examples from the conversation",  # noqa: E501
                    },
                },
                "required": [self.criterion_key, "reason"],
            },
        }

        # Create evaluation prompt
        evaluation_prompt = f"""
You are an expert evaluator of airline customer support conversations.
Please evaluate the following conversation focusing specifically on {self.criterion_key}.

Criterion: {self.criterion_description}

Conversation:
{conversation_text}

Please evaluate this specific criterion and call the evaluation function with your assessment.
"""

        try:
            # Call OpenAI API with function calling (async)
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": evaluation_prompt}],
                tools=[{"type": "function", "function": evaluation_function}],
                tool_choice={"type": "function", "function": {"name": f"evaluate_{self.criterion_key}"}},
                temperature=0.1,
            )

            # Parse the function call response
            function_call = response.choices[0].message.tool_calls[0].function
            evaluation_data = json.loads(function_call.arguments)

            # Map evaluation categories to scores
            score_mapping = {"poor": 0, "fair": 0.25, "good": 0.75, "excellent": 1.0}

            # Get the score for this specific criterion
            criterion_value = evaluation_data.get(self.criterion_key, "fair")
            score = score_mapping.get(criterion_value, 0)
            reason = evaluation_data.get("reason", "No reason provided")

        except Exception as e:
            print(f"Error in LLM evaluation for {self.criterion_key}: {e}")
            score = 0
            reason = f"Evaluation failed: {str(e)}"

        return Evaluation(
            score=score,
            threshold=Threshold(
                gte=0.75,
            ),
            metadata={"reason": reason},
        )


class Helpfulness(BaseConversationEvaluator):
    id = "helpfulness"

    def __init__(self):
        super().__init__("helpfulness", "How helpful was the bot in providing useful information and assistance?")


class Accuracy(BaseConversationEvaluator):
    id = "accuracy"

    def __init__(self):
        super().__init__("accuracy", "Were the responses factually correct and relevant?")


class Professionalism(BaseConversationEvaluator):
    id = "professionalism"

    def __init__(self):
        super().__init__("professionalism", "Was the tone appropriate and professional?")


class ProblemResolution(BaseConversationEvaluator):
    id = "problem_resolution"

    def __init__(self):
        super().__init__("problem_resolution", "Did the bot effectively address the customer's concerns?")


class CommunicationClarity(BaseConversationEvaluator):
    id = "communication_clarity"

    def __init__(self):
        super().__init__("communication_clarity", "Were the responses clear and easy to understand?")
