"""Run the four test cases from section 10 of the problem statement.

Needs a Gemini key:
    copy .env.example to .env, paste your key, then

    python run_demo.py            # all four test cases, auto-approving reviews
    python run_demo.py --ask      # stop and ask you to approve each escalation
"""

from __future__ import annotations

import sys

from support_agent import (
    build_agent,
    format_result,
    run_agent,
    set_approver,
)

TEST_CASES = [
    (
        "SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 "
        "unauthorized error. Employee replication has stopped.",
        "Category: SAP Integration Suite / CPI | Priority: High | Ticket: Yes | Review: Yes",
    ),
    (
        "How can I create a destination in SAP BTP cockpit?",
        "Category: SAP BTP | Priority: Low | Ticket: No | Review: No",
    ),
    (
        "SAP HANA Cloud connection is failing from CAP application.",
        "Category: SAP HANA Cloud / SAP BTP | Priority: Medium | Ticket: No | Review: No",
    ),
    (
        "Production S/4HANA order creation API is down and sales users cannot create orders.",
        "Category: SAP S/4HANA | Priority: High | Ticket: Yes | Review: Yes",
    ),
]

# A second issue on the same thread, to show the checkpointer holding history.
FOLLOW_UP = "The same CPI iFlow is still failing after we rotated the client secret."


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    if "--ask" not in sys.argv:
        set_approver(lambda state: (print("Approve response? yes/no: yes  (--ask to decide yourself)"), True)[1])

    app = build_agent()
    for i, (issue, expected) in enumerate(TEST_CASES, start=1):
        banner(f"Test Case {i}")
        print(f"Expected -> {expected}\n")
        print(format_result(run_agent(issue, app=app)))

    banner("Memory: two issues on one thread")
    remembering = build_agent(memory=True)
    run_agent(TEST_CASES[0][0], app=remembering, thread_id="ticket-4711")
    state = run_agent(FOLLOW_UP, app=remembering, thread_id="ticket-4711")
    print(format_result(state))
    print("\nIssues seen on this thread:")
    for n, past in enumerate(state["history"], start=1):
        print(f"  {n}. {past}")


if __name__ == "__main__":
    main()
