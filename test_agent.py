import subprocess
import json


def test_agent_returns_valid_json():
    question = "What is 2+2? Answer in one word."

    # Запускаем агента как подпроцесс с помощью uv
    result = subprocess.run(
        ["uv", "run", "agent.py", question], capture_output=True, text=True
    )

    # Проверяем, что скрипт завершился с кодом 0 (успех)
    assert result.returncode == 0, f"Agent failed with error: {result.stderr}"

    # Получаем вывод из stdout
    output = result.stdout.strip()

    # Проверяем, что это валидный JSON
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON. Got: {output}"

    # Проверяем наличие обязательных полей
    assert "answer" in data, "Missing 'answer' field in JSON"
    assert "tool_calls" in data, "Missing 'tool_calls' field in JSON"

    # Проверяем, что tool_calls это пустой список (по условию Task 1)
    assert isinstance(data["tool_calls"], list), "'tool_calls' should be a list"
    assert len(data["tool_calls"]) == 0, "'tool_calls' must be empty for Task 1"
