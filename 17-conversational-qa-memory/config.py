"""
STEP 1 -- SETTINGS

load_dotenv() reads the .env file so os.getenv() can find your API key.
Without this line the key is invisible and every Gemini call fails.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# The problem statement lists gemini-2.5-flash; we use the newer flash-lite.
# Either works -- override with GEMINI_CHAT_MODEL in .env to switch.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

# Chunk size in characters. Small enough that each policy section (Annual Leave,
# Carry Forward, Sick Leave, ...) becomes its own chunk, so retrieval can pick
# the one relevant section and cite the single document it came from -- rather
# than swallowing a whole file as one chunk and always citing everything.
CHUNK_SIZE = 300
CHUNK_OVERLAP = 60    # so a sentence on a boundary survives whole in one chunk

TOP_K = 3             # how many chunks we hand to Gemini per question

# How many past messages the follow-up rewriter is allowed to look at. Enough
# to resolve an "it" or a "them"; capped so the rewrite prompt stays small.
MAX_HISTORY_MESSAGES = 6

# One fixed sentence for "not in the documents", so we can recognise it in code.
FALLBACK = "The information is not available in the provided documents."
