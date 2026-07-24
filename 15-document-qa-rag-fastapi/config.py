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

# Chunk size in characters. Too big and one chunk holds five unrelated rules;
# too small and a rule gets cut in half. Policy documents are written in short
# paragraphs, so ~800 characters keeps one rule (leave entitlement, notice
# period) inside a single chunk.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120   # so a sentence on a boundary survives whole in one chunk

TOP_K = 3             # how many chunks we hand to Gemini per question

# The three sample HR documents are embedded at startup so /ask answers straight
# away. Set SEED_SAMPLE_DOCS=false in .env to start with an empty store instead
# and ingest your own documents through /ingest.
SEED_SAMPLE_DOCS = os.getenv("SEED_SAMPLE_DOCS", "true").lower() not in {
    "false",
    "0",
    "no",
}

# One fixed sentence for "not in the documents", so we can recognise it in code.
FALLBACK = "The information is not available in the provided documents."
