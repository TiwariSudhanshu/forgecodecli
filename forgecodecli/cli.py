import typer
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file


app = typer.Typer()

@app.command()
def run (prompt:str):
    """
    ForgeCode CLI — agent with actions
    """
    
    messages = [{"role": "user", "content": prompt}]
    for step in range(5):
        decision = think(messages)
        action = decision.get("action")
        args = decision.get("args", {})
    
        if action == "read_file":
            path = args.get("path")
            result = read_file(path)
            messages.append({
                "role": "assistant",
                "content": f"READ RESULT:\n{result}"
})
        
        elif action == "list_files":
            path= args.get("path", ".")
            result = list_files(path)
            messages.append({
            "role": "assistant",
            "content": f"LIST RESULT:\n{result}"
        })
        elif action == "write_file":
            path = args.get("path")
            content = args.get("content")
            result = write_file(path, content)
            messages.append({
            "role": "assistant",
            "content": f"WRITE RESULT:\n{result}"
        })
        elif action == "answer":
            print(args.get("text", ""))
            break


    
def main():
        app()
        
if __name__ == "__main__":
    main()