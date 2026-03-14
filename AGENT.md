# Agent Documentation

## Architecture & Agentic Loop

The agent acts as a fully autonomous system diagnostic tool. It uses an iterative LLM loop to process the user's question, decide which tools to use, and gather context. The LLM evaluates the results of its tool calls and can choose to chain them (for example, hitting an API endpoint, receiving a 500 Internal Server Error, and subsequently reading the backend source code to diagnose the stack trace). The loop runs up to 10 times to prevent infinite execution.

## Available Tools

1. **`list_files(path)`**: Navigates the local project structure. Crucial for discovering module names and project layouts.
2. **`read_file(path)`**: Reads the contents of source code, Dockerfiles, or wiki documentation. Path traversal is prevented securely using Python's `pathlib.Path.resolve()`.
3. **`query_api(method, path, body, skip_auth)`**: Sends live HTTP requests to the deployed backend. It returns both the HTTP status code and the response body. The `skip_auth` parameter (default `False`) allows testing unauthenticated endpoints by omitting the Authorization header.

## Configuration and Authentication

The agent dynamically configures itself using environment variables:

- **LLM Configuration**: Reads `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL` from `.env.agent.secret` to authenticate with the Qwen Code model.
- **Backend Authentication**: Reads `LMS_API_KEY` from `.env.docker.secret` and injects it as a `Bearer` token in the `Authorization` header for all `query_api` requests (unless `skip_auth=true`).
- **API Routing**: Uses `AGENT_API_BASE_URL` to know where the backend is hosted (defaulting to `http://localhost:42002`).

## Tool Selection & System Prompt Logic

The system prompt explicitly instructs the LLM on tool taxonomy:

- **Wiki questions** → `list_files` with `path="wiki"`, then `read_file` on relevant files.
- **Source code questions** (frameworks, routers, logic) → `read_file` on specific files (e.g., `backend/app/main.py` for framework).
- **API/data questions** (counts, status codes, errors) → `query_api` for live data.
- **Unauthenticated status codes** → `query_api` with `skip_auth=true`.
- **Analytics errors** → Try multiple lab values (lab-01, lab-99) to reproduce errors, then read `backend/app/routers/analytics.py`.
- **API error responses** (500, TypeError, ZeroDivisionError) → Read the source file mentioned in the traceback.

## The `query_api` Tool

### Purpose

Enables the agent to query the deployed backend API for live data such as database counts, endpoint status codes, and error responses.

### Parameters

- `method` (required): HTTP method (GET, POST, etc.)
- `path` (required): Endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (optional): JSON request body for POST/PUT requests
- `skip_auth` (optional): Set to `true` to omit the Authorization header (for testing unauthenticated access)

### Returns

JSON string with `status_code` and `body` fields.

### Authentication

Automatically includes `Authorization: Bearer <LMS_API_KEY>` header unless `skip_auth=true`.

## Lessons Learned & Debugging

### Key Issues Fixed

1. **`AttributeError: 'NoneType'` crashes**: When the LLM makes tool calls, `message.content` is often `None`. Fixed by using `(message.content or "")` instead of `msg.get("content", "")`.

2. **Tool parameter not passed**: The `skip_auth` parameter was defined in the schema but not passed to the actual function call. Fixed by adding `args.get("skip_auth", False)` to the tool invocation.

3. **Agent doesn't read source on errors**: Initially, the agent would find API errors but not read the source code. Added explicit prompt rule: "If you get an API error (500, TypeError, ZeroDivisionError), read the source code file mentioned in the traceback."

4. **Analytics errors not reproduced**: The top-learners endpoint only crashes for specific labs with data. Added prompt guidance to try multiple lab values.

5. **JSON schema boolean issue**: Initially used `"default": false` in the JSON schema, which caused a Python `NameError`. Removed the default and handle it in code instead.

### Debugging Tips

- Use `print(..., file=sys.stderr)` for debug output (doesn't pollute stdout JSON)
- Run single questions with `uv run run_eval.py --index N`
- Check tool call arguments in stderr logs

## Final Evaluation Score

**10/10 PASSED** on local benchmark questions.

The agent successfully handles:

- Wiki lookups (git workflow, SSH connection)
- Source code analysis (FastAPI framework, router modules)
- Live API queries (item counts, status codes)
- Bug diagnosis (ZeroDivisionError, TypeError in analytics)
- Complex reasoning (request lifecycle, ETL idempotency)
