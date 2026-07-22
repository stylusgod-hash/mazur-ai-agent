"""
Персональний ІІ-агент на базі Gemini + Google ADK.
Має доступ до: файлової системи, shell, браузера (Playwright), Google Search.
"""

import subprocess
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


# ---------- Інструмент: робота з файлами ----------

def read_file(path: str) -> str:
    """Читає та повертає текстовий вміст файлу за вказаним шляхом.

    Args:
        path: шлях до файлу (відносний або абсолютний).
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Помилка читання файлу: {e}"


def write_file(path: str, content: str) -> str:
    """Записує (або перезаписує) текстовий вміст у файл за вказаним шляхом.

    Args:
        path: шлях до файлу, куди зберегти вміст.
        content: текст, який потрібно записати.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Успішно записано {len(content)} символів у {path}"
    except Exception as e:
        return f"Помилка запису файлу: {e}"


def list_files(directory: str = ".") -> str:
    """Показує список файлів та папок у вказаній директорії.

    Args:
        directory: шлях до директорії (за замовчуванням поточна).
    """
    try:
        import os
        items = os.listdir(directory)
        return "\n".join(items) if items else "Директорія порожня."
    except Exception as e:
        return f"Помилка: {e}"


# ---------- Інструмент: виконання команд ----------

def run_shell(command: str) -> str:
    """Виконує shell-команду в терміналі Codespace і повертає результат.
    Використовуй обережно — команда виконується з правами поточного користувача.

    Args:
        command: shell-команда для виконання.
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr
        return output[:4000] if output else "Команда виконана без виводу."
    except subprocess.TimeoutExpired:
        return "Команда перевищила ліміт часу (60с)."
    except Exception as e:
        return f"Помилка виконання: {e}"


# ---------- Інструмент: браузер (Playwright) ----------

def browse(url: str) -> str:
    """Відкриває сторінку в браузері та повертає її текстовий вміст.

    Args:
        url: повна URL-адреса сторінки (з http:// або https://).
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=15000)
            text = page.inner_text("body")
            browser.close()
            return text[:5000]
    except Exception as e:
        return f"Помилка при відкритті сторінки: {e}"


# ---------- Під-агент для пошуку ----------
# У ADK вбудований google_search не можна поєднувати з власними function tools
# в межах одного агента, тому пошук виконує окремий під-агент, а головний
# агент викликає його як звичайний інструмент.

search_agent = Agent(
    name="search_agent",
    model="gemini-flash-latest",
    instruction="Виконуй пошук в Google за запитом користувача та повертай стислий результат з джерелами.",
    tools=[google_search],
)


# ---------- Головний агент ----------

root_agent = Agent(
    name="personal_assistant",
    model="gemini-flash-latest",
    instruction="""Ти персональний ІІ-агент користувача, що працює автономно
    в GitHub Codespaces.

    У тебе є доступ до:
    - файлової системи (read_file, write_file, list_files)
    - shell-команд (run_shell)
    - браузера для відкриття веб-сторінок (browse)
    - пошуку в інтернеті (search_agent)

    Правила роботи:
    1. Якщо задача складна — розбий її на кроки і виконуй послідовно.
    2. Перед виконанням дій, що змінюють файли або систему, коротко поясни план.
    3. Звітуй про результат кожного кроку.
    4. Якщо чогось не вистачає (даних, доступу) — повідом про це чітко.
    5. Відповідай українською мовою, якщо користувач не просить іншого.
    """,
    tools=[
        AgentTool(agent=search_agent),
        read_file,
        write_file,
        list_files,
        run_shell,
        browse,
    ],
)
