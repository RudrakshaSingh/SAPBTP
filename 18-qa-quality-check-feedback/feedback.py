"""
STEP 7 -- REQUIREMENTS B and C: COLLECT AND SUMMARIZE FEEDBACK

Once the assistant is live, the team wants to know which answers actually helped.
So we let users send a thumbs-up / thumbs-down for an answer and keep a running
tally.

    B) Store a helpful / not-helpful value  -> record()
    C) Summarize helpful vs not helpful      -> summary()

The constraint says a list in memory is fine, so that is exactly what this is --
no database, and it resets when the server restarts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Feedback:
    """One thumbs-up or thumbs-down for the answer to a question."""

    question: str
    helpful: bool


class FeedbackStore:
    """Every piece of feedback received, in the order it arrived."""

    def __init__(self) -> None:
        self._items: List[Feedback] = []

    def record(self, question: str, helpful: bool) -> None:
        """Store one thumbs-up (helpful=True) or thumbs-down (helpful=False)."""
        self._items.append(Feedback(question=question, helpful=helpful))

    def summary(self) -> Dict[str, int]:
        """Totals: how many answers were marked helpful vs not helpful."""
        helpful = sum(1 for f in self._items if f.helpful)
        return {
            "total": len(self._items),
            "helpful": helpful,
            "not_helpful": len(self._items) - helpful,
        }
