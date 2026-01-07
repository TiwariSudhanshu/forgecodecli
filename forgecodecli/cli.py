import typer
import sys
import os
import getpass

from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file, create_dir
from forgecodecli.secrets import save_api_key, delete_api_key
from forgecodecli.config import save_config, config_exists, delete_config

app = typer.Typer()
IS_EXE = getattr(sys, "frozen", False)


# ===============================
# UI
# ===============================
def show_logo():
    cwd = os.getcwd()
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
Model      : Gemini 2.5 Flash
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

    typer.echo("Select LLM provider:")
    typer.echo("  1) Gemini")
    typer.echo("  2) Exit")

    choice = typer.prompt(">")
    if choice != "1":
        typer.echo("Setup cancelled.")
        return

    api_key = getpass.getpass("Enter your Gemini API Key: ").strip()
    if not api_key:
        typer.echo("API Key cannot be empty.")
        return

    save_api_key(api_key)
    save_config({
        "provider": "gemini",
        "model": "gemini-2.5-flash"
    })

    typer.echo("\n✓ Setup complete")
    typer.echo("Run `forgecodecli` to start.")


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
            user_input = input("forgecode > ").strip().lower()

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
  reset  - Reset configuration
  exit   - Exit ForgeCodeCLI
""")
                continue

            if user_input == "reset":
                reset()
                print("\nRestarting setup...\n")
                init()
                messages = []
                continue

            # -------- SEND TO AGENT --------
            messages.append({"role": "user", "content": user_input})
            answered = False

            for _ in range(5):
                decision = think(messages)
                action = decision.get("action")
                args = decision.get("args", {})

                if action == "read_file":
                    describe_action(action, args)
                    result = read_file(args.get("path"))
                elif action == "list_files":
                    describe_action(action, args)
                    result = list_files(args.get("path", "."))
                elif action == "create_dir":
                    describe_action(action, args)
                    result = create_dir(args.get("path"))
                elif action == "write_file":
                    describe_action(action, args)
                    result = write_file(args.get("path"), args.get("content"))
                elif action == "answer":
                    print(args.get("text", ""))
                    answered = True
                    break
                else:
                    result = "⚠️ Unknown action"

                print(result)
                messages.append({"role": "assistant", "content": result})

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
