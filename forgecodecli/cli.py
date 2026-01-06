import typer
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file, create_dir

app = typer.Typer()

import os

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
(type 'quit' or Ctrl+C to exit)\n
""")

def describe_action(action: str, args: dict):
    if action == "read_file":
        print(f"📂 Reading file: {args.get('path')}")
    elif action == "list_files":
        print(f"📄 Listing files in: {args.get('path', '.')}")
    elif action == "create_dir":
        print(f"📁 Creating directory: {args.get('path')}")
    elif action == "write_file":
        print(f"✍️ Writing file: {args.get('path')}")


@app.command()
def run(prompt: str = typer.Argument(None)):
    """
    ForgeCode CLI — agent with actions
    """

    # ===============================
    # INTERACTIVE MODE
    # ===============================
    if prompt is None:
        show_logo()
        messages = []

        try:
            while True:
                user_input = input("forgecode (agent) >  ").strip()

                if user_input.lower() in ("quit", "exit"):
                    print("Bye")
                    break

                messages.append({"role": "user", "content": user_input})
                # print("🤔 Planning actions...")
                answered = False

                for _ in range(5):
                    decision = think(messages)
                    action = decision.get("action")
                    args = decision.get("args", {})

                    if action == "read_file":
                        describe_action(action, args)
                        result = read_file(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})
                    
                    elif action == "list_files":
                        describe_action(action, args)
                        result = list_files(args.get("path", "."))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "create_dir":
                        describe_action(action, args)
                        result = create_dir(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "write_file":
                        describe_action(action, args)
                        result = write_file(
                            args.get("path"),
                            args.get("content")
                        )
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "answer":
                        print(args.get("text", ""))
                        answered = True
                        # Keep only last 10 messages to avoid context overflow
                        if len(messages) > 20:
                            messages = messages[-20:]
                        break

                if not answered:
                    print("⚠️ I couldn't complete this request.")
                    print("✅ Done")
                    # Keep only last 10 messages to avoid context overflow
                    if len(messages) > 20:
                        messages = messages[-20:]

        except KeyboardInterrupt:
            print("\nBye")

        return

    # ===============================
    # ONE-SHOT MODE
    # =============================== 
    messages = [{"role": "user", "content": prompt}]
    answered = False

    for _ in range(5):
        decision = think(messages)
        action = decision.get("action")
        args = decision.get("args", {})

        if action == "read_file":
            result = read_file(args.get("path"))
            messages.append({"role": "assistant", "content": result})

        elif action == "list_files":
            result = list_files(args.get("path", "."))
            messages.append({"role": "assistant", "content": result})

        elif action == "create_dir":
            result = create_dir(args.get("path"))
            messages.append({"role": "assistant", "content": result})

        elif action == "write_file":
            result = write_file(
                args.get("path"),
                args.get("content")
            )
            messages.append({"role": "assistant", "content": result})

        elif action == "answer":
            print(args.get("text", ""))
            answered = True
            break

    if not answered:
        print("⚠️ I couldn't complete this request with the available tools.")


def main():
    app()


if __name__ == "__main__":
    main()
