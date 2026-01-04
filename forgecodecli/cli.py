import typer
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file


app = typer.Typer()

@app.command()
def run (prompt:str):
    """
    ForgeCode CLI — agent with actions
    """
    decision = think(prompt)
    action = decision.get("action")
    args = decision.get("args", {})
    
    if action == "read_file":
        path = args.get("path")
        result = read_file(path)
        print(result)
        
    elif action == "list_files":
        path= args.get("path", ".")
        result = list_files(path)
        print(result)
    elif action == "write_file":
        path = args.get("path")
        content = args.get("content")
        result = write_file(path, content)
        print(result)

    elif action == "answer":
        text = args.get("text")
        print(text)

    else:
        print(f"Unknown action: {action}")
    

    
def main():
        app()
        
if __name__ == "__main__":
    main()