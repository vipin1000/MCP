
from mcp.server.fastmcp import FastMCP
import os
import tempfile
import threading
# Create MCP server
mcp = FastMCP("Demo")


_base_dir = os.path.dirname(__file__)
_file_lock = threading.Lock()

@mcp.tool()
def read_code(file_path: str) -> str:
    """
    Read the entire file at file_path (relative to this module).
    Logs only metadata, returns full content.
    """
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    if not os.path.exists(abs_path):
        return f"File not found: {abs_path}"

    with _file_lock:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

    # Log only metadata
    print(f"[read_code] path={abs_path} len={len(content)} chars")
    return content or ""


@mcp.tool()
def write_code(file_path: str, content: str) -> str:
    """
    Atomically write content to file_path using a temp file + os.replace.
    Logs only metadata, returns success message.
    """
    abs_path = file_path if os.path.isabs(file_path) else os.path.join(_base_dir, file_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with _file_lock:
        fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(abs_path), prefix=".tmp_", text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                tmpf.write(content)
            os.replace(tmp_path, abs_path)  # atomic replace
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # Log only metadata
    print(f"[write_code] path={abs_path} len={len(content)} chars")
    return f"File written successfully: {abs_path}"
