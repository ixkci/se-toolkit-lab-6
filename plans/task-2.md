# Task 2 Implementation Plan

## Tool Schemas

1. **`list_files`**: Takes a relative `path`. Returns a newline-separated list of files/directories.
2. **`read_file`**: Takes a relative `path`. Returns the file content.

## Path Security

Both tools will use `os.path.abspath` to resolve paths relative to the project root. Before accessing the filesystem, the tool will verify that the resolved path starts with the absolute path of the project root. If it doesn't (e.g., due to `../` traversal attempts), it will return a security error string.

## Agentic Loop

1. Initialize conversation with a system prompt instructing the LLM to use `list_files` to explore the `wiki` directory and `read_file` to find answers, ending with a JSON containing `answer` and `source`.
2. Enter a `while` loop (max 10 iterations).
3. Send the conversation history and tool schemas to the LLM.
4. If the LLM returns `tool_calls`, execute each tool in Python, append the results as `tool` role messages, and continue the loop.
5. Record executed tools in a `tool_calls_history` array.
6. If the LLM returns a text response, parse it as JSON (extracting `answer` and `source`), combine it with `tool_calls_history`, print it to `stdout`, and exit.
