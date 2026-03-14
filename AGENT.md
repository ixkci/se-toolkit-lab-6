# Agent Documentation

## Architecture & Agentic Loop

The agent implements an iterative loop to answer questions by exploring the local filesystem.

1. It sends the user's question and a system prompt to the LLM, along with available tool definitions.
2. If the LLM requests a tool call, the agent pauses, executes the corresponding Python function, and appends the result to the conversation history as a `tool` role message.
3. This loop continues until the LLM stops calling tools and provides a final answer, or until the safety limit of 10 tool calls is reached.
4. The final answer is parsed as JSON, combined with the history of all executed tool calls, and output to `stdout`.

## Tools

1. **`list_files`**: Lists contents of a directory. Used by the LLM to discover what files exist (e.g., in the `wiki` folder).
2. **`read_file`**: Reads the text content of a file. Used by the LLM to extract information.

## Security

Path traversal (e.g., `../../etc/passwd`) is prevented using Python's `pathlib`. All tool paths are resolved to absolute paths and verified to ensure they start with the absolute path of the project's root directory. Any attempt to access files outside the project results in an "Access denied" error being returned to the LLM.
