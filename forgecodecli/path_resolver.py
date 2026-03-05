import os

CLI_CWD = os.getcwd()

def resolve_path(path: str) -> str:
    global CLI_CWD

    if not path or path in (".", "cwd"):
        return CLI_CWD

    path = path.strip()

    if os.path.isabs(path):
        return path

    home = os.path.expanduser("~")

    if path.lower() == "desktop":
        return os.path.join(home, "Desktop")

    if path.lower() == "documents":
        return os.path.join(home, "Documents")

    return os.path.abspath(os.path.join(CLI_CWD, path))
