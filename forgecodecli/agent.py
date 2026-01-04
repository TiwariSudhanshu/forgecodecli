from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from json import JSONDecoder
from openai import RateLimitError

# Load env
load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SYSTEM_PROMPT = """
You are an agent that decides what action to take.
You may take multiple actions to solve the task.
After each tool result, decide the next best action.
When the task is complete, choose "answer".

You can choose ONLY one of these actions:
- "read_file"
- "list_files"
- "write_file"
- "create_dir"
- "answer"

Rules:
- If the user asks to read/open/inspect a file → read_file
- If the user asks about files/folders/structure → list_files
- If the user asks to create/write/save a file → write_file
- If the user asks to create a directory/folder → create_dir
- Otherwise → answer
- Do NOT repeat the same action with the same arguments.

You MUST respond in VALID JSON ONLY.

JSON format:
{
  "action": "<action_name>",
  "args": { ... }
}
"""

def think(messages: list[dict]) -> dict:
    try:
      response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages
    )
    except RateLimitError as e:
      return {
        "action": "answer",
        "args": {
            "text": "⚠️ Rate limit hit. Please wait a few seconds and try again."
        }
    }
    except Exception as e:
      return {
        "action": "answer",
        "args": {
            "text": f"❌ LLM error: {str(e)}"
        }
    }


    content = response.choices[0].message.content
    cleaned = content.strip()

    # Strip markdown fences
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()

    # Strip leading `json`
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    # Robust JSON extraction (NO REGEX)
    decoder = JSONDecoder()
    cleaned = cleaned.lstrip()

    if not cleaned.startswith("{"):
        idx = cleaned.find("{")
        if idx == -1:
            raise ValueError("No JSON object found in LLM output")
        cleaned = cleaned[idx:]

    obj, _ = decoder.raw_decode(cleaned)
    return obj
