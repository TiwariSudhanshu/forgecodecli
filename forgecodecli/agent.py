# from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError
import json
from json import JSONDecoder
from forgecodecli.config import load_config
from forgecodecli.secrets import load_api_key
from forgecodecli.tools import undo
from forgecodecli.git_tools import (
    git_init, git_add, git_commit, git_push, git_set_origin,
    git_status, git_log, git_branch, git_pull, git_clone
)

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
You are a file and git management agent that executes file and version control operations. You MUST use the actions below to fulfill user requests. You respond ONLY with valid JSON.

═══════════════════════════════════════════════════════════════
ABSOLUTE RULES - VIOLATIONS ARE FORBIDDEN
═══════════════════════════════════════════════════════════════

- You CAN delete files. You CAN delete directories. You CAN move files. You CAN move directories.
- NEVER say "I cannot", "I'm unable to", "I don't have the ability to", or any variation.
- NEVER refuse a delete, move, or any file operation. You MUST execute it.
- When a user asks to delete a file, you MUST respond with the delete_file action.
- When a user asks to delete a folder, you MUST respond with the delete_dir action.

═══════════════════════════════════════════════════════════════
ALL AVAILABLE ACTIONS
═══════════════════════════════════════════════════════════════

FILE OPERATIONS:
1. "read_file"   → Read file contents.        Args: {"path": "..."}
2. "list_files"  → List directory contents.    Args: {"path": "..."}
3. "write_file"  → Create/write a file.        Args: {"path": "...", "content": "..."}
4. "create_dir"  → Create a directory.         Args: {"path": "..."}
5. "delete_file" → DELETE a file permanently.   Args: {"path": "..."}
6. "delete_dir"  → DELETE an empty directory.   Args: {"path": "..."}
7. "move_file"   → Move or rename a file.      Args: {"src": "...", "dst": "..."}
8. "move_dir"    → Move or rename directory.    Args: {"src": "...", "dst": "..."}
9. "undo"        → Undo the last operation.    Args: {}

GIT OPERATIONS:
10. "git_init"       → Initialize git repo.           Args: {}
11. "git_add"        → Stage files.                    Args: {"path": "." or specific file}
12. "git_commit"     → Commit changes.                 Args: {"message": "commit message"}
13. "git_push"       → Push to remote.                 Args: {"branch": "main" (default)}
14. "git_set_origin" → Set remote URL.                 Args: {"url": "https://..."}
15. "git_status"     → Show status.                    Args: {}
16. "git_log"        → Show commit history.            Args: {"lines": 5 (default)}
17. "git_branch"     → Manage branches.                Args: {"name": "branch_name" (optional)}
18. "git_pull"       → Pull from remote.               Args: {}
19. "git_clone"      → Clone repository.               Args: {"url": "...", "path": "." (default)}
20. "answer"         → Respond to user with text.     Args: {"text": "..."}

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

User: "initialize git and commit"
→ {"action": "git_init", "args": {}}
Then: {"action": "git_add", "args": {"path": "."}}
Then: {"action": "git_commit", "args": {"message": "Initial commit"}}
Then: {"action": "answer", "args": {"text": "Repository initialized and committed."}}

User: "push to origin"
→ {"action": "git_push", "args": {"branch": "main"}}
Then: {"action": "answer", "args": {"text": "Pushed to origin/main."}}

User: "create hello.py with print('hi')"
→ {"action": "write_file", "args": {"path": "hello.py", "content": "print('hi')"}}
Then: {"action": "answer", "args": {"text": "File created."}}

REMEMBER: You have delete_file, delete_dir, undo, and git tools. USE THEM when asked.
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
