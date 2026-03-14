# Task 3 Implementation Plan

## New Tool: `query_api`

1. **Schema**: Accepts `method` (GET, POST), `path` (e.g., `/items/`), `body` (optional JSON string), and `skip_auth` (optional boolean to omit Authorization header).
2. **Execution**: Uses the `requests` library to make HTTP calls to the backend.
3. **Authentication**: Injects the `LMS_API_KEY` (from `.env.docker.secret`) into the `Authorization: Bearer <key>` header. Use `skip_auth=true` to test unauthenticated requests.
4. **Endpoint**: Uses `AGENT_API_BASE_URL` from environment variables, defaulting to `http://localhost:42002`.

## System Prompt Update

The prompt explicitly guides the LLM on tool selection:

- Use `list_files` / `read_file` for static questions (frameworks, source code logic, wiki).
- Use `query_api` for dynamic questions (database counts, live API errors, status codes).
- For analytics endpoints, try multiple lab values (e.g., lab-01, lab-99) to reproduce errors.
- If you get an API error (500, TypeError, ZeroDivisionError), read the source code file mentioned in the traceback.

## Benchmark Results

### Initial Failures

1. **Question 3 (Framework)**: Agent used only `list_files`, not `read_file`. Fixed by updating prompt to explicitly say "read backend/app/main.py for framework questions".
2. **Question 6 (Status code without auth)**: Agent always sent auth header. Added `skip_auth` parameter to `query_api` tool.
3. **Question 7 (ZeroDivisionError)**: Agent found error but didn't read source file. Added prompt rule to read source on API errors.
4. **Question 8 (TypeError in top-learners)**: Agent didn't reproduce error. Added prompt to try multiple lab values for analytics endpoints.

### Iteration Strategy

- Run `run_eval.py` after each change
- Fix one failure at a time, starting with tool usage issues
- Use debug output (`print(..., file=sys.stderr)`) to trace tool calls

### Final Score

**10/10 PASSED** - All local benchmark questions pass.
