# Task 1 Implementation Plan

## LLM Provider & Model

- **Provider:** Qwen Code API (Remote VM)
- **Model:** `coder-model`

## Architecture

1. **Input:** The agent will read the user's question from `sys.argv[1]`.
2. **Environment:** Credentials (`LLM_API_KEY`, `LLM_API_BASE`, `LLM_MODEL`) will be loaded from `.env.agent.secret` using the `python-dotenv` library.
3. **LLM Integration:** The official `openai` Python SDK will be used to make OpenAI-compatible chat completion requests to the Qwen API.
4. **Output:** The raw answer will be wrapped in a dictionary `{"answer": "...", "tool_calls": []}` and printed to `stdout` using `json.dumps()`.
5. **Logging/Errors:** All debug information and errors will be routed to `stderr` to keep `stdout` strictly as valid JSON.
