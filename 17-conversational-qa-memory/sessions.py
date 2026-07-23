"""
STEP 5 -- REQUIREMENT A: ONE CONVERSATION HISTORY PER SESSION

A chatbot has to remember what was said. For each session_id we keep the ordered
list of messages exchanged. The constraint says no external database, so the
"database" is a dict in memory: session_id -> the conversation.

Two rules from the problem statement live here:
  * Each conversation has its own unique session_id      -> new_session()
  * Different sessions must never mix their histories     -> every id owns its
    own list of messages; nothing is shared between them.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Message:
    """One line of the conversation."""

    role: str      # "user" or "assistant"
    content: str


@dataclass
class Session:
    """One conversation: its id and every message so far, oldest first."""

    session_id: str
    messages: List[Message] = field(default_factory=list)


class SessionStore:
    """Every live conversation, keyed by its session_id."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def new_session(self) -> str:
        """Create an empty conversation and return its fresh, unique id."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id=session_id)
        return session_id

    def get(self, session_id: str) -> Optional[Session]:
        """The conversation with this id, or None if it was never created."""
        return self._sessions.get(session_id)

    def add_turn(self, session_id: str, question: str, answer: str) -> None:
        """Append the user question and then the assistant answer, in order."""
        session = self._sessions[session_id]
        session.messages.append(Message(role="user", content=question))
        session.messages.append(Message(role="assistant", content=answer))
