# Task 3 Implementation Plan

## New Tool: `query_api`

1. **Schema**: Accepts `method` (GET, POST), `path` (e.g., `/items/`), and an optional `body` (JSON string).
2. **Execution**: Uses the `requests` library to make HTTP calls to the backend.
3. **Authentication**: Injects the `LMS_API_KEY` (from `.env.docker.secret`) into the `Authorization: Bearer <key>` header.
4. **Endpoint**: Uses `AGENT_API_BASE_URL` from environment variables, defaulting to `http://localhost:42002`.

## System Prompt Update

The prompt will explicitly guide the LLM on tool selection:

- Use `list_files` / `read_file` for static questions (frameworks, source code logic, wiki).
- Use `query_api` for dynamic questions (database counts, live API errors, status codes).

## Benchmark Strategy

- Initial run will likely fail on complex reasoning questions.
- We will iterate by adjusting the system prompt and ensuring the LLM handles `None` content correctly during tool calls to prevent crashes.
- Initial evaluation score: TBD (will run `run_eval.py` after implementing the tool).
