# middleware.py (replace relevant parts)

import sys, os, json, re
sys.path.append(os.path.dirname(__file__))
import main as tools
import ollama
import time

def _extract_first_json_object(text: str):
    """Return the first balanced JSON object parsed from text, or None."""
    if not isinstance(text, str):
        return None
    start = text.find('{')
    if start == -1:
        return None
    stack = []
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '{':
            stack.append('{')
        elif ch == '}':
            if not stack:
                # unmatched brace; continue searching
                continue
            stack.pop()
            if not stack:
                candidate = text[start:i+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None

def run_with_ollama(user_prompt: str, history=None, round_count=0, max_rounds=10, last_tool_call=None):
    if history is None:
        history = []

    if round_count >= max_rounds:
        return "Max tool-call rounds reached. Stopping to prevent infinite loop."

    system_msg = {
        "role": "system",
        "content": (
            "You are a strict tool-using coding assistant.\n"
            "You MUST call tools to read or write files. Do not fabricate file contents.\n\n"
            "Available tools:\n"
            "1. read_code(file_path: str) -> str\n"
            "2. write_code(file_path: str, content: str) -> str\n\n"
            "CALL FORMAT (exact JSON, no extra text, no code fences). Examples (DO NOT USE PLACEHOLDERS LITERALLY):\n"
            "{\"tool\":\"read_code\",\"args\":{\"file_path\":\"some/real/path.txt\"}}\n"
            "{\"tool\":\"write_code\",\"args\":{\"file_path\":\"some/real/path.txt\",\"content\":\"NEW_CONTENT\"}}\n\n"
            "RULES:\n"
            "- If asked to analyze or modify a file, first call read_code.\n"
            "- If changing a file, call write_code with the full updated content.\n"
            "- Return ONLY a single JSON object when calling a tool.\n"
            "- Do not wrap JSON in markdown.\n"
            "- After tool results are returned, produce a concise final answer.\n"
        ),
    }

    messages = [system_msg, *history]
    if round_count == 0:
        messages.append({"role": "user", "content": user_prompt})

    response = ollama.chat(model="llama3", messages=messages)
    content = response["message"]["content"]

    # robustly extract a single JSON tool call
    tool_req = _extract_first_json_object(content)

    # heuristic fallback: handle patterns like read_code("path")
    if not tool_req and isinstance(content, str):
        m = re.search(r"read_code\(\s*['\"]([^'\"]+)['\"]\s*\)", content)
        if m:
            tool_req = {"tool": "read_code", "args": {"file_path": m.group(1)}}

    if tool_req:
        tool_name = tool_req.get("tool")
        args = tool_req.get("args", {})

        # detect exact repeat to avoid loops
        current_call = (tool_name, tuple(sorted(args.items())))
        if current_call == last_tool_call:
            return "Detected repeated identical tool call. Aborting to avoid loop."

        # default file_path if missing
        args.setdefault("file_path", "main1.py")

        # avoid executing placeholder/example paths
        if args.get("file_path") in {"RELATIVE_OR_ABSOLUTE_PATH", "PATH", "some/real/path.txt"}:
            print("[Skipping placeholder tool call]", tool_req)
            tool_req = None

        if tool_req and tool_name == "read_code":
            result = tools.read_code(**args)
        elif tool_req and tool_name == "write_code":
            result = tools.write_code(**args)
        elif tool_req:
            result = f"Unknown tool {tool_name}"
        else:
            result = None

        # diagnostics: show path and length (helps detect truncation)
        try:
            length = len(result) if isinstance(result, str) else "N/A"
        except Exception:
            length = "N/A"
        print(f"[Tool executed: {tool_name}] path={args.get('file_path')} len={length}")

        # append tool response to history and continue
        if result is not None:
            history.append({"role": "tool", "content": result})
            return run_with_ollama(user_prompt, history, round_count + 1, max_rounds, last_tool_call=current_call)

    # not a tool call → log and return final assistant response
    print("[Assistant content (no tool call detected)]", content)
    return content


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]).strip() or "Read main.py and summarize what tools are available."
    result = run_with_ollama(user_prompt)
    print("\n=== Final Response from Ollama ===\n")
    print(result)
