# Agent Documentation (Task 1)

## Architecture

This is a basic CLI agent built in Python. It takes a single string query from the command line, sends it to an LLM, and prints the result to standard output in a strict JSON format.

All diagnostic messages, errors, and logs are directed to `stderr` to ensure that `stdout` only ever contains parsable JSON.

## LLM Configuration

- **Provider:** Qwen Code API (hosted on remote VM)
- **Model:** `coder-model`
- **Authentication:** The agent reads `LLM_API_KEY`, `LLM_API_BASE`, and `LLM_MODEL` from the `.env.agent.secret` file.

## Usage

Run the agent using `uv`:

```bash
uv run agent.py "What does REST stand for?"
