"""Root entry point for the Resume-to-Job Match Assistant.

Needs a Gemini key: copy .env.example to .env and paste your key, then

    python app.py                                   # all three job descriptions
    python app.py --jd 1                            # only the first one
    python app.py --resume my_cv.txt --jd-file jd.txt   # your own files
    python app.py --memory                          # one thread, three roles
    python app.py --graph                           # print the graph as Mermaid
"""

from __future__ import annotations

import argparse
from pathlib import Path

from job_match_agent import branch_taken, build_agent, format_report, print_graph, run_agent
from sample_data import JOB_DESCRIPTIONS, SAMPLE_RESUME


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def screen_samples(which: int | None) -> None:
    """Run the built-in resume against one or all of the sample job descriptions."""
    jobs = JOB_DESCRIPTIONS if which is None else [JOB_DESCRIPTIONS[which - 1]]

    app = build_agent()
    results = []
    for label, jd in jobs:
        banner(f"Screening against: {label}")
        state = run_agent(SAMPLE_RESUME, jd, app=app)
        print(format_report(state))
        results.append((label, state))

    if len(results) > 1:
        banner("Same resume, three roles")
        print(f"{'Role':<26}{'Score':<8}{'Fit Level':<24}Branch taken")
        print("-" * 78)
        for label, state in results:
            print(
                f"{label:<26}{str(state['fit_score']) + '/100':<8}"
                f"{state['fit_level']:<24}{branch_taken(state)}"
            )


def screen_files(resume_path: str, jd_path: str) -> None:
    """Screen a resume file against a job description file."""
    resume = Path(resume_path).read_text(encoding="utf-8")
    jd = Path(jd_path).read_text(encoding="utf-8")
    banner(f"Screening {Path(resume_path).name} against {Path(jd_path).name}")
    print(format_report(run_agent(resume, jd)))


def screen_on_one_thread() -> None:
    """All three roles on one thread, so the checkpointer keeps the history."""
    banner("Memory: three roles on one thread")
    app = build_agent(memory=True)
    state = {}
    for _, jd in JOB_DESCRIPTIONS:
        state = run_agent(SAMPLE_RESUME, jd, app=app, thread_id="candidate-prem")
        print(f"  {state['parsed_jd']['job_title']:<26}{state['fit_score']}/100")

    print("\nRoles screened on thread candidate-prem:")
    for n, role in enumerate(state["history"], start=1):
        print(f"  {n}. {role}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jd", type=int, choices=[1, 2, 3], help="run only this sample job")
    parser.add_argument("--resume", help="path to your own resume text file")
    parser.add_argument("--jd-file", help="path to your own job description text file")
    parser.add_argument("--memory", action="store_true", help="keep all roles on one thread")
    parser.add_argument("--graph", action="store_true", help="print the graph and exit")
    args = parser.parse_args()

    if args.graph:
        print_graph()
    elif args.resume or args.jd_file:
        if not (args.resume and args.jd_file):
            parser.error("--resume and --jd-file must be given together")
        screen_files(args.resume, args.jd_file)
    elif args.memory:
        screen_on_one_thread()
    else:
        screen_samples(args.jd)


if __name__ == "__main__":
    main()
