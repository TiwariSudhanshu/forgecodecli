import typer
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file, create_dir

app = typer.Typer()


@app.command()
def run(prompt: str = typer.Argument(None)):
    """
    ForgeCode CLI — agent with actions
    """

    # ===============================
    # INTERACTIVE MODE
    # ===============================
    if prompt is None:
        print("ForgeCode Interactive Mode (type 'quit' or Ctrl+C to exit)\n")
        messages = []

        try:
            while True:
                user_input = input("> ").strip()

                if user_input.lower() in ("quit", "exit"):
                    print("Bye")
                    break

                messages.append({"role": "user", "content": user_input})
                answered = False

                for _ in range(5):
                    decision = think(messages)
                    action = decision.get("action")
                    args = decision.get("args", {})

                    if action == "read_file":
                        result = read_file(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "list_files":
                        result = list_files(args.get("path", "."))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "create_dir":
                        result = create_dir(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "write_file":
                        result = write_file(
                            args.get("path"),
                            args.get("content")
                        )
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "answer":
                        print(args.get("text", ""))
                        answered = True
                        break

                if not answered:
                    print("⚠️ I couldn't complete this request.")

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
