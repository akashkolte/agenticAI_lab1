"""Tool definitions and the tool registry for the Lab 1 agent.

Each tool is a plain Python callable with a well-defined signature, a
docstring, and a predictable return type. Every tool returns a *string* --
including on failure -- so that a tool error becomes an observation the
agent can reason about rather than an exception that kills the loop.
"""

import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Names visible to `calculator`: everything public from `math`, plus a short
# allowlist of numeric builtins. `round` in particular is needed for questions
# like "rounded to 2 decimal places". Nothing here can open files, import
# modules, or reach the filesystem.
_SAFE_BUILTINS = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "pow": pow, "int": int, "float": float, "len": len,
}
_ALLOWED_NAMES = {k: v for k, v in math.__dict__.items()
                  if not k.startswith("__")}
_ALLOWED_NAMES.update(_SAFE_BUILTINS)


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result as a string."""
    try:
        # Restricted namespace: builtins are stripped, so only the names in
        # _ALLOWED_NAMES resolve.
        result = eval(expression, {"__builtins__": {}}, dict(_ALLOWED_NAMES))
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def file_reader(filename: str) -> str:
    """Read a text file from the data/ directory and return its contents."""
    try:
        path = os.path.realpath(os.path.join(DATA_DIR, filename))
        # Confine reads to data/. Without this, 'file_reader("../.env")'
        # would hand the model the API key.
        if os.path.commonpath([path, DATA_DIR]) != DATA_DIR:
            return f"Error: Access to '{filename}' is not allowed."
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except IsADirectoryError:
        return f"Error: '{filename}' is a directory, not a file."
    except Exception as e:
        return f"Error: {e}"


# A small local knowledge base. Kept deliberately modest (12 entries) --
# the point is to exercise lookup logic, not to build a real KB.
KNOWLEDGE_BASE = {
    "university at buffalo": (
        "The University at Buffalo (UB) is a public research university in "
        "Buffalo, New York, and the largest campus in the SUNY system."
    ),
    "buffalo": (
        "Buffalo, NY is the second-largest city in New York State, located "
        "at the eastern end of Lake Erie near Niagara Falls."
    ),
    "niagara falls": (
        "Niagara Falls is a group of three waterfalls on the border between "
        "Ontario, Canada and New York State, about 20 miles from Buffalo."
    ),
    "python": (
        "Python is a high-level, general-purpose programming language "
        "created by Guido van Rossum and first released in 1991."
    ),
    "react": (
        "ReAct (Reasoning + Acting) is a prompting pattern from Yao et al. "
        "(ICLR 2023) in which a model interleaves reasoning traces with tool "
        "calls, consuming each observation before continuing."
    ),
    "peas": (
        "PEAS is a framework from Russell & Norvig for specifying an agent: "
        "Performance measure, Environment, Actuators, and Sensors."
    ),
    "agent": (
        "An agent is a software system that perceives a bounded environment, "
        "selects actions from a defined action space using a policy, and "
        "executes those actions to pursue an explicit goal."
    ),
    "tool": (
        "In an agentic system, a tool is a callable with a well-defined "
        "signature, a description, and a predictable return type, exposed to "
        "the model through a registry."
    ),
    "hallucination": (
        "Hallucination is the failure mode in which a language model states "
        "content that is not grounded in its input or in any observation it "
        "actually received."
    ),
    "temperature": (
        "Temperature is a sampling parameter controlling randomness in model "
        "output. Temperature 0 is effectively greedy decoding and is "
        "preferred when tool selection must be deterministic."
    ),
    "cse 510": (
        "CSE 510 is Introduction to Agentic Engineering at the University at "
        "Buffalo, taught in Fall 2026 by Dr. Joaquin Carbonara and "
        "Dr. David Doermann."
    ),
    "ub": (
        "UB is the common abbreviation for the University at Buffalo."
    ),
}


def lookup(query: str) -> str:
    """Look up a fact from a small local knowledge base."""
    key = query.lower().strip()
    # Longest keys first so a short key does not shadow a more specific one:
    # "university at buffalo" should win over both "buffalo" and "ub".
    for k in sorted(KNOWLEDGE_BASE, key=len, reverse=True):
        if k in key:
            return KNOWLEDGE_BASE[k]
    return "No entry found for that query."


# Tool registry: maps tool name -> (callable, description).
# The descriptions are what the model actually sees, so they name the
# argument each tool expects.
TOOLS = {
    "calculator": (
        calculator,
        "Evaluates a mathematical expression. Argument: 'expression', a "
        "string such as '2 + 2' or 'sqrt(16)'. Must be valid Python math "
        "syntax -- use '*' for multiplication, not the word 'times'. "
        "Returns the numeric result."
    ),
    "file_reader": (
        file_reader,
        "Reads a text file from the data/ directory. Argument: 'filename', "
        "a string such as 'notes.txt'. Returns the file contents."
    ),
    "lookup": (
        lookup,
        "Looks up a factual query in a local knowledge base. Argument: "
        "'query', a topic string such as 'python' or 'UB'. Returns a short "
        "description, or 'No entry found for that query.'"
    ),
}


def build_tool_descriptions(tools: dict) -> str:
    """Render the tool registry as a prompt-ready description block."""
    lines = ["You have access to the following tools:\n"]
    for name, (fn, desc) in tools.items():
        lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)
