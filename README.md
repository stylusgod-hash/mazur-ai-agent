# Персональний ІІ-агент (Gemini + Google ADK)

Автономний агент з пам'яттю, доступом до файлів, shell, браузера та пошуку.
Працює повністю в GitHub Codespaces, без локального ПК.

## Структура проєкту

```
mazur-ai-agent/
├── .devcontainer/
│   └── devcontainer.json      # автоналаштування Codespace
├── personal_assistant/
│   ├── __init__.py
│   └── agent.py                # логіка агента та інструменти
├── runner.py                    # CLI-запуск з пам'яттю (SQLite)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Встановлення (у GitHub Codespaces)

1. Заклади всі ці файли в корінь свого репозиторію (структуру зберігай як є).
2. Якщо Codespace вже запущений — перевстанови залежності вручну:

```bash
pip install -r requirements.txt
playwright install chromium --with-deps
```

Якщо Codespace ще не створений — GitHub сам виконає це через `.devcontainer/devcontainer.json` при старті.

3. Ключ `GOOGLE_API_KEY` додай як **Codespaces Secret** (Settings → Codespaces → Secrets на GitHub.com) — так, як ти вже зробив раніше. Це найбезпечніший спосіб.

   Альтернатива: скопіюй `.env.example` у `.env` і встав ключ туди (файл вже в `.gitignore`, у git не потрапить).

## Запуск

### Варіант A — Веб-інтерфейс ADK (рекомендовано для старту)

```bash
adk web
```

Відкриється Dev UI. У Codespaces перейди на вкладку **Ports** внизу, знайди порт 8000 і натисни **Open in Browser**. Обери агента `personal_assistant` зі списку зліва.

### Варіант B — Командний рядок з постійною пам'яттю

```bash
python runner.py
```

Історія розмов зберігається у файлі `agent_memory.db` (SQLite) і залишається доступною навіть після перезапуску Codespace.

## Що вміє агент

| Інструмент | Що робить |
|---|---|
| `read_file` / `write_file` / `list_files` | Читає, створює, редагує файли в проєкті |
| `run_shell` | Виконує будь-яку shell-команду в Codespace |
| `browse` | Відкриває сторінку в браузері (Playwright) і читає вміст |
| `search_agent` | Шукає інформацію в інтернеті через Google Search |

## Розширення

- **Додати нові інструменти**: просто напиши Python-функцію з docstring (опис для моделі) і додай її в список `tools=[...]` у `personal_assistant/agent.py`.
- **Автономні багатокрокові задачі**: для складних workflow можна використати `SequentialAgent` або `LoopAgent` з `google.adk.agents` замість звичайного `Agent`.
- **Telegram-бот / API назовні**: обгорни `runner.py`-логіку у FastAPI + `python-telegram-bot`, щоб отримати доступ з телефону.
- **24/7 робота**: безкоштовний Codespace засинає при простої. Для постійної роботи задеплой той самий код на Cloud Run (є безкоштовний ліміт) або Google Agent Engine.

## Ліміти безкоштовного тарифу

- **Gemini API**: обмежена кількість запитів на хвилину/добу (дивись актуальні ліміти на aistudio.google.com).
- **GitHub Codespaces**: ~60–120 годин/міс безкоштовно залежно від типу акаунту, засинає після простою.
