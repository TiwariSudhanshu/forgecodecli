from pathlib import Path
import os
import shutil
from forgecodecli.path_resolver import resolve_path


_undo_stack = []

class FileOperation:
    """Represent a reversible file operation"""
    def __init__(self, op_type: str, src: str, dst: str = None, content: str = None):
        self.op_type = op_type  # 'write', 'delete', 'move', 'mkdir', 'rmdir'
        self.src = src
        self.dst = dst
        self.content = content  # For write operations
    def undo(self):
        """Reverse the operation"""
        if self.op_type == "write":
            os.remove(self.src)
        elif self.op_type == "delete":
            with open(self.src, "w", encoding="utf-8") as f:
                f.write(self.content)
        elif self.op_type == "move":
            os.rename(self.dst, self.src)
        elif self.op_type == "mkdir":
            os.rmdir(self.src)
        elif self.op_type == "rmdir":
            os.makedirs(self.src, exist_ok=True)
            
            
def is_safe_path(path: str) -> bool:
    """Check if path is safe (no absolute paths, no parent directory traversal)"""
    if not path:
        return False
    if os.path.isabs(path):
        return False
    if ".." in path:
        return False
    return True


def read_file(path: str) -> str:
    """Read a file and return its contents"""
    full_path = resolve_path(path)
    file_path = Path(full_path)
 
    if not file_path.exists():
        return f"Error: File '{path}' does not exist."
 
    return file_path.read_text()


def list_files(path: str = ".") -> str:
    full_path = resolve_path(path)
    
    if not os.path.exists(full_path):
        return "❌ Path does not exist."

    if not os.path.isdir(full_path):
        return "❌ Path is not a directory."
    
    try:
        items = os.listdir(full_path)
        if not items:
            return "📂 Directory is empty."
        
        return "\n".join(sorted(items))
    except Exception as e:
        return f"❌ Error reading directory: {str(e)}"

    
def write_file(path: str, content: str) -> str:
    full_path = resolve_path(path)

    # Prevent overwriting existing files (for now)
    if os.path.exists(full_path):
        return "❌ File already exists. Overwrite not allowed."

    parent = os.path.dirname(full_path)
    if parent and not os.path.exists(parent):
        return "❌ Parent directory does not exist."

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        _undo_stack.append(FileOperation("write", full_path))

        return f"✅ File written: {path}"
    except Exception:
        return "❌ Failed to write file."

def create_dir(path: str) -> str:
    full_path = resolve_path(path)
    if os.path.exists(full_path):
        return f"❌ Directory already exists: {path}"
    try:
        os.makedirs(full_path, exist_ok=True)
        _undo_stack.append(FileOperation("mkdir", full_path))
        return f"✅ Directory created: {path}"
    except Exception as e:
        return f"❌ Failed to create directory: {str(e)}"
    
def delete_file(path: str) -> str:
    full_path = resolve_path(path)
    if not os.path.exists(full_path):
        return f"❌ File '{path}' does not exist."
    if os.path.isdir(full_path):
        return f"❌ '{path}' is a directory, not a file."
    try:
        content = Path(full_path).read_text()
        os.remove(full_path)
        _undo_stack.append(FileOperation("delete", full_path, content=content))
        return f"✅ File deleted: {path}"
    except Exception as e:
        return f"❌ Failed to delete file: {str(e)}"
    
def delete_dir(path: str) -> str:
    full_path = resolve_path(path)
    if not os.path.exists(full_path):
        return f"❌ Directory '{path}' does not exist."
    if not os.path.isdir(full_path):
        return f"❌ '{path}' is not a directory."
    try:
        shutil.rmtree(full_path)
        _undo_stack.append(FileOperation("rmdir", full_path))
        return f"✅ Directory deleted: {path}"
    except Exception as e:
        return f"❌ Failed to delete directory: {str(e)}"
    
def move_file(src: str, dst: str) -> str:
    full_src = resolve_path(src)
    full_dst = resolve_path(dst)

    if not os.path.exists(full_src):
        return f"❌ Source file '{src}' does not exist."
    if os.path.isdir(full_src):
        return f"❌ Source '{src}' is a directory, not a file."
    
    dst_parent = os.path.dirname(full_dst)
    if dst_parent and not os.path.exists(dst_parent):
        return f"❌ Destination parent directory does not exist."

    try:
        os.rename(full_src, full_dst)
        _undo_stack.append(FileOperation("move", full_src, full_dst))
        return f"✅ File moved from '{src}' to '{dst}'"
    except Exception as e:
        return f"❌ Failed to move file: {str(e)}"
    
def move_dir(src: str, dst: str) -> str:
    full_src = resolve_path(src)
    full_dst = resolve_path(dst)

    if not os.path.exists(full_src):
        return f"❌ Source directory '{src}' does not exist."
    if not os.path.isdir(full_src):
        return f"❌ Source '{src}' is not a directory."
    
    dst_parent = os.path.dirname(full_dst)
    if dst_parent and not os.path.exists(dst_parent):
        return f"❌ Destination parent directory does not exist."

    try:
        os.rename(full_src, full_dst)
        _undo_stack.append(FileOperation("move", full_src, full_dst))
        return f"✅ Directory moved from '{src}' to '{dst}'"
    except Exception as e:
        return f"❌ Failed to move directory: {str(e)}"
    
def undo() -> str:
    """Undo the last file operation"""
    if not _undo_stack:
        return "⚠️ Nothing to undo."
    
    try:
        operation = _undo_stack.pop()
        operation.undo()
        return f"✅ Undid {operation.op_type} operation"
    except Exception as e:
        return f"❌ Failed to undo: {str(e)}"