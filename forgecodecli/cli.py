import typer
import sys
import os
import json
import getpass
import subprocess

from forgecodecli import path_resolver
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file, create_dir, delete_file, delete_dir, move_file, move_dir, undo
from forgecodecli.git_tools import (
    git_init, git_add, git_commit, git_push, git_set_origin,
    git_status, git_log, git_branch, git_pull, git_clone
)
from forgecodecli.secrets import save_api_key, delete_api_key
from forgecodecli.config import save_config, config_exists, delete_config, load_config
from forgecodecli.path_resolver import  resolve_path

app = typer.Typer()
IS_EXE = getattr(sys, "frozen", False)


# ===============================
# UI
# ===============================
PROVIDERS = {
    "1": {"name": "Google Gemini",     "key": "gemini",    "models": [
        ("gemini-2.5-flash",  "Fast & free tier"),
        ("gemini-2.0-flash",  "Latest Gemini"),
        ("gemini-1.5-pro",    "Most powerful Gemini"),
    ]},
    "2": {"name": "OpenAI",            "key": "openai",    "models": [
        ("gpt-4o",            "Most capable GPT"),
        ("gpt-4-turbo",       "Fast GPT-4"),
        ("gpt-3.5-turbo",     "Fast & cheap"),
    ]},
    "3": {"name": "Anthropic (Claude)", "key": "anthropic", "models": [
        ("claude-3-5-sonnet-20241022", "Best balance"),
        ("claude-3-opus-20240229",     "Most powerful"),
        ("claude-3-haiku-20240307",    "Fastest & cheapest"),
    ]},
    "4": {"name": "Groq",              "key": "groq",      "models": [
        ("llama-3.3-70b-versatile",  "Best Llama 3.3"),
        ("mixtral-8x7b-32768",       "Mixtral 8x7B"),
        ("gemma2-9b-it",             "Google Gemma2"),
    ]},
}

def show_logo():
    cwd = path_resolver.CLI_CWD
    config = load_config()
    provider_key = config.get("provider", "gemini")
    model = config.get("model", "gemini-2.5-flash")
    provider_name = next((v["name"] for v in PROVIDERS.values() if v["key"] == provider_key), provider_key)
    print(f"""
███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

ForgeCode CLI • Agentic File Assistant
Safe • Deterministic • File-aware

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Mode : Code Agent
Provider   : {provider_name}
Model      : {model}
Workspace  : {cwd}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type natural language commands to manage files.
Type 'help' for commands.
""")

def wait_before_exit():
    if IS_EXE and os.name == "nt":
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass


# ===============================
# SETUP COMMANDS
# ===============================
@app.command()
def init():
    """Initialize ForgeCodeCLI"""
    if config_exists():
        typer.echo("ForgeCodeCLI is already set up.")
        return

    typer.echo("Welcome to ForgeCodeCLI ✨\n")

    # ── Step 1: Select Provider ──
    typer.echo("Select LLM Provider:")
    for num, p in PROVIDERS.items():
        typer.echo(f"  {num}) {p['name']}")
    typer.echo("  5) Exit")

    provider_choice = typer.prompt(">").strip()
    if provider_choice not in PROVIDERS:
        typer.echo("Setup cancelled.")
        return

    provider = PROVIDERS[provider_choice]

    # ── Step 2: Select Model ──
    typer.echo(f"\nSelect Model for {provider['name']}:")
    for i, (model_id, desc) in enumerate(provider["models"], 1):
        typer.echo(f"  {i}) {model_id}  — {desc}")

    model_choice = typer.prompt(">").strip()
    try:
        selected_model = provider["models"][int(model_choice) - 1][0]
    except (ValueError, IndexError):
        typer.echo("Invalid choice. Setup cancelled.")
        return

    # ── Step 3: Enter API Key ──
    api_key = getpass.getpass(f"\nEnter your {provider['name']} API Key: ").strip()
    if not api_key:
        typer.echo("API Key cannot be empty.")
        return

    save_api_key(api_key)
    save_config({
        "provider": provider["key"],
        "model": selected_model
    })

    # Auto-install provider SDK if needed
    if provider["key"] == "anthropic":
        typer.echo("\n📦 Installing Anthropic SDK...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic", "-q"])
            typer.echo("✓ Anthropic SDK installed")
        except subprocess.CalledProcessError:
            typer.echo("⚠️  Could not auto-install. Run: pip install anthropic")

    typer.echo(f"\n✓ Setup complete")
    typer.echo(f"  Provider : {provider['name']}")
    typer.echo(f"  Model    : {selected_model}")
    typer.echo("\nRun `forgecodecli` to start.")


@app.command()
def reset():
    """Reset configuration"""
    if not config_exists():
        typer.echo("ForgeCodeCLI is not set up.")
        return

    if not IS_EXE:
        confirm = typer.prompt("Are you sure? (y/N)", default="n")
        if confirm.lower() != "y":
            typer.echo("Reset cancelled.")
            return

    delete_api_key()
    delete_config()
    typer.echo("✓ Configuration reset")


