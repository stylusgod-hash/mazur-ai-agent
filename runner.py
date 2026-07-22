"""
Запуск агента з командного рядка з постійною пам'яттю (SQLite),
яка зберігається між перезапусками Codespace.

Використання:
    python runner.py
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from personal_assistant.agent import root_agent

APP_NAME = "mazur_ai_agent"
USER_ID = "user_1"
DB_URL = "sqlite:///./agent_memory.db"


async def main():
    session_service = DatabaseSessionService(db_url=DB_URL)

    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("Персональний агент готовий. Введи задачу (або 'exit' для виходу).\n")

    while True:
        user_input = input("Ти: ").strip()
        if user_input.lower() in ("exit", "quit", "вихід"):
            break
        if not user_input:
            continue

        content = types.Content(role="user", parts=[types.Part(text=user_input)])

        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\nАгент: {part.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
