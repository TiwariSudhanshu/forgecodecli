# ForgeCodeCLI Release History

## v2.0.0 (Current - Released) - March 5, 2026

### ✨ New Features

**File Operations**
- **Undo functionality** - Stack-based operation reversal
- **Delete files and directories** - Full file/directory manipulation
- **Move and rename files/directories** - Flexible file organization

**Git Operations** - Full version control support
- `git_init` - Initialize repositories
- `git_add` - Stage files for commit
- `git_commit` - Commit staged changes
- `git_push` - Push to remote repository
- `git_pull` - Pull from remote
- `git_status` - Check repository status
- `git_log` - View commit history
- `git_branch` - Manage branches
- `git_clone` - Clone repositories
- `git_set_origin` - Configure remote URL

**LLM Integration**
- **Multi-Provider LLM Support**
  - Google Gemini
  - OpenAI (GPT-4, GPT-4 turbo, GPT-3.5)
  - Anthropic (Claude 3 family)
  - Groq (Llama, Mixtral)
- **Model Selection** - Choose specific models per provider
- **Auto-install SDKs** - Anthropic SDK installs on demand

**Agent Improvements**
- Fixed agent loop iterations preventing proper completion
- Proper conversation flow with max actions (2 per request)
- Improved message history management

### 🔄 Changes

- Restructured agent loop with action limit
- Improved system prompt with better examples
- Added comprehensive .gitignore
- Removed build artifacts from git tracking

### 📦 Downloads

- **forgecodecli** on PyPI: `pip install forgecodecli==0.2.0`
- **forgecodecli.exe** - Standalone Windows executable (~20.8 MB)
  - No Python installation required
  - Ready to use out of the box

---

## v1.0.0 - February 2026

### ✨ Features

- **File Operations**
  - Read files
  - List directories
  - Create files
  - Create directories
- **Agentic Workflow** - LLM decides actions, CLI executes
- **Secure API Key Storage** - System keyring integration
- **Interactive CLI** - Real-time agent feedback
- **Gemini Support** - Google Gemini LLM integration

---

## Installation

### Latest Version (v2.0.0)

**From PyPI**:
```bash
pip install forgecodecli
```

**Windows Users**:
Download `forgecodecli.exe` from [Releases](https://github.com/TiwariSudhanshu/forgecodecli/releases) and run directly.

**From Source**:
```bash
git clone https://github.com/TiwariSudhanshu/forgecodecli.git
cd forgecodecli
pip install -e .
```

---

## Version Support

- **v2.0.0** - Current (Recommended)
- **v1.0.0** - Legacy (no longer updated)
