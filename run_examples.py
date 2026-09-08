"""Run the test questions and write a readable trace for each to logs/.

Six questions: four that should succeed (one of them requiring two tool
calls) and two chosen to fail in different ways.
"""

import json
import os

from agent import run_agent

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

# (question, log filename). Names are fixed so reruns overwrite cleanly and
# the submission always has the files the spec asks for.
CASES = [
    ("What is 1247 divided by 43, rounded to 2 decimal places?",
     "success_1.txt"),
    ("What does the file 'course_info.txt' say?",
     "success_2.txt"),
    ("Tell me something about the University at Buffalo.",
     "success_3.txt"),
    ("Read the file 'numbers.txt' and tell me the sum of all numbers in it.",
     "success_4_two_step.txt"),
    ("What is the meaning of life?",
     "failure_1.txt"),
    ("Read the file 'secrets.txt' and summarize it.",
     "failure_2.txt"),
]


def format_trace(question: str, result: dict) -> str:
    """Render one run as a plain-text Thought/Action/Observation transcript."""
    lines = [
        "=" * 70,
        f"QUESTION: {question}",
        "=" * 70,
        "",
        "TRACE",
        "-" * 70,
    ]

    for entry in result["trace"]:
        step = entry["step"] + 1
        kind = entry["type"]

        if kind == "model_reply":
            lines.append(f"[Step {step}] Model output:")
            lines.append(f"    {entry['content']}")
        elif kind == "tool_call":
            args = json.dumps(entry.get("args", {}))
            lines.append(f"[Step {step}] Action: {entry['tool']}({args})")
        elif kind == "observation":
            lines.append(f"[Step {step}] Observation: {entry['content']}")
        elif kind == "malformed":
            lines.append(f"[Step {step}] Parse failure: {entry['content']}")
        elif kind == "api_error":
            lines.append(f"[Step {step}] API error: {entry['content']}")
        elif kind == "final":
            lines.append(f"[Step {step}] Final answer: {entry['content']}")
        lines.append("")

    lines.extend([
        "-" * 70,
        "RESULT",
        "-" * 70,
        f"success: {result['success']}",
        f"answer:  {result['answer']}",
    ])
    if "reason" in result:
        lines.append(f"reason:  {result['reason']}")

    lines.extend(["", "RAW RESULT (JSON)", "-" * 70,
                  json.dumps(result, indent=2), ""])

    return "\n".join(lines)


def main() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    for question, filename in CASES:
        print(f"\n{'=' * 70}")
        print(f"Question: {question}")

        result = run_agent(question, verbose=True)

        transcript = format_trace(question, result)
        path = os.path.join(LOG_DIR, filename)
        with open(path, "w") as f:
            f.write(transcript)

        print(f"\nsuccess={result['success']}  answer={result['answer']}")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
