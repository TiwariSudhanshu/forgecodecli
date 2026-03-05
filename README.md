# ForgeCodeCLI

An agentic, file-aware command-line tool that lets you manage and modify your codebase using natural language — powered by LLMs.

It acts as a safe, deterministic AI agent that can read files, create/delete directories, and write code only through explicit tools, not raw hallucination.

## Features

- ✅ **Agentic workflow** - LLM decides actions, CLI executes them safely
- ✅ **File operations** - Read, list, create, write, delete, move files & directories
- ✅ **Undo support** - Reverse the last file operation with `undo`
- ✅ **Multi-provider LLMs** - Gemini, OpenAI (GPT), Anthropic (Claude), Groq
- ✅ **Model selection** - Choose specific models for each provider
- ✅ **Secure storage** - API keys stored in system keyring (no env vars)
- ✅ **Deterministic** - Rule-based execution with validation
- ✅ **Interactive CLI** - Real-time agent feedback

## Installation

Requires Python 3.9+

```bash
pip install forgecodecli
```

**Optional:** For Anthropic (Claude) support, install with the anthropic extra:

```bash
pip install forgecodecli[anthropic]
```

Or install later when prompted during setup.

## Quick Start

### Initialize (one-time setup)

```bash
forgecodecli init
```

You will be prompted to:

1. **Select LLM Provider**

   ```
   1) Google Gemini
   2) OpenAI
   3) Anthropic (Claude)
   4) Groq
   ```

2. **Select Model** (varies by provider)
   - Gemini: `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`
   - OpenAI: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
   - Claude: `claude-3-5-sonnet`, `claude-3-opus`, `claude-3-haiku`
   - Groq: `llama-3.3-70b`, `mixtral-8x7b`, `gemma2-9b-it`

3. **Enter API Key** (stored securely in system keyring)

### Start the agent

```bash
forgecodecli
```

You are now in interactive agent mode. Example commands:

```
create a folder src/app with main.py that prints "Hello World"
read the config.py file
list all files in src
delete old_backup folder
move test.py to tests/test.py
undo
```

Type `help` for built-in commands, or press `Ctrl + C` to exit.

## Reset Configuration

To remove all configuration and API keys:

```bash
forgecodecli reset
```

## Security

- API keys are stored using the system keyring
- No API keys are written to config files or environment variables
- Config files contain only non-sensitive metadata

## How It Works

1. You enter a natural language command
2. The LLM decides the next valid action
3. ForgeCodeCLI executes the action with validation
4. The agent receives feedback and responds
5. Process repeats until agent provides an answer

**Safety mechanisms:**

- Action limit of 2 per request (prevents infinite loops)
- Conversation context maintained for agent awareness
- All operations logged and reversible with `undo`
- Strict tool validation

## Supported Actions

The agent can execute these operations:

**File Operations:**
| Action | Description |
|--------|-------------|
| `read_file` | Read and display file contents |
| `list_files` | List files in a directory |
| `create_dir` | Create new directories |
| `write_file` | Create and write files |
| `delete_file` | Delete files permanently |
| `delete_dir` | Delete directories |
| `move_file` | Move or rename files |
| `move_dir` | Move or rename directories |
| `undo` | Reverse the last operation |

**Git Operations:**
| Action | Description |
|--------|-------------|
| `git_init` | Initialize git repository |
| `git_add` | Stage files for commit |
| `git_commit` | Commit staged changes |
| `git_push` | Push to remote repository |
| `git_set_origin` | Set remote repository URL |
| `git_status` | Show repository status |
| `git_log` | View commit history |
| `git_branch` | Manage branches |
| `git_pull` | Pull from remote |
| `git_clone` | Clone a repository |

All actions are executed safely with validation and error handling.

## Roadmap

### ✅ v1 (Released)

- Basic file operations (read, list, create, write)
- Gemini support
- Interactive CLI

### ✅ v2 (Released)

- **Undo functionality** - Stack-based operation reversal
- **Delete & move operations** - Full file/directory manipulation
- **Multi-provider support** - Gemini, OpenAI, Anthropic, Groq
- **Model selection** - Choose specific models per provider
- **Auto-install SDKs** - Anthropic SDK installs on demand
- **Fixed agent loop** - Proper conversation flow with max actions

### ✅ v3 (Current)

- **Git operations** - init, add, commit, push, pull, status, log, branch, clone, set_origin
- **Git workflow support** - Full version control integration
- **Repository management** - Clone and manage git repos

### 🚀 v4 (Planned)

- Copy files/directories
- Full undo/redo history (not just last operation)
- File search capabilities
- Code generation templates
- Batch operations
- Backup/snapshot functionality

## License

MIT License

## Author

Built by Sudhanshu
