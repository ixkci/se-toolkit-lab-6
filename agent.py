import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).parent.resolve()


def secure_resolve(relative_path: str) -> Path | None:
    """Resolves path and ensures it stays within PROJECT_ROOT."""
    try:
        # Resolve the absolute path
        target = (PROJECT_ROOT / relative_path).resolve()
        # Check if it starts with the project root path
        if not str(target).startswith(str(PROJECT_ROOT)):
            return None
        return target
    except Exception:
        return None


def list_files(path: str) -> str:
    target = secure_resolve(path)
    if not target:
        return "Error: Access denied (path traversal detected)."
    if not target.exists():
        return f"Error: Path '{path}' does not exist."
    if not target.is_dir():
        return f"Error: Path '{path}' is not a directory."

    try:
        entries = [e.name for e in target.iterdir()]
        return "\n".join(entries) if entries else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {e}"


def read_file(path: str) -> str:
    target = secure_resolve(path)
    if not target:
        return "Error: Access denied (path traversal detected)."
    if not target.exists():
        return f"Error: File '{path}' does not exist."
    if not target.is_file():
        return f"Error: '{path}' is not a file."

    try:
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


# Tool definitions for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given relative path from project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path (e.g., 'wiki')",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path (e.g., 'wiki/git-workflow.md')",
                    }
                },
                "required": ["path"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a documentation agent. You answer questions by reading local files.
1. Use `list_files` to discover files in the 'wiki' directory.
2. Use `read_file` to read the relevant files.
3. Once you have the answer, output ONLY a JSON object with two string fields:
   - "answer": Your concise answer to the user's question.
   - "source": The relative file path and section anchor where you found the answer (e.g., "wiki/git-workflow.md#resolving-merge-conflicts").

Do NOT output anything except the final JSON object when you are done.
"""


def main():
    load_dotenv(".env.agent.secret")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "coder-model")

    if len(sys.argv) < 2:
        print("Error: No question provided.", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]
    client = OpenAI(api_key=api_key, base_url=base_url)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    executed_tools_history = []
    loop_count = 0
    max_loops = 10

    while loop_count < max_loops:
        loop_count += 1

        try:
            response = client.chat.completions.create(
                model=model, messages=messages, tools=TOOLS, tool_choice="auto"
            )
        except Exception as e:
            print(f"Agent API error: {e}", file=sys.stderr)
            sys.exit(1)

        message = response.choices[0].message
        messages.append(message)  # Append assistant's response to history

        # If LLM wants to call tools
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args_str = tool_call.function.arguments

                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}

                result_content = ""
                if func_name == "list_files":
                    result_content = list_files(args.get("path", ""))
                elif func_name == "read_file":
                    result_content = read_file(args.get("path", ""))
                else:
                    result_content = f"Error: Unknown tool {func_name}"

                # Append tool result to history
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_content,
                    }
                )

                # Record for final output
                executed_tools_history.append(
                    {"tool": func_name, "args": args, "result": result_content}
                )
        else:
            # LLM provided a final text response (should be JSON due to system prompt)
            content = message.content.strip()

            # Remove markdown JSON blocks if the LLM wrapped it
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
            content = content.strip()

            try:
                final_data = json.loads(content)
                # Ensure fields exist
                if "answer" not in final_data:
                    final_data["answer"] = "No answer generated."
                if "source" not in final_data:
                    final_data["source"] = "unknown"

                # Append the history of tool calls we executed
                final_data["tool_calls"] = executed_tools_history

                print(json.dumps(final_data))
                sys.exit(0)
            except json.JSONDecodeError:
                # Fallback if LLM failed to format as JSON
                fallback = {
                    "answer": content,
                    "source": "unknown",
                    "tool_calls": executed_tools_history,
                }
                print(json.dumps(fallback))
                sys.exit(0)

    # If max loops reached
    fallback = {
        "answer": "Error: Maximum tool calls reached.",
        "source": "none",
        "tool_calls": executed_tools_history,
    }
    print(json.dumps(fallback))
    sys.exit(0)


if __name__ == "__main__":
    main()
