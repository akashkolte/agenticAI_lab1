# Lab 1 — A Minimal Tool-Using Agent

CSE 410 / 510 — Introduction to Agentic Engineering, Fall 2026

A small tool-using agent built from scratch in Python. It takes a
natural-language question, decides which of three tools to call, executes the
call, and answers from the tool's output. No agent framework — the control
flow is a `for` loop with an API call inside.

## Requirements

- Python 3.10+
- An API key for an OpenAI-compatible chat completions endpoint

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
```

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `BULLSAI_API_KEY` | API key for the gateway |
| `BASE_URL` | OpenAI-compatible API root, ending in `/v1` |
| `MODEL` | Model id to use |
| `TEMPERATURE` | Sampling temperature; keep at `0` for deterministic tool selection |

`.env` is gitignored and must never be committed.

## Running

Run all six test questions and write a trace for each to `logs/`:

```bash
python run_examples.py
```

Ask a single ad-hoc question:

```bash
python agent.py "What is 1247 divided by 43?"
```

## Layout

```
lab1/
├── agent.py           # The agent loop: Thought -> Action -> Observation
├── tools.py           # The three tools and the tool registry
├── run_examples.py    # Runs the test questions, writes logs/
├── design_note.md     # PEAS, design decisions, failure analysis
├── data/              # Files readable by the file_reader tool
│   ├── course_info.txt
│   └── numbers.txt
├── logs/              # Trace transcripts, one file per question
└── README.md
```

## The tools

| Tool | Argument | Returns |
|---|---|---|
| `calculator` | `expression: str` | Result of the expression, as a string |
| `file_reader` | `filename: str` | Contents of that file from `data/` |
| `lookup` | `query: str` | A short fact from a 12-entry local knowledge base |

Every tool returns a string on failure too (`"Error: ..."`), so a tool problem
becomes an observation the agent can reason about rather than an exception
that ends the run.

## Notes

- `calculator` uses `eval` with a stripped-out `__builtins__` and an allowlist
  of `math` functions plus a few numeric builtins. Fine for a lab; see
  `design_note.md` for the tradeoff.
- `file_reader` resolves paths and refuses anything outside `data/`, so the
  model cannot read `../.env`.
- The agent stops after 5 steps and reports `max_steps_exceeded` rather than
  looping forever.
