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

    # Check that the source mentions the git-workflow wiki file
    assert "wiki/git-workflow.md" in data["source"]


def test_agent_lists_wiki_files():
    question = "What files are in the wiki directory?"
    data = run_agent(question)

    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0, "Agent did not use any tools"

    # Check if list_files was called
    tool_names = [call["tool"] for call in data["tool_calls"]]
    assert "list_files" in tool_names, "Agent did not use list_files tool"
