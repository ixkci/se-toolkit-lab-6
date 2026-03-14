import sys
import json
import os
from dotenv import load_dotenv
from openai import OpenAI


def main():
    # Загружаем переменные из .env.agent.secret
    load_dotenv(".env.agent.secret")

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("LLM_MODEL", "coder-model")

    # Проверяем, передан ли аргумент с вопросом
    if len(sys.argv) < 2:
        print(
            "Error: No question provided. Usage: uv run agent.py <question>",
            file=sys.stderr,
        )
        sys.exit(1)

    question = sys.argv[1]

    try:
        # Инициализируем клиент OpenAI с кастомным URL
        client = OpenAI(api_key=api_key, base_url=base_url)

        # Отправляем запрос к LLM
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer concisely.",
                },
                {"role": "user", "content": question},
            ],
        )

        answer_content = response.choices[0].message.content

        # Формируем итоговый JSON по требованиям задания
        result = {"answer": answer_content, "tool_calls": []}

        # Выводим ТОЛЬКО валидный JSON в stdout
        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        # Все ошибки отправляем в stderr, чтобы не сломать парсинг вывода
        print(f"Agent error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
