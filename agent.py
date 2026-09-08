"""The agent loop.

Orchestrates a Thought -> Action -> Observation cycle: ask the model what to
do, execute the tool it names, feed the result back as an observation, and
repeat until the model produces a final answer or the step budget runs out.

There is no framework here -- it is a `for` loop with an API call inside.
"""

import json
import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from openai import OpenAI

from tools import TOOLS, build_tool_descriptions

load_dotenv()

# Accept either the prefixed or the bare form of each setting.
API_KEY = os.getenv("BULLSAI_API_KEY") or os.getenv("API_KEY")
BASE_URL = os.getenv("BULLSAI_BASE_URL") or os.getenv("BASE_URL")
MODEL = os.getenv("BULLSAI_MODEL") or os.getenv("MODEL")

try:
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
except ValueError:
    TEMPERATURE = 0.0


SYSTEM_PROMPT = """\
You are a helpful assistant with access to tools.

{tool_descriptions}

Rules:
- To use a tool, respond ONLY with JSON:
  {{"tool": "<name>", "args": {{"<arg>": "<value>"}}}}
- For a final answer, respond ONLY with:
  {{"final_answer": "<your answer>"}}
- Do not mix prose and JSON. Choose one or the other.
- Do not wrap the JSON in markdown code fences.
- Base your final answer on the observations you received. If a tool
  returned an error, say so instead of inventing a result.
- Use at most 5 tool calls per question.
"""


def _build_client() -> OpenAI:
    """Construct the API client, failing loudly if configuration is missing."""
    missing = [
        name for name, value in (
            ("BULLSAI_API_KEY", API_KEY),
            ("BASE_URL", BASE_URL),
            ("MODEL", MODEL),
        ) if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill them in."
        )
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def _extract_json(reply: str) -> dict | None:
    """Parse a model reply as JSON, tolerating markdown code fences.

    Returns None if no JSON object can be recovered.
    """
    text = reply.strip()

    if text.startswith("```"):
        # Drop the opening fence (with an optional language tag) and the
        # closing fence. Models emit these regularly despite being told not to.
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Last resort: the model wrapped JSON in prose. Take the outermost
        # {...} span and try again.
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            parsed = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None

    return parsed if isinstance(parsed, dict) else None


def _call_tool(tool_name: str, args: dict) -> str:
    """Dispatch to a registered tool, converting any failure into a string."""
    if tool_name not in TOOLS:
        return (
            f"Error: Unknown tool '{tool_name}'. "
            f"Available tools: {', '.join(TOOLS)}."
        )

    fn, _ = TOOLS[tool_name]
    if not isinstance(args, dict):
        return f"Error: 'args' must be a JSON object, got {type(args).__name__}."

    try:
        return str(fn(**args))
    except TypeError as e:
        return f"Error calling tool '{tool_name}': {e}"


def run_agent(question: str, max_steps: int = 5, verbose: bool = True) -> dict:
    """Run the agent on a single question.

    Returns a dict with keys: success, answer, trace, and (on failure) reason.
    The trace records every step so the run can be read back afterwards.
    """
    client = _build_client()

    system = SYSTEM_PROMPT.format(
        tool_descriptions=build_tool_descriptions(TOOLS))
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]

    trace = []

    for step in range(max_steps):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=TEMPERATURE,
            )
            reply = (response.choices[0].message.content or "").strip()
        except Exception as e:
            trace.append({"step": step, "type": "api_error", "content": str(e)})
            return {"success": False, "answer": None, "trace": trace,
                    "reason": "api_error"}

        if verbose:
            print(f"\n--- Step {step + 1} ---")
            print(f"Model: {reply}")

        trace.append({"step": step, "type": "model_reply", "content": reply})

        parsed = _extract_json(reply)

        if parsed is None:
            # Malformed output. Tell the model what went wrong and give it
            # one more turn rather than aborting the run.
            observation = (
                "Error: Your response was not valid JSON. Respond with either "
                '{"tool": ..., "args": {...}} or {"final_answer": "..."} '
                "and nothing else."
            )
            trace.append({"step": step, "type": "malformed",
                          "content": observation})
            if verbose:
                print(f"Observation: {observation}")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": observation})
            continue

        if "final_answer" in parsed:
            answer = parsed["final_answer"]
            trace.append({"step": step, "type": "final", "content": answer})
            return {"success": True, "answer": answer, "trace": trace}

        if "tool" in parsed:
            tool_name = parsed["tool"]
            args = parsed.get("args", {})
            trace.append({"step": step, "type": "tool_call",
                          "tool": tool_name, "args": args})

            observation = _call_tool(tool_name, args)

            if verbose:
                print(f"Observation: {observation}")

            trace.append({"step": step, "type": "observation",
                          "content": observation})

            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user",
                             "content": f"Observation: {observation}"})
            continue

        # Valid JSON, but neither a tool call nor a final answer.
        observation = (
            'Error: Your JSON must contain either a "tool" key or a '
            '"final_answer" key.'
        )
        trace.append({"step": step, "type": "malformed", "content": observation})
        if verbose:
            print(f"Observation: {observation}")
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": observation})

    return {"success": False, "answer": None, "trace": trace,
            "reason": "max_steps_exceeded"}


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What is 1247 divided by 43?"
    print(json.dumps(run_agent(q), indent=2))
