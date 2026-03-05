# from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError
import json
from json import JSONDecoder
from forgecodecli.config import load_config
from forgecodecli.secrets import load_api_key
from forgecodecli.tools import undo

# Provider base URLs (OpenAI-compatible)
PROVIDER_BASE_URLS = {
    "gemini":    "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openai":    None,   # default OpenAI
    "groq":      "https://api.groq.com/openai/v1",
}

def get_client():
    config = load_config()
    api_key = load_api_key()

    if not config:
        raise RuntimeError(
            "ForgeCodeCLI is not set up. Run `forgecodecli init`."
        )

    if not api_key:
        raise RuntimeError(
            "API key not found. Run `forgecodecli init` again."
        )

    provider = config.get("provider", "gemini")

    if provider == "anthropic":
        try:
            import anthropic as _anthropic
            return _anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise RuntimeError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

    base_url = PROVIDER_BASE_URLS.get(provider)
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
You are a file management agent that executes file operations. You MUST use the actions below to fulfill user requests. You respond ONLY with valid JSON.

═══════════════════════════════════════════════════════════════
ABSOLUTE RULES - VIOLATIONS ARE FORBIDDEN
═══════════════════════════════════════════════════════════════

- You CAN delete files. You CAN delete directories. You CAN move files. You CAN move directories.
- NEVER say "I cannot", "I'm unable to", "I don't have the ability to", or any variation.
- NEVER refuse a delete, move, or any file operation. You MUST execute it.
- When a user asks to delete a file, you MUST respond with the delete_file action.
- When a user asks to delete a folder, you MUST respond with the delete_dir action.

═══════════════════════════════════════════════════════════════
ALL 8 AVAILABLE ACTIONS
═══════════════════════════════════════════════════════════════

1. "read_file"   → Read file contents.        Args: {"path": "..."}
2. "list_files"  → List directory contents.    Args: {"path": "..."}
3. "write_file"  → Create/write a file.        Args: {"path": "...", "content": "..."}
4. "create_dir"  → Create a directory.         Args: {"path": "..."}
5. "delete_file" → DELETE a file permanently.   Args: {"path": "..."}
6. "delete_dir"  → DELETE an empty directory.   Args: {"path": "..."}
7. "move_file"   → Move or rename a file.      Args: {"src": "...", "dst": "..."}
8. "move_dir"    → Move or rename directory.    Args: {"src": "...", "dst": "..."}
9. "undo"        → Undo the last operation.    Args: {}
10. "answer"     → Respond to user with text.  Args: {"text": "..."}

═══════════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════════

1. MAXIMUM 2 actions per request (not counting "answer")
2. After completing all required actions, ALWAYS respond with "answer"
3. Do NOT repeat the same action twice
4. Do NOT take multiple write_file or create_dir actions in one request
5. Choose the MOST DIRECT action for the task

═══════════════════════════════════════════════════════════════
RESPONSE FORMAT - ONLY VALID JSON
═══════════════════════════════════════════════════════════════

You MUST respond ONLY with valid JSON, nothing else. No text before or after.

{"action": "action_name", "args": {"key": "value"}}

═══════════════════════════════════════════════════════════════
EXAMPLES
═══════════════════════════════════════════════════════════════

User: "delete love.txt from megha folder"
→ {"action": "delete_file", "args": {"path": "megha/love.txt"}}
Then: {"action": "answer", "args": {"text": "File megha/love.txt deleted."}}

User: "delete temp.txt"
→ {"action": "delete_file", "args": {"path": "temp.txt"}}
Then: {"action": "answer", "args": {"text": "File deleted."}}

User: "remove the old_data folder"
→ {"action": "delete_dir", "args": {"path": "old_data"}}
Then: {"action": "answer", "args": {"text": "Directory removed."}}

User: "read config.py"
→ {"action": "read_file", "args": {"path": "config.py"}}
Then: {"action": "answer", "args": {"text": "Here is the config.py file"}}

User: "create hello.py with print('hi')"
→ {"action": "write_file", "args": {"path": "hello.py", "content": "print('hi')"}}
Then: {"action": "answer", "args": {"text": "File created."}}

User: "move file.py to backup/file.py"
→ {"action": "move_file", "args": {"src": "file.py", "dst": "backup/file.py"}}
Then: {"action": "answer", "args": {"text": "File moved."}}

User: "what's in src?"
→ {"action": "list_files", "args": {"path": "src"}}
Then: {"action": "answer", "args": {"text": "Here are the files."}}

User: "make a backup folder"
→ {"action": "create_dir", "args": {"path": "backup"}}
Then: {"action": "answer", "args": {"text": "Folder created."}}

REMEMBER: You have delete_file, delete_dir, and undo actions. USE THEM when asked to delete or undo.
"""

def think(messages: list[dict]) -> dict:
    config = load_config()
    model = config.get("model", "gemini-2.5-flash")
    provider = config.get("provider", "gemini")
    try:
      client = get_client()

      # Anthropic uses its own SDK format
      if provider == "anthropic":
          response = client.messages.create(
              model=model,
              max_tokens=1024,
              system=SYSTEM_PROMPT,
              messages=messages,
          )
          content = response.content[0].text
      else:
          response = client.chat.completions.create(
              model=model,
              messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
              temperature=0
          )
          content = response.choices[0].message.content

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
    
    # Handle empty response
    if content is None or not content.strip():
        return {
            "action": "answer",
            "args": {
                "text": "Task completed successfully!"
            }
        }
    
    cleaned = content.strip()

    # Robust JSON extraction
    decoder = JSONDecoder()
    
    # Try to find JSON object in the content
    idx = cleaned.find("{")
    if idx == -1:
        return {
        "action": "answer",
        "args": {
            "text": cleaned
        }
    }
    
    # Extract from first { onwards
    cleaned = cleaned[idx:]
    
    # Try to decode JSON, handling partial/malformed content
    try:
        obj, _ = decoder.raw_decode(cleaned)
        return obj
    except json.JSONDecodeError:
        # If it fails, try to find the end of a valid JSON object
        # by trying progressively shorter strings from the end
        for end_pos in range(len(cleaned), idx, -1):
            try:
                obj, _ = decoder.raw_decode(cleaned[:end_pos])
                return obj
            except json.JSONDecodeError:
                continue
        
        raise ValueError(f"Could not parse JSON from LLM output: {cleaned[:100]}...")
