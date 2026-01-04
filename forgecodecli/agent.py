from dotenv import load_dotenv
from openai import OpenAI
import os
import json

# 1️⃣ Load environment variables from .env
load_dotenv()

# 2️⃣ Create the LLM client (Gemini via OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3️⃣ SYSTEM PROMPT = RULEBOOK FOR THE AGENT
SYSTEM_PROMPT = """
You are an agent that decides what action to take.

You can choose ONLY one of these actions:
- "read_file"
- "list_files"
- "write_file"
- "answer"

Rules:
- If the user asks to read, open, inspect, or check a file, choose "read_file"
- If the user asks about files, folders, structure, or project layout, choose "list_files"
- If the user asks to create, write, or save a file, choose "write_file"
- Otherwise choose "answer"

You MUST respond in VALID JSON ONLY.
Do not add explanations.
Do not add extra text.
When using "read_file", args MUST be:
{
  "path": "<file_path>"
}
When using "list_files", args MUST be:
{
  "path": "<directory_path>"
}
When using "write_file", args MUST be:
{
  "path": "<file_path>",
    "content": "<file_content>"
}
DO NOT use keys like "file_path", "filename", or "file".
ONLY use "path".

JSON format:
{
  "action": "<action_name>",
  "args": { ... }
}
"""

# 4️⃣ Agent brain function
def think(prompt: str) -> dict:
    """
    Takes user input and returns a decision as a Python dictionary.
    """

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # 5️⃣ Extract text response from model
    content = response.choices[0].message.content
    cleaned = content.strip()

    # if cleaned.startswith("```"):
    #     cleaned = cleaned.split("```")[1]
        
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()

# Remove leading language tag like "json"
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()

    # 6️⃣ Convert JSON string → Python dict
    return json.loads(cleaned)