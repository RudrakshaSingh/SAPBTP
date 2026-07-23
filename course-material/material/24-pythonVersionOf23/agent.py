"""The Gemini agent: system instruction plus the call that runs the tools."""

from google.genai import types

from config import MODEL_NAME, client
from tools import AGENT_TOOLS

SYSTEM_INSTRUCTION = """
You are a concise course-support agent for an AI training company.
Use the available tools whenever the user asks about courses, prices,
discount calculations, or order status. Never invent a course, price,
order, or tool result. If a tool returns an error, explain it clearly.
All prices are in Indian rupees. Keep the final response helpful and concise.
""".strip()


def run_agent(message: str) -> str:
    """Send a user message to Gemini with access to the local Python tools."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=AGENT_TOOLS,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
