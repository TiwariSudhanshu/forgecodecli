"""Git operations for ForgeCodeCLI"""
import subprocess
import os

def run_git_command(cmd: str) -> str:
    """Execute a git command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode != 0:
            return f"❌ {result.stderr.strip()}"
        return f"✅ {result.stdout.strip()}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def git_init() -> str:
    """Initialize a new git repository"""
    return run_git_command("git init")

def git_add(path: str = ".") -> str:
    """Stage files for commit"""
    if path == ".":
        return run_git_command("git add .")
    return run_git_command(f'git add "{path}"')

def git_commit(message: str) -> str:
    """Commit staged changes"""
    if not message:
        return "❌ Commit message cannot be empty"
    return run_git_command(f'git commit -m "{message}"')

def git_push(branch: str = "main") -> str:
    """Push commits to remote repository"""
    return run_git_command(f"git push origin {branch}")

def git_set_origin(url: str) -> str:
    """Set remote repository URL"""
    if not url:
        return "❌ Repository URL cannot be empty"
    return run_git_command(f'git remote add origin "{url}"')

def git_status() -> str:
    """Show git status"""
    return run_git_command("git status")

def git_log(lines: int = 5) -> str:
    """Show commit history"""
    return run_git_command(f"git log --oneline -n {lines}")

def git_branch(name: str = None) -> str:
    """List branches or create new branch"""
    if name:
        return run_git_command(f"git checkout -b {name}")
    return run_git_command("git branch -a")

def git_pull() -> str:
    """Pull changes from remote"""
    return run_git_command("git pull origin main")

def git_clone(url: str, path: str = ".") -> str:
    """Clone a repository"""
    if not url:
        return "❌ Repository URL cannot be empty"
    return run_git_command(f'git clone "{url}" "{path}"')
