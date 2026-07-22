"""Mock SAP back-end tools the support agent can call.

Three plain Python functions stand in for the systems a real SAP support desk
would query:

1.  ``search_kb``             -- keyword search over a small troubleshooting KB.
2.  ``check_system_status``   -- availability of CPI / SuccessFactors / S4HANA / HANA / BTP.
3.  ``create_support_ticket`` -- books an incident and returns its ticket ID.

They are ordinary functions so graph nodes can call them directly. The bottom of
the file also wraps them as LangChain tools (``SAP_TOOLS``) for the advanced
challenge, where Gemini picks the tool itself via ``ToolNode``.
"""

from __future__ import annotations

import itertools
import re
from datetime import date
from functools import lru_cache
from typing import Dict, List, Tuple

from langchain_core.tools import tool as as_tool

# --------------------------------------------------------------------------- #
# Knowledge base
# --------------------------------------------------------------------------- #

# Topic -> troubleshooting steps. This is the "documentation" the agent reads.
SAP_KB: Dict[str, str] = {
    "401 unauthorized": (
        "Check destination credentials, OAuth token, client secret, role collection, "
        "and OData authentication."
    ),
    "cpi failure": (
        "Check CPI message monitoring, iFlow deployment status, certificates, "
        "and adapter configuration."
    ),
    "successfactors replication": (
        "Check employee replication job, middleware mapping, Compound Employee API, "
        "and permissions."
    ),
    "hana connection": (
        "Check HANA Cloud endpoint, IP allowlist, user privileges, and HDI container binding."
    ),
    "btp destination": (
        "In the BTP cockpit open Connectivity > Destinations, create the destination with "
        "URL, proxy type and authentication, then run 'Check Connection'."
    ),
    "s4hana api": (
        "Check the OData service in /IWFND/MAINT_SERVICE, the gateway error log "
        "/IWFND/ERROR_LOG, background jobs, and current system load."
    ),
}

# Trigger words per topic. Kept separate from SAP_KB so the article text stays
# readable -- matching is a lookup concern, not part of the documentation.
KB_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "401 unauthorized": (
        "401", "403", "unauthorized", "unauthorised", "forbidden",
        "authentication", "credential", "token", "oauth", "certificate expired",
    ),
    "cpi failure": (
        "cpi", "integration suite", "iflow", "i-flow", "cloud integration",
        "adapter", "message mapping", "middleware",
    ),
    "successfactors replication": (
        "successfactors", "employee replication", "employee data", "compound employee",
        "ec payroll", "hcm",
    ),
    "hana connection": (
        "hana", "hdi", "database connection", "cap application", "cds",
    ),
    "btp destination": (
        "destination", "btp cockpit", "connectivity", "subaccount", "role collection",
    ),
    "s4hana api": (
        "s/4hana", "s4hana", "s4 hana", "s/4 hana", "odata", "gateway",
        "order creation", "bapi", "idoc",
    ),
}

MAX_KB_HITS = 3

# --------------------------------------------------------------------------- #
# Mock system landscape
# --------------------------------------------------------------------------- #

# Flip any value to "Degraded" or "Down" to watch the agent's draft response
# start blaming the platform instead of the configuration.
MOCK_STATUS: Dict[str, str] = {
    "CPI": "Running",
    "SuccessFactors": "Running",
    "S4HANA": "Running",
    "HANA": "Running",
    "BTP": "Running",
}

# Every spelling a user might type, mapped onto a MOCK_STATUS key.
SYSTEM_ALIASES: Dict[str, str] = {
    "cpi": "CPI",
    "integration suite": "CPI",
    "cloud integration": "CPI",
    "iflow": "CPI",
    "successfactors": "SuccessFactors",
    "employee central": "SuccessFactors",
    "s4hana": "S4HANA",
    "s/4hana": "S4HANA",
    "s4 hana": "S4HANA",
    "s/4 hana": "S4HANA",
    "ecc": "S4HANA",
    "hana": "HANA",
    "hana cloud": "HANA",
    "hdi": "HANA",
    "btp": "BTP",
    "business technology platform": "BTP",
    "cockpit": "BTP",
}