# ===============================
# ACTION UI
# ===============================
def describe_action(action: str, args: dict):
    if action == "read_file":
        print(f"📂 Reading file: {args.get('path')}")
    elif action == "list_files":
        print(f"📄 Listing files: {args.get('path', '.')}")
    elif action == "create_dir":
        print(f"📁 Creating directory: {args.get('path')}")
    elif action == "write_file":
        print(f"✍️ Writing file: {args.get('path')}")
    elif action == "delete_file":
        print(f"🗑️ Deleting file: {args.get('path')}")
    elif action == "delete_dir":
        print(f"🗑️ Deleting directory: {args.get('path')}")
    elif action == "move_file":
        print(f"🔄 Moving file: {args.get('src')} → {args.get('dst')}")
    elif action == "move_dir":
        print(f"🔄 Moving directory: {args.get('src')} → {args.get('dst')}")
    elif action == "undo":
        print(f"↩️ Undoing last operation")
    elif action == "git_init":
        print(f"🔧 Initializing git repository")
    elif action == "git_add":
        print(f"📝 Staging files: {args.get('path', '.')}")
    elif action == "git_commit":
        print(f"💾 Committing: {args.get('message', '')}")
    elif action == "git_push":
        print(f"🚀 Pushing to {args.get('branch', 'main')}")
    elif action == "git_set_origin":
        print(f"🔗 Setting origin: {args.get('url', '')}")
    elif action == "git_status":
        print(f"📊 Checking git status")
    elif action == "git_log":
        print(f"📜 Showing commit history")
    elif action == "git_branch":
        if args.get("name"):
            print(f"🌿 Creating branch: {args.get('name')}")
        else:
            print(f"🌿 Listing branches")
    elif action == "git_pull":
        print(f"⬇️ Pulling from remote")
    elif action == "git_clone":
        print(f"📦 Cloning repository: {args.get('url', '')}")


# ===============================
# MAIN LOOP
# ===============================
@app.callback(invoke_without_command=True)
def run(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return

    if not config_exists():
        print("ForgeCodeCLI is not set up.")
        print("Starting setup...\n")
        init()

    show_logo()
    messages = []

    while True:
        try:
            raw_input = input("forgecode > ").strip()
            user_input = raw_input.lower()
            if not user_input:
                continue

            # -------- INTERNAL COMMANDS --------
            if user_input == "exit":
                print("Goodbye.")
                wait_before_exit()
                sys.exit(0)

            if user_input == "help":
                print("""
                Available commands:
                help   - Show this help
                undo   - Undo last file operation
                reset  - Reset configuration
                exit   - Exit ForgeCodeCLI
                """)
                continue

            if user_input == "undo":
                result = undo()
                print(result)
                continue

            if user_input == "reset":
                reset()
                print("\nRestarting setup...\n")
                init()
                messages = []
                continue
            
            if user_input.startswith(("cd ", "navigate ", "go to ")):
                target = raw_input.split(" ",1)[1]
                new_path = resolve_path(target)
                
                if os.path.isdir(new_path):
                    path_resolver.CLI_CWD = new_path
                    print(f"{path_resolver.CLI_CWD} > ")
                else:
                    print("❌ Directory does not exist.")
                continue
            # -------- SEND TO AGENT --------
            messages.append({"role": "user", "content": raw_input})
            answered = False
            actions_taken = 0
            MAX_ACTIONS = 2

            for _ in range(MAX_ACTIONS + 2):
                # If action limit hit, force agent to answer
                if actions_taken >= MAX_ACTIONS:
                    messages.append({"role": "user", "content": "[System]: You have completed the required actions. Now respond with the 'answer' action only."})

                decision = think(messages)
                action = decision.get("action")
                args = decision.get("args", {})

                # Append agent's decision as assistant message
                messages.append({"role": "assistant", "content": json.dumps(decision)})

                if action == "read_file":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path"))
                    result = read_file(real_path)
                elif action == "list_files":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path", "."))
                    result = list_files(real_path)
                elif action == "create_dir":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path"))
                    result = create_dir(real_path)
                elif action == "write_file":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path"))
                    result = write_file(real_path, args.get("content"))
                elif action == "delete_file":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path"))
                    result = delete_file(real_path)
                elif action == "delete_dir":
                    describe_action(action, args)
                    real_path = resolve_path(args.get("path"))
                    result = delete_dir(real_path)
                elif action == "move_file":
                    describe_action(action, args)
                    src_path = resolve_path(args.get("src"))
                    dst_path = resolve_path(args.get("dst"))
                    result = move_file(src_path, dst_path)
                elif action == "move_dir":
                    describe_action(action, args)
                    src_path = resolve_path(args.get("src"))
                    dst_path = resolve_path(args.get("dst"))
                    result = move_dir(src_path, dst_path)
                elif action == "undo":
                    describe_action(action, args)
                    result = undo()
                elif action == "git_init":
                    describe_action(action, args)
                    result = git_init()
                elif action == "git_add":
                    describe_action(action, args)
                    result = git_add(args.get("path", "."))
                elif action == "git_commit":
                    describe_action(action, args)
                    result = git_commit(args.get("message", ""))
                elif action == "git_push":
                    describe_action(action, args)
                    result = git_push(args.get("branch", "main"))
                elif action == "git_set_origin":
                    describe_action(action, args)
                    result = git_set_origin(args.get("url", ""))
                elif action == "git_status":
                    describe_action(action, args)
                    result = git_status()
                elif action == "git_log":
                    describe_action(action, args)
                    result = git_log(args.get("lines", 5))
                elif action == "git_branch":
                    describe_action(action, args)
                    result = git_branch(args.get("name"))
                elif action == "git_pull":
                    describe_action(action, args)
                    result = git_pull()
                elif action == "git_clone":
                    describe_action(action, args)
                    result = git_clone(args.get("url", ""), args.get("path", "."))
                elif action == "answer":
                    print(args.get("text", ""))
                    answered = True
                    break
                else:
                    result = "⚠️ Unknown action"

                actions_taken += 1
                print(result)
                # Append tool result as user message so agent knows what happened
                messages.append({"role": "user", "content": f"[Tool result]: {result}"})

            if not answered:
                print("⚠️ Could not complete request.")

            if len(messages) > 20:
                messages = messages[-20:]

        except KeyboardInterrupt:
            print("\nInterrupted. Type 'exit' to quit.")


# ===============================
# ENTRY
# ===============================
def main():
    app()

if __name__ == "__main__":
    main()
