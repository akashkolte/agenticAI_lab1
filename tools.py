import math
 
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    try:
        allowed = {k: v for k, v in math.__dict__.items()
                   if not k.startswith("__")}
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


import os
 
def file_reader(filename: str) -> str:
    """Read a text file and return its contents."""
    try:
        safe_dir = os.path.join(os.path.dirname(__file__), "data")
        path = os.path.join(safe_dir, filename)
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error: {e}"


def lookup(query: str) -> str:
    """Look up a fact from a small local knowledge base."""
    kb = {
        "buffalo": "Buffalo, NY is the second-largest city in NY State...",
        "python":  "Python is a high-level programming language...",
        "ub":      "The University at Buffalo (UB) is a public...",
        # Add more entries as needed (10-15 is plenty)
    }
    key = query.lower().strip()
    for k, v in kb.items():
        if k in key:
            return v
    return "No entry found for that query."

TOOLS = {
    "calculator": (
        calculator,
        "Evaluates a math expression. Input: '2 + 2' or 'sqrt(16)'."
    ),
    "file_reader": (
        file_reader,
        "Reads a text file from data/. Input: a filename like 'notes.txt'."
    ),
    "lookup": (
        lookup,
        "Looks up a query in a local KB. Input: a topic like 'python'."
    ),
}

def build_tool_descriptions(tools: dict) -> str:
    lines = ["You have access to the following tools:\n"]
    for name, (fn, desc) in tools.items():
        lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)