_TICKET_SEQ = itertools.count(1)


@lru_cache(maxsize=None)
def _pattern(phrase: str) -> re.Pattern:
    """Whole-word matcher for one keyword.

    Plain ``in`` matching is what makes "S/4HANA" look like a HANA Cloud issue
    and "Salesforce" look like SuccessFactors. Word boundaries stop both: in
    "s/4hana" the "hana" sits directly after the word character "4", so no
    boundary exists there, while "HANA Cloud" still matches.
    """
    return re.compile(rf"\b{re.escape(phrase)}\b")


def mentions(text: str, phrase: str) -> bool:
    """True when ``phrase`` appears in ``text`` as a whole word."""
    return _pattern(phrase.lower()).search(text.lower()) is not None


# --------------------------------------------------------------------------- #
# Tool 1 -- knowledge base search
# --------------------------------------------------------------------------- #
def search_kb(query: str) -> str:
    """Search the SAP support knowledge base and return troubleshooting steps.

    Scores every article by how many of its trigger words appear in the query and
    returns the best matches, so a single sentence mentioning both CPI and a 401
    pulls back both articles.
    """
    scored = [
        (sum(mentions(query, word) for word in words), rank, topic)
        for rank, (topic, words) in enumerate(KB_KEYWORDS.items())
    ]
    # Best score first; ties keep SAP_KB order rather than falling back to
    # alphabetical, so the same query always returns the same article order.
    hits = sorted((s for s in scored if s[0] > 0), key=lambda s: (-s[0], s[1]))[:MAX_KB_HITS]

    if not hits:
        return "No knowledge base article matched. Handle as a new issue and document the fix."

    return "\n".join(f"[{topic}] {SAP_KB[topic]}" for _, _, topic in hits)


# --------------------------------------------------------------------------- #
# Tool 2 -- system status
# --------------------------------------------------------------------------- #
def check_system_status(system_name: str) -> str:
    """Return the mock availability of one SAP system, e.g. ``CPI = Running``."""
    key = SYSTEM_ALIASES.get(system_name.strip().lower())
    if key is None:
        # Longest alias first, so "s/4hana" is settled before bare "hana".
        key = next(
            (
                SYSTEM_ALIASES[alias]
                for alias in sorted(SYSTEM_ALIASES, key=len, reverse=True)
                if mentions(system_name, alias)
            ),
            None,
        )
    if key is None:
        return f"{system_name} = Unknown system"
    return f"{key} = {MOCK_STATUS[key]}"


def detect_systems(text: str) -> List[str]:
    """Return the MOCK_STATUS keys mentioned in free text, longest alias first.

    Longest-first matching stops "hana" inside "s/4hana" from registering HANA
    Cloud when the user only ever mentioned S/4HANA.
    """
    lowered = text.lower()
    found: List[str] = []
    for alias in sorted(SYSTEM_ALIASES, key=len, reverse=True):
        matched, count = _pattern(alias).subn(" ", lowered)
        if count:
            lowered = matched  # consumed, so a shorter alias cannot re-match it
            system = SYSTEM_ALIASES[alias]
            if system not in found:
                found.append(system)
    return found


# --------------------------------------------------------------------------- #
# Tool 3 -- ticket creation
# --------------------------------------------------------------------------- #
def create_support_ticket(summary: str, priority: str) -> str:
    """Create a mock support ticket and return its ticket ID."""
    band = {"high": "P1", "medium": "P2", "low": "P3"}.get(priority.strip().lower(), "P3")
    ticket_id = f"INC-{date.today():%Y%m%d}-{band}-{next(_TICKET_SEQ):03d}"
    print(f"[ticket] {ticket_id} raised ({priority}): {summary[:70].strip()}...")
    return ticket_id


# --------------------------------------------------------------------------- #
# LangChain tool objects -- for the ToolNode / tools_condition challenge
# --------------------------------------------------------------------------- #
SAP_TOOLS = [as_tool(search_kb), as_tool(check_system_status), as_tool(create_support_ticket)]
