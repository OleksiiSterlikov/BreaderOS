# DEVELOPMENT.md

## Локальна розробка

### Підготовка середовища

```bash
git clone <repo>
cd BreaderOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Проєкт розрахований на запуск через `python3` або інтерпретатор з `.venv`.

---

## Локальний запуск

```bash
source .venv/bin/activate
python app.py
```

Застосунок буде доступний на:

```text
http://127.0.0.1:5000
```

Рекомендований стабільний запуск:

```bash
source .venv/bin/activate
APP_DEBUG=0 APP_USE_RELOADER=0 APP_USE_DEBUGGER=0 python app.py
```

Підтримувані env-параметри локального запуску:

```bash
APP_HOST=127.0.0.1
APP_PORT=5000
APP_DEBUG=0
APP_USE_RELOADER=0
APP_USE_DEBUGGER=0
```

`app.py` тепер містить `create_app()`, який можна використовувати для:

- тестів
- WSGI runtime
- майбутнього винесення конфігурації запуску в окремі профілі

---

## Docker-запуск

```bash
docker compose build
docker compose up -d
```

При запуску через compose зовнішня адреса:

```text
http://127.0.0.1
```

---

## Структура коду

- `app.py` - `create_app()`, реєстрація blueprint і локальний dev entrypoint
- `routes/main.py` - HTTP endpoints
- `services/fswalker.py` - робота з файловою системою книг
- `templates/` - Jinja templates
- `static/css/` - стилі
- `static/js/` - клієнтська логіка дерева і viewer
- `static/books/` - книги у форматі HTML
- `tests/` - базові автоматизовані тести

---

## Frontend

Поточна UI-модель:

- sidebar з деревом книг
- `iframe` для перегляду HTML-сторінок
- lazy loading вкладених папок через `/api/folder`
- кнопки `A-` і `A+` для зміни розміру тексту
- перемикач світлої/темної теми

---

## Маршрути

- `/` - головна сторінка з деревом книг
- `/api/folder?path=...` - повертає вміст папки всередині `static/books`
- `/book/<path>` - безпечна віддача файлу книги

Для `/api/folder` і `/book/<path>` діє обмеження доступу лише в межах каталогу книг.

---

## Тестування

Запуск тестів:

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Поточний набір перевіряє:

- відкриття головної сторінки
- коректну роботу `/api/folder`
- блокування path traversal
- віддачу HTML-книги через `/book/<path>`

---

## Debugging

Поточний локальний запуск використовує:

- керовані env-параметри для `debug`, `reloader` і `debugger`

Для налагодження достатньо:

- Flask traceback
- локальних перевірок через test client
- помірного логування без виводу великих списків у консоль

Для стабільної роботи в обмежених середовищах варто тримати:

- `APP_DEBUG=0`
- `APP_USE_RELOADER=0`
- `APP_USE_DEBUGGER=0`

---

## Code style

- Python: PEP 8
- JavaScript: простий Vanilla JS без framework-specific tooling
- Документація в `docs/ai/` повинна оновлюватися разом із поведінковими змінами
