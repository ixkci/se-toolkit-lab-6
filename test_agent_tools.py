import subprocess
import json


def run_agent(question: str) -> dict:
    result = subprocess.run(
        ["uv", "run", "agent.py", question], capture_output=True, text=True
    )
    assert result.returncode == 0, f"Agent failed: {result.stderr}"

    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON. Got: {result.stdout}"


def test_agent_resolves_merge_conflict():
    question = "How do you resolve a merge conflict? Look in the wiki."
    data = run_agent(question)

    assert "answer" in data
    assert "source" in data
    assert "tool_calls" in data

    # Check that tool_calls were actually used
    assert len(data["tool_calls"]) > 0, "Agent did not use any tools"

    # Check if read_file was called
    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "read_file" in tool_names, "Agent did not use read_file tool"

    # Check that the source mentions a git-related wiki file
    source = data["source"]
    assert "wiki/git" in source, f"Source should reference git wiki file, got: {source}"


def test_agent_lists_wiki_files():
    question = "What files are in the wiki directory?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0, "Agent did not use any tools"

    # Check if list_files was called
    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "list_files" in tool_names, "Agent did not use list_files tool"


def test_agent_checks_backend_framework():
    question = "What Python web framework does the backend use?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "read_file" in tool_names, (
        "Agent should read source files to find the framework"
    )


def test_agent_queries_api_for_items():
    question = "How many items are currently stored in the database?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "query_api" in tool_names, "Agent should use query_api to get database count"


def test_agent_checks_unauthenticated_status():
    """Test that agent uses query_api with skip_auth to check status codes."""
    question = "What HTTP status code does the API return when you request /items/ without authentication?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "query_api" in tool_names, "Agent should use query_api to check status code"

    # Check that 401 or 403 is mentioned in the answer
    answer = data.get("answer", "").lower()
    assert "401" in answer or "403" in answer, (
        f"Answer should mention 401 or 403 status code, got: {data.get('answer')}"
    )


def test_agent_diagnoses_analytics_bug():
    """Test that agent diagnoses the ZeroDivisionError in completion-rate endpoint."""
    question = "Query GET /analytics/completion-rate?lab=lab-99. What error do you get?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "query_api" in tool_names, "Agent should use query_api to check the endpoint"

    # Check that division by zero is mentioned in the answer
    answer = data.get("answer", "").lower()
    assert "division" in answer or "zero" in answer, (
        f"Answer should mention division by zero error, got: {data.get('answer')}"
    )
