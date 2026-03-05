# ForgeCodeCLI Release History

## v3.0.0 (Current) - March 5, 2026

### ✨ New Features
- **Git Operations** - Full version control support
  - `git_init` - Initialize repositories
  - `git_add` - Stage files
  - `git_commit` - Commit changes
  - `git_push` - Push to remote
  - `git_pull` - Pull from remote
  - `git_status` - Check repository status
  - `git_log` - View commit history
  - `git_branch` - Manage branches
  - `git_clone` - Clone repositories
  - `git_set_origin` - Configure remote URL

### 🐛 Bug Fixes
- Fixed agent loop iterations preventing proper completion
- Improved message history management

### 📦 Downloads
- **forgecodecli.exe** - Standalone Windows executable (~20.8 MB)
  - No Python installation required
  - Ready to use out of the box

---

## v2.1.0 - March 4, 2026

### ✨ New Features
- **Multi-Provider LLM Support**
  - Google Gemini
  - OpenAI (GPT-4, GPT-4 turbo, GPT-3.5)
  - Anthropic (Claude 3 family)
  - Groq (Llama, Mixtral)
- **Model Selection** - Choose specific models per provider
- **Auto-install SDKs** - Anthropic SDK installs on demand

### 🐛 Bug Fixes
- Fixed stale compiled files (.pyc cache) causing old UI to persist
- Removed build artifacts from git tracking

---

## v2.0.0 - March 3, 2026

### ✨ New Features
- **Undo Functionality** - Reverse the last operation
- **File Deletion** - Delete files and directories
- **File Movement** - Move and rename files/directories
- **Multi-Provider Setup** - Interactive provider selection during init
- **Conversation Flow** - Agent properly tracks completed actions

### 🔄 Changes
- Restructured agent loop with action limit (max 2 per request)
- Improved system prompt with better examples
- Added comprehensive .gitignore

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

### Latest Version (v3.0.0)

**Windows Users**:
Download `forgecodecli.exe` from [Releases](https://github.com/TiwariSudhanshu/forgecodecli/releases) and run directly.

**Developers**:
```bash
pip install forgecodecli
```

### From Source
```bash
git clone https://github.com/TiwariSudhanshu/forgecodecli.git
cd forgecodecli
pip install -e .
```

---

## Version Support
- **v3.0.0** - Current (Recommended)
- **v2.1.0** - Supported
- **v2.0.0** - Supported
- **v1.0.0** - Legacy (no longer updated)
