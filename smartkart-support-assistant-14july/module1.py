"""Module 1 — Connect LangChain with Google Gemini.

Run:  python module1.py
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Reads .env into the process environment. The key itself never appears in code.
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not set. Paste your key into the .env file "
        "(get one at https://aistudio.google.com/apikey)."
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    # Low temperature: a support bot should be factual and consistent,
    # not creative. 0.0-0.3 is the right band here.
    temperature=0.2,
    google_api_key=GOOGLE_API_KEY,
)


if __name__ == "__main__":
    print("API key loaded:", GOOGLE_API_KEY[:6] + "..." + GOOGLE_API_KEY[-4:])

    response = llm.invoke("Explain customer-support automation in three sentences.")

    # Use .text, not .content — Gemini 3.x returns .content as a list of
    # content blocks, while .text gives the plain string.
    print("\nAnswer:\n" + response.text)

    print("\ntype:      ", type(response).__name__)
    print("tool_calls:", response.tool_calls)  # empty — no tools bound yet
    print("tokens:    ", response.usage_metadata)
