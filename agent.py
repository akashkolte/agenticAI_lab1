import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# from openai import OpenAI

load_dotenv()

api_key = os.getenv("BULLSAI_API_KEY")
temperature = os.getenv("TEMPERATURE")

SYSTEM_PROMPT = """\
You are a helpful assistant with access to tools.
 
{tool_descriptions}
 
Rules:
- To use a tool, respond ONLY with JSON:
  {{"tool": "<name>", "args": {{"<arg>": "<value>"}}}}
- For a final answer, respond ONLY with:
  {{"final_answer": "<your answer>"}}
- Do not mix prose and JSON. Choose one or the other.
- Use at most 5 tool calls per question.
"""

# pyrefly: ignore [invalid-annotation]
def run_agent(query: str, verbose: True):
    pass
    # for step in range(max_steps):
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini", messages=messages, temperature=0)
    # reply = response.choices[0].message.content.strip()
 
    # parsed = json.loads(reply)            # parse the model output
 
    # if "final_answer" in parsed:          # done?
    #     return {"success": True, "answer": parsed["final_answer"], ...}
 
    # if "tool" in parsed:                  # tool call
    #     fn, _ = TOOLS[parsed["tool"]]
    #     observation = fn(**parsed.get("args", {}))
    #     messages.append({"role": "assistant", "content": reply})
    #     messages.append({"role": "user",
    #                      "content": f"Observation: {observation}"})