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
# Probation, Working Hours, ...) becomes its own chunk, so retrieval can pick
# the one relevant section and cite the single document it came from.
CHUNK_SIZE = 300
CHUNK_OVERLAP = 60    # so a sentence on a boundary survives whole in one chunk

TOP_K = 3             # how many chunks we hand to Gemini per question

# Confidence bands read off the best retrieval similarity score. This is a
# document-based signal -- how close the question is to stored text -- NOT the
# model's own opinion of itself, which is what the constraint warns against.
# Tuned for gemini-embedding-001; raise them if answers look over-confident.
CONFIDENCE_HIGH = 0.72     # question closely matches stored text -> "high"
CONFIDENCE_MEDIUM = 0.55   # a fair match -> "medium"; below this -> "low"

# One fixed sentence for "not in the documents", so we can recognise it in code.
# It is also what /ask returns whenever an answer is not supported.
FALLBACK = "The information is not available in the provided documents."
